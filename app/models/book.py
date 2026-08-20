from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)          # original / regular price
    discount_price = Column(Float, nullable=True)  # discounted price
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    images = relationship(
        "BookImage",
        back_populates="book",
        cascade="all, delete-orphan",
        lazy="selectin",
    )