from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Author, Book
from app.schemas import AuthorCreate, AuthorOut, AuthorUpdate, BookCreate, BookOut

router = APIRouter(prefix="/orm", tags=["ORM simple"])


@router.get("/authors", response_model=list[AuthorOut])
def list_authors(session: Session = Depends(get_session)) -> list[AuthorOut]:
    stmt = select(Author).order_by(Author.id)
    return session.scalars(stmt).all()


@router.post("/authors", response_model=AuthorOut, status_code=201)
def create_author(
    payload: AuthorCreate,
    session: Session = Depends(get_session),
) -> AuthorOut:
    author = Author(name=payload.name)
    session.add(author)
    session.commit()
    session.refresh(author)
    return author


@router.patch("/authors/{author_id}", response_model=AuthorOut)
def update_author(
    author_id: int,
    payload: AuthorUpdate,
    session: Session = Depends(get_session),
) -> AuthorOut:

    # On récupère l'auteur à mettre à jour depuis la base de données
    # get() est une méthode de Session qui permet de récupérer un objet par sa clé primaire (ici id)
    author = session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    # model_dump(exclude_unset=True) retourne uniquement les champs envoyés dans le body
    # Si le client envoie {} (body vide), rien n'est modifié
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(author, field, value)

    session.commit()
    session.refresh(author)
    return author


@router.get("/books", response_model=list[BookOut])
def list_books(session: Session = Depends(get_session)) -> list[BookOut]:
    stmt = select(Book).order_by(Book.id)
    return session.scalars(stmt).all()


@router.post("/books", response_model=BookOut, status_code=201)
def create_book(
    payload: BookCreate,
    session: Session = Depends(get_session),
) -> BookOut:
    author = session.get(Author, payload.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    book = Book(title=payload.title, pages=payload.pages, author_id=payload.author_id)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book
