from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from .schemas import Book, BookUpdateModels, BookCreateModels, BookDetailsModel
import uuid

# from src.books.book_data import books
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.auth.dependencies import AccessTokenBearer, RoleChecker

router = APIRouter()
book_ser = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))


@router.get("/", response_model=List[Book], dependencies=[role_checker])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    books = await book_ser.get_all_books(session)
    return books


@router.get("/user/{user_uid}", response_model=List[Book], dependencies=[role_checker])
async def get_user_book_submission(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    books = await book_ser.get_user_books(user_uid, session)
    return books


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
    dependencies=[role_checker],
)
async def create_a_book(
    book_data: BookCreateModels,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):

    user_id = token_details.get("user")["user_uid"]
    new_book = await book_ser.create_book(book_data, user_id, session)
    return new_book


@router.get("/{book_uid}", response_model=BookDetailsModel, dependencies=[role_checker])
async def get_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    book = await book_ser.get_book(book_uid, session)

    if book:
        return book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with this Id - {book_uid} not found.!",
        )


@router.patch("/{book_uid}", response_model=Book, dependencies=[role_checker])
async def update_book(
    book_uid: str,
    update_book_dt: BookUpdateModels,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    book_updated = await book_ser.update_book(book_uid, update_book_dt, session)

    if update_book:
        return book_updated
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book not found with this Id - {book_uid}.!",
        )


@router.delete(
    "/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    book_to_del = await book_ser.delete_book(book_uid, session)
    if book_to_del:
        return None
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book not found with give Id - {book_uid}.!",
        )
