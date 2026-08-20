from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.book import Book
from app.models.book_image import BookImage
from app.schemas.book import BookCreate, BookListResponse, BookResponse, BookUpdate

router = APIRouter()


def _get_book_or_404(db: Session, book_id: int) -> Book:
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


def _apply_book_images(db: Session, book: Book, images) -> None:
    """Replace the images of a book with the provided list."""
    # Remove existing images
    db.query(BookImage).filter(BookImage.book_id == book.id).delete()
    for img in images:
        db.add(
            BookImage(
                book_id=book.id,
                image_url=img.image_url,
                is_primary=1 if img.is_primary else 0,
            )
        )


@router.get("", response_model=BookListResponse)
def list_books(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by title"),
    min_price: Optional[float] = Query(None, gt=0),
    max_price: Optional[float] = Query(None, gt=0),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List books with optional filtering, search, and pagination."""
    query = db.query(Book)

    if category:
        query = query.filter(Book.category == category)
    if search:
        query = query.filter(Book.title.ilike(f"%{search}%"))
    if min_price is not None:
        query = query.filter(Book.price >= min_price)
    if max_price is not None:
        query = query.filter(Book.price <= max_price)

    total = query.count()
    items = (
        query.order_by(Book.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return BookListResponse(total=total, items=items)


@router.get("/categories", response_model=list[str])
def list_categories(db: Session = Depends(get_db)):
    """Get all distinct book categories."""
    categories = db.query(Book.category).distinct().all()
    return [c[0] for c in categories]


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)) -> Book:
    """Get a single book by ID."""
    return _get_book_or_404(db, book_id)


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book_data: BookCreate, db: Session = Depends(get_db)) -> Book:
    """Create a new book with one or more images."""
    book = Book(
        title=book_data.title,
        category=book_data.category,
        description=book_data.description,
        price=book_data.price,
        discount_price=book_data.discount_price,
    )
    db.add(book)
    db.flush()  # get book.id

    if book_data.images:
        _apply_book_images(db, book, book_data.images)

    db.commit()
    db.refresh(book)
    return book


@router.put("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: Session = Depends(get_db),
) -> Book:
    """Update a book and optionally replace its images."""
    book = _get_book_or_404(db, book_id)

    if book_data.title is not None:
        book.title = book_data.title
    if book_data.category is not None:
        book.category = book_data.category
    if book_data.description is not None:
        book.description = book_data.description
    if book_data.price is not None:
        book.price = book_data.price
    if book_data.discount_price is not None:
        book.discount_price = book_data.discount_price

    if book_data.images is not None:
        _apply_book_images(db, book, book_data.images)

    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a book and its associated images."""
    book = _get_book_or_404(db, book_id)
    db.delete(book)  # cascade deletes book_images
    db.commit()