from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import get_settings
from .db import Base, engine, get_db
from .image_processing import ImageEncodingError, ImageValidationError, process_image
from .models import StoredImage
from .schemas import ImageResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


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
        image_url=f"/images/{image.id}/content",
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
    return Response(content=image.image_bytes, media_type="image/avif")


@app.post("/images", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def create_image(file: UploadFile = File(...), db: Session = Depends(get_db)) -> ImageResponse:
    source = await file.read()
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
    return to_response(stored)


@app.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(image_id: int, db: Session = Depends(get_db)) -> None:
    image = db.get(StoredImage, image_id)
    if image is None:
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    db.delete(image)
    db.commit()

