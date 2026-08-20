# Book Store Backend

FastAPI + PostgreSQL backend for the Book Store application.

> This repository contains only the **Backend** code.
> The frontend applications (frontend_user, frontend_admin) are kept out of this repo.

## Features

- **Books**: title, category, description, price, discount_price, multiple images
- **Authentication**: signup, login, JWT bearer token auth
- **Admin**: first registered user is the admin (superuser)
- **Database**: PostgreSQL on Render (SQLite local fallback for dev)

## Quick Start

```bash
cd Backend
pip install -r requirements.txt

# configure .env (see Backend/.env.example)
# then run:
python -m uvicorn app.main:app --reload
```

Swagger docs: http://localhost:8000/docs

## Seed Admin

```bash
cd Backend
python seed_admin.py
```

Creates `adminbook@gmail.com` / `admin11112222` as the admin (superuser).

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Register a user |
| POST | `/api/v1/auth/login` | Login → JWT token |
| GET | `/api/v1/auth/me` | Current user profile |
| GET/POST | `/api/v1/books` | List / create books |
| GET/PUT/DELETE | `/api/v1/books/{id}` | Get / update / delete a book |
| GET | `/api/v1/books/categories` | List categories |
| GET | `/api/v1/admin/backup` | Download DB backup (JSON) — admin only |
| POST | `/api/v1/admin/import` | Import DB backup — admin only |