from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload


from app.db import get_session
from app.models import Author, Book, Person, Tag, BookTag
from app.schemas import AuthorCreate, AuthorOut, AuthorUpdate, BookCreate, BookOut, PersonOut, PersonWithBooks, Stats, PersonWithBookCount

router = APIRouter(prefix="/orm", tags=["ORM stats"])

@router.get("/stats", response_model=Stats)
def get_stats(session: Session = Depends(get_session)) -> Stats:
    book_count = session.scalar(select(func.count(Book.id)))
    author_count = session.scalar(select(func.count(Author.id)))
    tag_count = session.scalar(select(func.count(Tag.id)))
    biggest_book_pages = session.scalar(select(func.max(Book.pages)))
    book_mean_pages = session.scalar(select(func.avg(Book.pages)))

    biggest_book_title = None
    if biggest_book_pages is not None:
        biggest_book = session.scalar(
            select(Book)
            .where(Book.pages == biggest_book_pages)
            .order_by(Book.id)
        )
        biggest_book_title = biggest_book.title if biggest_book else None

    return Stats(
        book_count=book_count,
        author_count=author_count,
        tag_count=tag_count,
        biggest_book_title=biggest_book_title,
        biggest_book_pages=biggest_book_pages,
        book_mean_pages=book_mean_pages,
    )

@router.get("/persons-with-book-count", response_model=list[PersonWithBookCount])
def list_persons_with_book_count(session: Session = Depends(get_session)) -> list[PersonWithBookCount]:
    stmt = (
        select(
            Person.first_name,
            Person.last_name,
            func.count(Book.id).label("book_count")
        )
        .join(Book, Book.owner_id == Person.id, isouter=True)
        .group_by(Person.id)
        .order_by(Person.id)
    )

    rows = session.execute(stmt).all()
    return [
        PersonWithBookCount(
            first_name=row.first_name,
            last_name=row.last_name,
            book_count=row.book_count
        )
        for row in rows
    ]