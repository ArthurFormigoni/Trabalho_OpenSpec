from sqlalchemy import BigInteger, CheckConstraint, Integer, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class StoredImage(Base):
    __tablename__ = "image"
    __table_args__ = (
        CheckConstraint("size_x > 0", name="ck_image_size_x_positive"),
        CheckConstraint("size_y > 0", name="ck_image_size_y_positive"),
        CheckConstraint("filesize_bytes > 0", name="ck_image_filesize_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    size_x: Mapped[int] = mapped_column(Integer, nullable=False)
    size_y: Mapped[int] = mapped_column(Integer, nullable=False)
    filesize_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    image_bytes: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
