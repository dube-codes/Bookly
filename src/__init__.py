from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from src.books.routes import router as books_router
from src.auth.routes import router as auth_router
from src.reviews.routes import router as reviews_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from .errors import register_all_errors
from .middleware import register_middleware


@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"server is starting...!")
    await init_db()
    yield
    print(f"server has been stopped")


version = "v1"
app = FastAPI(
    title="Bookly API",
    version=version,
    description="A simple API for managing books.",
    docs_url=f"/api/{version}/docs",
    redoc_url=f"/api/{version}/redoc",
    # lifespan=life_span, // not using lifespan
)

register_all_errors(app)

register_middleware(app)


app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["Auth"])
app.include_router(books_router, prefix=f"/api/{version}/books", tags=["Books"])
app.include_router(reviews_router, prefix=f"/api/{version}/review", tags=["Review"])
