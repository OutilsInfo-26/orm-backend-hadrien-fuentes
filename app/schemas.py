from datetime import date

from pydantic import BaseModel, Field


class AuthorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Author full name")

    model_config = {
        "json_schema_extra": {
            "example": {"name": "Ada Lovelace"}
        }
    }


class AuthorUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=100)


class AuthorOut(AuthorCreate):
    id: int

    model_config = {
        "from_attributes": True,
    }


class BookCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200, description="Book title")
    pages: int = Field(..., gt=0, le=2000, description="Number of pages")
    author_id: int = Field(..., gt=0, description="Existing author id")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Notes on the Analytical Engine",
                "pages": 120,
                "author_id": 1,
            }
        }
    }


class BookOut(BookCreate):
    id: int

    model_config = {
        "from_attributes": True,
    }


class BookSummary(BaseModel):
    id: int
    title: str


class BookWithAuthor(BaseModel):
    id: int
    title: str
    pages: int
    author_name: str


# Contrairement à BookWithAuthor, ici author est un objet imbriqué
# accessible via la navigation ORM (book.author.id, book.author.name)
class BookWithAuthorObject(BaseModel):
    id: int
    title: str
    pages: int
    author: AuthorOut

    model_config = {"from_attributes": True}


class BookWithPublisher(BaseModel):
    id: int
    title: str
    pages: int
    publisher_name: str | None

class BookFull(BaseModel):
    id: int
    title: str
    pages: int
    author_name: str
    publisher_name: str | None
    owner_name: str | None


class TagOut(BaseModel):
    name: str
    tagged_at: date

    model_config = {"from_attributes": True}


class BookWithTags(BaseModel):
    id: int
    title: str
    tags: list[TagOut]

    model_config = {"from_attributes": True}

class PersonOut(BaseModel):
    first_name: str
    last_name: str

    model_config = {"from_attributes": True}

class PersonCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)

    model_config = {
        "json_schema_extra": {
            "example": {
                "first_name": "Hadrien",
                "last_name": "Fuentes",
            }
        }
    }

class PersonWithBooks(BaseModel):
    first_name: str
    last_name: str
    books_owned_titles: list[str]

    model_config = {"from_attributes": True}

class PersonWithBookCount(BaseModel):
    first_name: str
    last_name: str
    book_count: int

    model_config = {"from_attributes": True}

class Stats(BaseModel):
    book_count: int
    author_count: int
    tag_count: int
    biggest_book_title: str | None
    biggest_book_pages: int | None
    book_mean_pages: float | None