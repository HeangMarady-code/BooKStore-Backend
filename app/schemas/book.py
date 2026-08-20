from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BookImageBase(BaseModel):
    image_url: str = Field(..., max_length=500)
    is_primary: Optional[bool] = False


class BookImageCreate(BaseModel):
    image_url: str = Field(..., max_length=500)
    is_primary: Optional[bool] = False


class BookImageResponse(BookImageBase):
    id: int
    book_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    discount_price: Optional[float] = Field(None, gt=0)


class BookCreate(BookBase):
    images: List[BookImageCreate] = []


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    discount_price: Optional[float] = Field(None, gt=0)
    images: Optional[List[BookImageCreate]] = None


class BookResponse(BookBase):
    id: int
    images: List[BookImageResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookListResponse(BaseModel):
    total: int
    items: List[BookResponse]