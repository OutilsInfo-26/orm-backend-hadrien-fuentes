from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db import get_session
from app.models import Author, Book, Publisher, Person
from app.schemas import BookWithAuthor, BookWithAuthorObject, BookWithPublisher, BookFull

router = APIRouter(prefix="/orm", tags=["ORM jointure"])


@router.get("/books-with-authors", response_model=list[BookWithAuthor])
def list_books_with_authors(
    session: Session = Depends(get_session),
) -> list[BookWithAuthor]:
    stmt = (
        select(
            Book.id,
            Book.title,
            Book.pages,
            Author.name.label("author_name"),
        )
        .join(Author)
        .order_by(Book.id)
    )

    # On pourrait aussi utiliser mappings et ** pour éviter de répéter tous les champs de Book :
    # rows = session.execute(stmt).mappings().all()
    # return [BookWithAuthor(**row) for row in rows]

    rows = session.execute(stmt).all()
    return [
        BookWithAuthor(
            id=row.id,
            title=row.title,
            pages=row.pages,
            author_name=row.author_name,
        )
        for row in rows
    ]



@router.get("/books-with-author-object", response_model=list[BookWithAuthorObject])
def list_books_with_author_object(
    session: Session = Depends(get_session),
) -> list[BookWithAuthorObject]:
    # Contrairement à /books-with-authors qui extrait author_name comme simple string,
    # ici on charge des objets Book complets avec book.author navigable (objet Author).
    # joinedload → un seul SELECT avec JOIN, idéal pour une relation many-to-one.
    books = session.scalars(
        select(Book)
        .options(joinedload(Book.author))
        .order_by(Book.id)
    ).all()
    # book.author est un objet Author — on peut accéder à book.author.id, book.author.name
    return books


@router.get("/books-with-publisher", response_model=list[BookWithPublisher])
def list_books_with_publisher(
    session: Session = Depends(get_session),
) -> list[BookWithPublisher]:
    # Publisher n'est pas accessible via book.publisher (pas de relationship défini).
    # On doit donc construire la jointure manuellement avec join() et la condition explicite.
    stmt = (
        select(
            Book.id,
            Book.title,
            Book.pages,
            Publisher.name.label("publisher_name"),
        )
        .join(Publisher, Book.publisher_id == Publisher.id, isouter=True)
        .order_by(Book.id)
    )

    # Idem, on pourrait utiliser mappings et **
    rows = session.execute(stmt).all()
    return [
        BookWithPublisher(
            id=row.id,
            title=row.title,
            pages=row.pages,
            publisher_name=row.publisher_name,
        )
        for row in rows
    ]


@router.get("/books-full", response_model=list[BookFull])
def list_books_with_publisher(
    session: Session = Depends(get_session),
) -> list[BookFull]:
    # Publisher n'est pas accessible via book.publisher (pas de relationship défini).
    # On doit donc construire la jointure manuellement avec join() et la condition explicite.
    stmt = (
        select(
            Book.id,
            Book.title,
            Book.pages,
            Publisher.name.label("publisher_name"),
            Author.name.label("author_name"),
            Person.first_name.label("owner_first_name"),
            Person.last_name.label("owner_last_name"),
        )
        .join(Publisher, Book.publisher_id == Publisher.id, isouter=True)
        .join(Author, Book.author_id == Author.id, isouter=True)
        .join(Person, Book.owner_id == Person.id, isouter=True)
        .order_by(Book.id)
    )

    # Idem, on pourrait utiliser mappings et **
    rows = session.execute(stmt).all()
    return [
        BookFull(
            id=row.id,
            title=row.title,
            pages=row.pages,
            publisher_name=row.publisher_name,
            author_name=row.author_name,
            owner_name=f"{row.owner_first_name} {row.owner_last_name}"
        )
        for row in rows
    ]



