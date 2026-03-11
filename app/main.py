from fastapi import FastAPI

from app.db import init_db
from app.orm_book_tag import router as orm_book_tag_router
from app.orm_join import router as orm_join_router
from app.orm_simple import router as orm_simple_router
from app.raw_sql import router as raw_sql_router

app = FastAPI(
    title="FastAPI - SQL vs ORM",
    description="Small project to compare raw SQL and ORM queries with schemas.",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/ping")
def ping() -> dict[str, str]:
    return {"status": "ok", "message": "API is running"}


app.include_router(raw_sql_router)
app.include_router(orm_simple_router)
app.include_router(orm_join_router)
app.include_router(orm_book_tag_router)
