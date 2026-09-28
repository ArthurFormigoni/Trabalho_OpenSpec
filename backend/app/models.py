from datetime import datetime, timezone

from sqlalchemy import BigInteger, CheckConstraint, Integer, LargeBinary, ForeignKey, DateTime, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class StoredImage(Base):
    __tablename__ = "image"
    __table_args__ = (
        CheckConstraint("size_x > 0", name="ck_image_size_x_positive"),
        CheckConstraint("size_y > 0", name="ck_image_size_y_positive"),
        CheckConstraint("filesize_bytes > 0", name="ck_image_filesize_positive"),
        CheckConstraint("likes_count >= 0", name="ck_image_likes_nonnegative"),
        CheckConstraint("comments_count >= 0", name="ck_image_comments_nonnegative"),
        CheckConstraint("revision >= 0", name="ck_image_revision_nonnegative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    size_x: Mapped[int] = mapped_column(Integer, nullable=False)
    size_y: Mapped[int] = mapped_column(Integer, nullable=False)
    filesize_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    image_bytes: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    likes_count: Mapped[int] = mapped_column(BigInteger, server_default="0", nullable=False)
    comments_count: Mapped[int] = mapped_column(BigInteger, server_default="0", nullable=False)
    revision: Mapped[int] = mapped_column(BigInteger, server_default="0", nullable=False)


class ImageComment(Base):
    __tablename__ = "image_comment"
    __table_args__ = (
        CheckConstraint("length(body) BETWEEN 1 AND 1000", name="ck_comment_length"),
        Index("ix_image_comment_image_id_id", "image_id", "id"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_id: Mapped[int] = mapped_column(ForeignKey("image.id", ondelete="CASCADE"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,
                                               default=lambda: datetime.now(timezone.utc))
