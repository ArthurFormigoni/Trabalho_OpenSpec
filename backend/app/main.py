from contextlib import asynccontextmanager
from hashlib import sha256

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status, Query, WebSocket, BackgroundTasks
from starlette.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .config import get_settings
from .db import engine, get_db
from .image_processing import ImageEncodingError, ImageValidationError, process_image
from .models import StoredImage, ImageComment
from .schemas import ImageResponse, CommentInput, CommentResponse
from .migrations import migrate
from .realtime import Realtime

settings = get_settings()
realtime = Realtime(settings)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await run_in_threadpool(migrate, engine)
    await realtime.start()
    try:
        yield
    finally:
        await realtime.stop()


app = FastAPI(title="Photo Gallery API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


def to_response(image: StoredImage) -> ImageResponse:
    return ImageResponse(
        id=image.id,
        size_x=image.size_x,
        size_y=image.size_y,
        filesize_bytes=image.filesize_bytes,
        image_url=f"/images/{image.id}/content?v={sha256(image.image_bytes).hexdigest()[:16]}",
        likes_count=image.likes_count,
        comments_count=image.comments_count,
        revision=image.revision,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/images", response_model=list[ImageResponse])
def list_images(db: Session = Depends(get_db)) -> list[ImageResponse]:
    images = db.scalars(select(StoredImage).order_by(StoredImage.id)).all()
    return [to_response(image) for image in images]


@app.get("/images/{image_id}/content")
def get_image_content(image_id: int, db: Session = Depends(get_db)) -> Response:
    image = db.get(StoredImage, image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Imagem não encontrada")
    return Response(
        content=image.image_bytes,
        media_type="image/avif",
        headers={"Cache-Control": "no-store, max-age=0", "Pragma": "no-cache"},
    )


@app.post("/images", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
def create_image(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(get_db)) -> ImageResponse:
    source = file.file.read(settings.max_upload_bytes + 1)
    if not source:
        raise HTTPException(status_code=400, detail="O arquivo enviado está vazio")
    if len(source) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="O arquivo enviado excede o limite operacional")
    try:
        width, height, encoded = process_image(source)
    except ImageValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ImageEncodingError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    stored = StoredImage(size_x=width, size_y=height, filesize_bytes=len(encoded), image_bytes=encoded)
    db.add(stored)
    db.commit()
    db.refresh(stored)
    result = to_response(stored)
    background_tasks.add_task(realtime.publish, "image.created", stored.id, result.model_dump())
    return result


@app.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(image_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> None:
    image = db.scalar(select(StoredImage).where(StoredImage.id == image_id).with_for_update())
    if image is None:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    db.delete(image)
    db.commit()
    background_tasks.add_task(realtime.publish, "image.deleted", image_id)


def increment_post(db: Session, image_id: int, field: str):
    column = getattr(StoredImage, field)
    result = db.execute(update(StoredImage).where(StoredImage.id == image_id).values(
        {field: column + 1, "revision": StoredImage.revision + 1}
    ).returning(StoredImage.id, StoredImage.likes_count, StoredImage.comments_count, StoredImage.revision)).mappings().first()
    if result is None:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    return {"image_id": result["id"], "likes_count": result["likes_count"],
            "comments_count": result["comments_count"], "revision": result["revision"]}


@app.post("/images/{image_id}/likes")
def like_image(image_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    result = increment_post(db, image_id, "likes_count")
    db.commit()
    background_tasks.add_task(realtime.publish, "post.updated", image_id, result)
    return result


@app.post("/images/{image_id}/comments", status_code=201)
def comment_image(image_id: int, body: CommentInput, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    result = increment_post(db, image_id, "comments_count")
    comment = ImageComment(image_id=image_id, body=body.body)
    db.add(comment)
    db.flush()
    result["comment"] = CommentResponse.model_validate(comment).model_dump(mode="json")
    db.commit()
    background_tasks.add_task(realtime.publish, "post.updated", image_id, result)
    return result


@app.get("/images/{image_id}/comments")
def list_comments(image_id: int, limit: int = Query(20, ge=1, le=100),
                  before_id: int | None = Query(None, gt=0), db: Session = Depends(get_db)):
    if db.scalar(select(StoredImage.id).where(StoredImage.id == image_id)) is None:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    query = select(ImageComment).where(ImageComment.image_id == image_id)
    if before_id is not None:
        query = query.where(ImageComment.id < before_id)
    rows = db.scalars(query.order_by(ImageComment.id.desc()).limit(limit + 1)).all()
    return {"items": [CommentResponse.model_validate(row) for row in rows[:limit]],
            "next_cursor": rows[limit - 1].id if len(rows) > limit else None}


@app.websocket("/ws")
async def websocket(socket: WebSocket):
    await realtime.serve(socket)
