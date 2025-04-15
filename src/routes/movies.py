from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.database.models import MovieModel
from src.schemas.movies import MovieModel as MovieSchema
from src.database.session import get_db

from src.schemas.movies import MovieListResponseSchema, MovieDetailResponseSchema


router = APIRouter(redirect_slashes=False)


@router.get("/movies/", response_model=MovieListResponseSchema)
async def get_movies(
    page: int = 1, per_page: int = 10, db: AsyncSession = Depends(get_db)
) -> MovieListResponseSchema:
    if page < 1:
        raise HTTPException(
            status_code=422,
            detail={
                "loc": ["query", "page"],
                "msg": "Input should be greater than or equal to 1",
                "type": "value_error.number.not_ge",
            },
        )
    if not (1 <= per_page <= 20):
        raise HTTPException(
            status_code=422,
            detail={
                "loc": ["query", "per_page"],
                "msg": "Input should be greater than or equal to 1",
                "type": "value_error.number.not_in_range",
            },
        )
    query = select(MovieModel).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    movies = result.scalars().all()
    if not movies:
        raise HTTPException(status_code=404, detail="No movies found.")
    query = select(func.count(MovieModel.id))
    total_items = (await db.execute(query)).scalar()
    total_pages = total_items // per_page
    if total_items % per_page != 0:
        total_pages += 1
    prefix = "/theater/movies/"
    prev_page_url = (
        f"{prefix}?page={page - 1}&per_page={per_page}" if page > 1 else None
    )
    next_page_url = (
        f"{prefix}?page={page + 1}&per_page={per_page}" if page < total_pages else None
    )

    response = MovieListResponseSchema(
        movies=[MovieDetailResponseSchema.from_orm(movie) for movie in movies],
        prev_page=prev_page_url,
        next_page=next_page_url,
        total_pages=total_pages,
        total_items=total_items,
    )

    return response


@router.get("/movies/{movie_id}/", response_model=MovieDetailResponseSchema)
async def get_movie(
    movie_id: int, db: AsyncSession = Depends(get_db)
) -> MovieDetailResponseSchema:
    result = await db.execute(select(MovieModel).where(MovieModel.id == movie_id))
    film = result.scalar_one_or_none()
    print("Router slash redirect setting:", router.redirect_slashes)
    if not film:
        raise HTTPException(
            status_code=404, detail="Movie with the given ID was not found."
        )
    return film
