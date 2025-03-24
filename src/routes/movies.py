from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from starlette.responses import Response

from src.database.models import MovieModel
from src.database.session import get_db

from src.schemas.movies import MovieBase, MovieListResponseSchema

router = APIRouter()


@router.get("/movies/{film_id}", response_model=MovieListResponseSchema)
async def get_movie(movie_id: int, db: AsyncSession = Depends(get_db)) -> Response:
    result = await db.execute(select(MovieModel).where(MovieModel.id == movie_id))
    film = result.scalar_one_or_none()
    if not film:
        raise HTTPException(status_code=404, detail="Movie with the given ID was not found.")
    return film


@router.get("/movies", response_model=MovieListResponseSchema)
async def get_movies(page: int = 1, per_page: int = 10, db: AsyncSession = Depends(get_db)) -> Response:
    if page < 1:
        raise HTTPException(status_code=422, detail={
            "loc": ["query", "page"],
            "msg": "ensure this value is greater than or equal to 1",
            "type": "value_error.number.not_ge"
        })
    query = await db.query(MovieBase).offset(page).limit(per_page)
    movies = (await db.execute(query)).scalars().all()
    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")
    query = select(func.count(MovieModel.id))
    total_items = (await db.execute(query)).scalar()
    total_pages = total_items // per_page
    if total_items % per_page != 0:
        total_pages += 1
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None
    response = MovieListResponseSchema(
        movies=movies,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items,
    )

    return response
