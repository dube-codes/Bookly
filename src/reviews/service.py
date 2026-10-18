from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import ReviewCreateModel
from fastapi.exceptions import HTTPException
from fastapi import status
import logging

book_serv = BookService()
user_serv = UserService()


class ReviewService:

    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        try:
            book = await book_serv.get_book(book_uid=book_uid, session=session)
            user = await user_serv.get_user_by_email(email=user_email, session=session)

            new_review_dict = review_data.model_dump()
            new_review = Review(**new_review_dict)

            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"Book not found..!"
                )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found..!"
                )

            new_review.user = user
            new_review.book = book

            session.add(new_review)
            await session.commit()

            return new_review
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Oops. Something want wrong...!",
            )
