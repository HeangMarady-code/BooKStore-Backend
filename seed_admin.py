"""
Seed the admin user (superuser) into the database.

Creates adminbook@gmail.com / admin11112222 as the first admin if it doesn't exist.
Run from the Backend folder:

    python seed_admin.py

Requires a working database connection (set DATABASE_CONNECTION_URL in .env).
"""
import logging
import os
import sys

# Ensure the app package is importable when running as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.user import User
import app.models  # noqa: F401  ensure all models are registered

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

ADMIN_EMAIL = "adminbook@gmail.com"
ADMIN_PASSWORD = "admin11112222"
ADMIN_NAME = "Admin"


def seed_admin() -> None:
    # Create all tables first (works with SQLite local DB & PostgreSQL)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if existing:
            # Ensure the existing user is a superuser
            if not existing.is_superuser:
                existing.is_superuser = True
                db.commit()
                logger.info("Existing user %s promoted to admin.", ADMIN_EMAIL)
            else:
                logger.info("Admin user %s already exists.", ADMIN_EMAIL)
            return

        admin = User(
            full_name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            hashed_password=hash_password(ADMIN_PASSWORD),
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info("Admin user created: %s (id=%s) — is_superuser=True", ADMIN_EMAIL, admin.id)
    except Exception as exc:
        db.rollback()
        logger.error("Failed to seed admin user: %s", exc)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()