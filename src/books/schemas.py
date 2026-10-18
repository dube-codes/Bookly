import uuid
from datetime import datetime, date
from typing import List
from pydantic import BaseModel
from src.reviews.schemas import ReviewCreateModel


class Book(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    update_at: datetime


class BookCreateModels(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str


class BookUpdateModels(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str


class BookDetailsModel(Book):
    reviews: List[ReviewCreateModel]
