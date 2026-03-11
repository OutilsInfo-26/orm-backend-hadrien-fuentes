from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db import get_session
from app.models import Book, BookTag, Tag
from app.schemas import BookWithTags, TagOut

router = APIRouter(prefix="/orm", tags=["ORM book-tag"])


@router.get("/books-with-tags", response_model=list[BookWithTags])
def list_books_with_tags(
    session: Session = Depends(get_session),
) -> list[BookWithTags]:
    # selectinload pour Book → book_tags  (collection, 1→N)  : génère un 2e SELECT avec IN (...)
    # joinedload  pour BookTag → tag      (objet unique, N→1) : ajoute un JOIN au 2e SELECT
    # Résultat : 2 requêtes seulement, pas de duplication de lignes
    books = session.scalars(
        select(Book)
        .options(selectinload(Book.book_tags).joinedload(BookTag.tag))
        .order_by(Book.id)
    ).all()

    return [
        BookWithTags(
            id=book.id,
            title=book.title,
            tags=[
                TagOut(name=bt.tag.name, tagged_at=bt.tagged_at)
                for bt in book.book_tags
            ],
        )
        for book in books
    ]


@router.get("/books-by-tag/{tag_name}", response_model=list[BookWithTags])
def list_books_by_tag(
    tag_name: str,
    session: Session = Depends(get_session),
) -> list[BookWithTags]:
    # On vérifie que le tag existe
    tag = session.scalar(select(Tag).where(Tag.name == tag_name))
    if not tag:
        raise HTTPException(status_code=404, detail=f"Tag '{tag_name}' not found")

    # On filtre les livres via la table de jointure :
    #   .join(Book.book_tags)  → JOIN book_tags ON book_tags.book_id = books.id
    #   .join(BookTag.tag)     → JOIN tags ON tags.id = book_tags.tag_id
    #   .where(Tag.name == tag_name) → WHERE tags.name = ?
    # On charge aussi les tags de chaque livre pour pouvoir les retourner
    books = session.scalars(
        select(Book)
        .join(Book.book_tags)
        .join(BookTag.tag)
        .where(Tag.name == tag_name)
        .options(selectinload(Book.book_tags).joinedload(BookTag.tag))
        .order_by(Book.id)
    ).all()

    return [
        BookWithTags(
            id=book.id,
            title=book.title,
            tags=[
                TagOut(name=bt.tag.name, tagged_at=bt.tagged_at)
                for bt in book.book_tags
            ],
        )
        for book in books
    ]
