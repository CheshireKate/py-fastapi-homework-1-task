from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn

from src.database import init_db, close_db
from src.routes import movie_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="Movies homework",
    description="Description of project",
    lifespan=lifespan,
    redirect_slashes=False,
)

api_version_prefix = "/api/v1"

app.include_router(movie_router, prefix="/api/v1/theater", tags=["theater"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
