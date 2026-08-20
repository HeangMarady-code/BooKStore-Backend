from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class BookImage(Base):
    __tablename__ = "book_images"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    is_primary = Column(Integer, default=0)  # 1 = primary image
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    book = relationship("Book", back_populates="images")