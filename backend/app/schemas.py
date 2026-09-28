from pydantic import BaseModel, ConfigDict, Field
from pydantic import field_validator
from datetime import datetime, timezone


class ImageResponse(BaseModel):
    id: int
    size_x: int = Field(gt=0)
    size_y: int = Field(gt=0)
    filesize_bytes: int = Field(gt=0, le=1048576)
    content_type: str = "image/avif"
    image_url: str
    likes_count: int = Field(default=0, ge=0)
    comments_count: int = Field(default=0, ge=0)
    revision: int = Field(default=0, ge=0)

    model_config = ConfigDict(from_attributes=True)


class CommentInput(BaseModel):
    body: str = Field(min_length=1, max_length=1000)

    @field_validator("body", mode="before")
    @classmethod
    def trim_body(cls, value):
        return value.strip() if isinstance(value, str) else value


class CommentResponse(BaseModel):
    id: int
    image_id: int
    body: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

    @field_validator("created_at")
    @classmethod
    def utc_timestamp(cls, value):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
