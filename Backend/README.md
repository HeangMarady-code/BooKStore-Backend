# Book Store API (Backend)

FastAPI backend for the Book Store application with PostgreSQL.

## Features

- **Books**: title, category, description, price, discount_price, multiple images
- **Authentication**: signup, login, JWT bearer token auth
- **User profile**: GET /api/v1/auth/me

## Tech Stack

- FastAPI
- SQLAlchemy 2.0 ORM
- PostgreSQL
- JWT Authentication (PyJWT + Passlib)

## Folder Structure

```
Backend/
├── app/
│   ├── api/
│   │   ├── deps.py                 # FastAPI dependencies (auth)
│   │   └── v1/
│   │       ├── router.py           # API router aggregation
│   │       └── endpoints/
│   │           ├── auth.py         # signup / login / me
│   │           └── books.py        # CRUD for books + images
│   ├── core/
│   │   ├── config.py               # Settings from .env
│   │   └── security.py             # Password hashing + JWT
│   ├── db/
│   │   ├── base.py                 # Declarative Base
│   │   └── session.py              # Engine & SessionLocal
│   ├── models/
│   │   ├── user.py
│   │   ├── book.py
│   │   └── book_image.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── token.py
│   │   └── book.py
│   └── main.py                     # FastAPI app entrypoint
├── .env                            # Local config (not committed)
├── .env.example                    # Template for .env
└── requirements.txt
```

## Setup & Run

### 1. Configure the environment

Copy `.env.example` to `.env` and fill in your PostgreSQL credentials:

```env
DATABASE_HOST=your-postgres-host
DATABASE_PORT=5432
DATABASE_NAME=book_store_xdbt
DATABASE_USER=bookstore
DATABASE_PASSWORD=your_database_password

SECRET_KEY=some-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2. Install dependencies

```bash
cd Backend
pip install -r requirements.txt
```

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- Interactive Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

## API Endpoints

### Authentication (`/api/v1/auth`)

| Method | Endpoint  | Description                          |
|--------|-----------|--------------------------------------|
| POST   | /signup   | Register a new user                  |
| POST   | /login    | Login (form) → returns access token  |
| GET    | /me       | Get current user profile (Bearer)    |

### Books (`/api/v1/books`)

| Method | Endpoint        | Description                                       |
|--------|-----------------|---------------------------------------------------|
| GET    | /               | List books (supports `category`, `search`, `min_price`, `max_price`, `page`, `page_size`) |
| GET    | /categories     | List all distinct book categories                 |
| GET    | /{book_id}      | Get book details with images                      |
| POST   | /               | Create a book (with `images[]`)                   |
| PUT    | /{book_id}      | Update a book (and optionally its images)         |
| DELETE | /{book_id}      | Delete a book                                     |

## Example: Create a Book

```json
POST /api/v1/books
{
  "title": "The Great Gatsby",
  "category": "Fiction",
  "description": "A classic novel.",
  "price": 19.99,
  "discount_price": 14.99,
  "images": [
    {"image_url": "https://example.com/cover.jpg", "is_primary": true},
    {"image_url": "https://example.com/back.jpg", "is_primary": false}
  ]
}
```

## Login Flow

1. `POST /api/v1/auth/signup` with `{ "email", "full_name", "password" }`
2. `POST /api/v1/auth/login` with form data `username=<email>` & `password=<password>`
3. Use the returned `access_token` in the `Authorization: Bearer <token>` header for protected endpoints.