from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload


from app.db import get_session
from app.models import Author, Book, Person
from app.schemas import AuthorCreate, AuthorOut, AuthorUpdate, BookCreate, BookOut, PersonOut, PersonWithBooks

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

@router.delete("/books/{book_id}", status_code=204)
def delete_book(
    book_id: int,
    session: Session = Depends(get_session),
) -> None:
    stmt = select(Book).where(Book.id == book_id)
    book = session.scalar(stmt)

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    try:
        session.delete(book)
        session.commit()
    except:
        raise HTTPException(
            status_code=409,
            detail="Impossible de supprimer ce livre car il est lié à d'autres enregistrements."
            )  

@router.get("/persons", response_model=list[PersonOut])
def list_persons(session: Session = Depends(get_session)) -> list[PersonOut]:
    stmt = select(Person).order_by(Person.id)
    return session.scalars(stmt).all()

@router.post("/persons", response_model=PersonOut, status_code=201)
def create_person(
    payload: PersonOut,
    session: Session = Depends(get_session),
) -> PersonOut:
    person = Person(first_name=payload.first_name, last_name=payload.last_name)
    session.add(person)
    session.commit()
    session.refresh(person)
    return person

@router.get("/persons-with-books", response_model=list[PersonWithBooks])
def list_persons_with_books(session: Session = Depends(get_session)) -> list[PersonWithBooks]:


    stmt = (
        select(Person)
        .options(selectinload(Person.books_owned))
        .order_by(Person.id)
    )
    persons = session.scalars(stmt).all()
    return [
        PersonWithBooks(
            first_name=person.first_name,
            last_name=person.last_name,
            books_owned_titles=[book.title for book in person.books_owned]
        )
        for person in persons
    ]