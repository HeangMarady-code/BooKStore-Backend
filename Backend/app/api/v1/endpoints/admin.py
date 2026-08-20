import io
import json
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_superuser
from app.db.session import get_db
from app.models.book import Book
from app.models.book_image import BookImage
from app.models.user import User

router = APIRouter()


def _serialize_book(book: Book) -> dict:
    return {
        "id": book.id,
        "title": book.title,
        "category": book.category,
        "description": book.description,
        "price": book.price,
        "discount_price": book.discount_price,
        "images": [
            {"image_url": img.image_url, "is_primary": bool(img.is_primary)}
            for img in book.images
        ],
    }


@router.get("/backup")
def backup_database(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    """Export the entire database (users, books, images) as a JSON download."""
    try:
        users = db.query(User).all()
        books = db.query(Book).order_by(Book.id).all()

        data = {
            "exported_at": datetime.now().isoformat(),
            "users": [
                {
                    "id": u.id,
                    "full_name": u.full_name,
                    "email": u.email,
                    "is_active": u.is_active,
                    "is_superuser": u.is_superuser,
                }
                for u in users
            ],
            "books": [_serialize_book(b) for b in books],
        }

        content = json.dumps(data, indent=2, ensure_ascii=False)
        filename = f"bookstore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        return StreamingResponse(
            io.BytesIO(content.encode("utf-8")),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(exc)}")


@router.post("/import")
async def import_database(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_superuser),
):
    """Import users and books from a JSON backup file."""
    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))

        if not isinstance(data, dict) or "books" not in data:
            raise HTTPException(status_code=400, detail="Invalid backup format: missing 'books' key")

        books = data.get("books", [])
        if not isinstance(books, list):
            raise HTTPException(status_code=400, detail="Invalid backup format: 'books' must be an array")

        imported_books = 0

        for item in books:
            if not isinstance(item, dict) or "title" not in item:
                continue  # skip malformed entries

            book = Book(
                title=item.get("title", ""),
                category=item.get("category", "Uncategorized"),
                description=item.get("description"),
                price=item.get("price", 0),
                discount_price=item.get("discount_price"),
            )
            db.add(book)
            db.flush()  # get book.id

            for img in item.get("images", []) or []:
                db.add(
                    BookImage(
                        book_id=book.id,
                        image_url=img.get("image_url", ""),
                        is_primary=1 if img.get("is_primary") else 0,
                    )
                )

            imported_books += 1

        db.commit()
        return {
            "message": f"Import completed successfully",
            "imported_books": imported_books,
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Import failed: {str(exc)}")