from pydantic import BaseModel, ConfigDict, Field


class ImageResponse(BaseModel):
    id: int
    size_x: int = Field(gt=0)
    size_y: int = Field(gt=0)
    filesize_bytes: int = Field(gt=0, le=1048576)
    content_type: str = "image/avif"
    image_url: str

    model_config = ConfigDict(from_attributes=True)

