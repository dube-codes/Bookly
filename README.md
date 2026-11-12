# Bookly

Bookly is a personal learning project where I practise building a Python API. I built it with FastAPI and SQLModel to work through user accounts, books, reviews, and database-backed routes.

## Features

- User signup, email verification, login, refresh, logout, and password reset
- JWT access and refresh tokens, with revoked access tokens stored in Redis
- Create, list, view, update, and delete books
- Add a review to a book
- Send email through FastAPI Mail and a Celery task
- Alembic migration files for the database schema

## Tech stack

- Python
- FastAPI and Uvicorn
- SQLModel and SQLAlchemy
- PostgreSQL with the `asyncpg` driver listed in `requirements.txt`
- Alembic
- Redis
- Celery
- Pydantic
- PyJWT and Passlib with bcrypt
- FastAPI Mail
- Pytest

## Project structure

```text
.
├── src/
│   ├── auth/          # Authentication routes, schemas, and services
│   ├── books/         # Book routes, schemas, and services
│   ├── db/            # Database models, engine, and Redis blocklist
│   ├── reviews/       # Review routes, schemas, and services
│   ├── tests/         # Auth and book tests
│   ├── __init__.py    # FastAPI app and router registration
│   ├── celery_tasks.py
│   ├── config.py
│   ├── errors.py
│   ├── mail.py
│   └── middleware.py
├── migrations/
│   └── versions/      # Alembic revisions
├── alembic.ini
├── requirements.txt
└── README.md
```

## Database setup and migrations

The models define users, books, and reviews. They use PostgreSQL UUID and timezone-aware timestamp columns. The database URL is read from `database_url` in the settings.

Alembic is configured in `alembic.ini`, with its environment and revisions in `migrations/`. The current revision history has two heads, and one branch attempts to create a reviews table that its parent revision already created. See [Known limitations](#known-limitations) before applying migrations.

The app also defines an `init_db` function that creates tables from SQLModel metadata, but the FastAPI lifespan function that calls it is not enabled. The app therefore does not initialize tables through that function on startup.

## Installation and setup

Create and activate a virtual environment from the project root.

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python -m venv venv
source venv/bin/activate
```

Install the pinned dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root and set the variables listed below. The settings are loaded when the application imports `src.config`.

## Environment variables

The settings require these values. Use your own local credentials; do not commit real secrets.

```dotenv
database_url=<database-connection-url>
JWT_SECRET=<replace-with-a-private-secret>
JWT_ALGORITHM=<jwt-algorithm>
MAIL_USERNAME=<smtp-username>
MAIL_PASSWORD=<smtp-password>
MAIL_FROM=<sender-address>
MAIL_PORT=<smtp-port>
MAIL_SERVER=<smtp-server>
MAIL_FROM_NAME=<sender-name>
DOMAIN=<host-name-used-in-email-links>
```

Optional settings defined in the code:

- `REDIS_URL=<redis-connection-url>`; defaults to `redis://localhost:6379/0`
- `MAIL_STARTTLS=<true-or-false>`; defaults to `true`
- `MAIL_SSL_TLS=<true-or-false>`; defaults to `false`
- `USE_CREDENTIALS=<true-or-false>`; defaults to `true`
- `VALIDATE_CERTS=<true-or-false>`; defaults to `true`

## How to run

From the project root, start the API with:

```bash
uvicorn src:app --reload
```

The email-send route queues a Celery task, and the app uses Redis for token revocation. A PostgreSQL database, Redis, and working mail settings are needed for those flows. The code defines a Celery app, but a worker start command is not specified in the project.

The tests are under `src/tests/`. Run them with:

```bash
pytest
```

## API endpoints

All routes use the `/api/v1` prefix. Path parameters are shown in braces. Request bodies are JSON. Except where noted, a route's success status is FastAPI's default `200`; malformed requests can also receive FastAPI validation errors.

| Method | Path | Parameters or body | Status codes | Authentication |
|---|---|---|---|---|
| POST | `/api/v1/auth/send_email` | `EmailModel` JSON: `email_addresses` (array of strings) | 200 | None |
| POST | `/api/v1/auth/signup` | `UserCreateModel` JSON | 201, 403 for an existing email | None |
| GET | `/api/v1/auth/verify-acc/{token}` | `token` (string path parameter) | 200, 404 if the user is missing, 500 if verification cannot complete | None |
| POST | `/api/v1/auth/login` | `UserLoginModel` JSON | 200, 403 for invalid credentials | None |
| GET | `/api/v1/auth/refresh_tokren` | Refresh token in bearer authorization header | 200, 400 for an expired token, 403 for invalid token or token type | Refresh bearer token |
| GET | `/api/v1/auth/me` | None | 200, 403 for invalid token or failed role/verification check | Access bearer token; verified user with `admin` or `user` role |
| GET | `/api/v1/auth/logout` | Access token in bearer authorization header | 200, 403 for invalid or revoked token | Access bearer token |
| POST | `/api/v1/auth/password-reset-request` | `PasswordResetRequestModel` JSON: `email` (string) | 200 | None |
| POST | `/api/v1/auth/password-reset-confirm/{token}` | `token` (string path parameter) and `PasswordResetConfirmModel` JSON | 200, 400 if passwords differ, 404 if the user is missing, 500 if reset cannot complete | Reset token in path |
| GET | `/api/v1/books/` | None | 200, 403 for invalid token or failed role/verification check | Access bearer token; verified user with `admin` or `user` role |
| GET | `/api/v1/books/user/{user_uid}` | `user_uid` (string path parameter) | 200, 403 for invalid token or failed role/verification check | Access bearer token; verified user with `admin` or `user` role |
| POST | `/api/v1/books/` | `BookCreateModels` JSON | 201, 403 for invalid token or failed role/verification check | Access bearer token; verified user with `admin` or `user` role |
| GET | `/api/v1/books/{book_uid}` | `book_uid` (string path parameter) | 200, 404 if the book is missing, 403 for invalid token or failed role/verification check | Access bearer token; verified user with `admin` or `user` role |
| PATCH | `/api/v1/books/{book_uid}` | `book_uid` (string path parameter) and `BookUpdateModels` JSON | 200; 500 if a missing book causes response validation to fail because of the route guard bug | Access bearer token; verified user with `admin` or `user` role |
| DELETE | `/api/v1/books/{book_uid}` | `book_uid` (string path parameter) | 204 declared; currently returns 404 after deletion, 403 for invalid token or failed role/verification check | Access bearer token; verified user with `admin` or `user` role |
| POST | `/api/v1/review/book/{book_uid}` | `book_uid` (string path parameter) and `ReviewCreateModel` JSON | 200, 500 if review creation fails | Access bearer token |

The `BookCreateModels` body has `title`, `author`, `publisher`, `published_date`, `page_count`, and `language`. `BookUpdateModels` has `title`, `author`, `publisher`, `page_count`, and `language`. The review body has `rating` and `review_text`.

## Request and response examples

Create a book:

```json
{
  "title": "Learning Python",
  "author": "Alex Example",
  "publisher": "Example Press",
  "published_date": "2025-01-15",
  "page_count": 320,
  "language": "English"
}
```

A successful book creation returns the `Book` response shape:

```json
{
  "uid": "9b26ca70-c73b-4a63-a53b-57471df18513",
  "title": "Learning Python",
  "author": "Alex Example",
  "publisher": "Example Press",
  "published_date": "2025-01-15",
  "page_count": 320,
  "language": "English",
  "created_at": "2026-01-02T03:04:05+00:00",
  "update_at": "2026-01-02T03:04:05+00:00"
}
```

Log in with `POST /api/v1/auth/login`:

```json
{
  "email": "learner@example.com",
  "password": "example-password"
}
```

The response contains the tokens and a user object:

```json
{
  "message": "Login Successful..!!",
  "access_token": "<access-token>",
  "refresh_token": "<refresh-token>",
  "user": {
    "uid": "9b26ca70-c73b-4a63-a53b-57471df18513",
    "email": "learner@example.com"
  }
}
```

Add a review with `POST /api/v1/review/book/{book_uid}`:

```json
{
  "rating": 4,
  "review_text": "A useful introduction."
}
```

## Swagger and ReDoc

The app enables FastAPI documentation at:

- Swagger UI: `/api/v1/docs`
- ReDoc: `/api/v1/redoc`

## What I learned

While building this project, I practised FastAPI routers and dependency injection, Pydantic request and response models, async database sessions, SQLModel relationships, JWT access and refresh tokens, password hashing, role checks, Alembic revisions, Redis token revocation, and queuing email work with Celery.

## Known limitations

- `POST /api/v1/review/book/{book_uid}` creates a review but uses the default `200` response instead of `201`.
- The `book_uid`, `user_uid`, and token path parameters are strings, not validated UUID or token types. The API version is a fixed `v1` prefix.
- Signup is unauthenticated and returns the newly created user object, including profile data. The per-user books endpoint also allows any authenticated, verified user with an allowed role to request another user's ID; ownership is not checked.
- The book-creation service assigns the user ID from the token without explicitly checking that the referenced user still exists; it relies on the database foreign key.
- The review model limits ratings to values less than 5 but does not set a minimum.
- `ReviewModel` is not used by a route. The user and book response schemas instead embed `ReviewCreateModel`, which only contains `rating` and `review_text`.
- The book update route checks the `update_book` function rather than its result. If the book is missing, it can return `None` where a `Book` response is required instead of reaching its 404 branch.
- The delete service returns `None` both when a book is missing and after it deletes one. The route therefore reports 404 even after a successful deletion, despite declaring 204.
- The review service catches every exception, including its own not-found errors, and converts it to a 500 response.
- The migration history has two heads (`4b0a0ce420ab` and `878f4715f7fb`). The latter creates a reviews table already created by its parent revision, so the migration history needs repair before it can be applied reliably.
- The `life_span` function calls `init_db`, but it is commented out in the `FastAPI` constructor. No route or startup hook currently calls `init_db`.
- The `MAIL_PORT` setting is required, but the mail connection is configured with port `587` directly.
- The database code constructs an `AsyncEngine` from `sqlmodel.create_engine`, while the database sessions are asynchronous. This engine setup may not be compatible at runtime.
- The tests cover only a small part of auth and book behavior, and the current fixtures do not replace the service instances used by the routes.

## Potential improvements

- Repair and test the Alembic revision graph, then document a verified migration workflow.
- Connect database initialization or migrations to a clear development setup.
- Fix book update and delete handling, and add tests for missing records.
- Add ownership checks to the per-user books route.
- Validate UUID path parameters and define an explicit review response model.
- Add a rating lower bound and validate email fields where they are accepted.
- Improve service error handling so missing records keep their intended 404 responses.
- Expand the tests to cover authentication, authorization, request validation, and response schemas.
