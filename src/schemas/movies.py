import datetime
from typing import List

from pydantic import BaseModel


class MovieModel(BaseModel):
    id: int
    name: str
    date: datetime.date
    score: float
    genre: str
    overview: str
    crew: str
    orig_title: str
    status: str
    orig_lang: str
    budget: float
    revenue: float
    country: str


class MovieListResponseSchema(BaseModel):
    movies: List[MovieModel]
    prev_page: int
    next_page: int
    total_pages: int
    total_items: int


class MovieDetailResponseSchema(MovieModel):
    pass

    class Config:
        from_attributes = True
