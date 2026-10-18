from pydantic import BaseModel, Field
from typing import List
from src.books.schemas import Book
from src.reviews.schemas import ReviewCreateModel
import uuid
from datetime import datetime


class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)


class UserModel(BaseModel):
    uid: uuid.UUID
    email: str
    username: str
    password_hash: str = Field(exclude=True)
    first_name: str
    last_name: str
    is_varified: bool
    created_at: datetime
    update_at: datetime


class UserBooksModel(UserModel):
    books: List[Book]
    reviews: List[ReviewCreateModel]


class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)


class EmailModel(BaseModel):
    email_addresses: List[str]


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str
