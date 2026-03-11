from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_session
from app.schemas import BookSummary

router = APIRouter(prefix="/raw", tags=["SQL brut"])


@router.get("/books", response_model=list[BookSummary])
def list_books_raw(session: Session = Depends(get_session)) -> list[BookSummary]:
    """Query SQL brute avec text() et mapping manuel."""
    stmt = text("SELECT id, title FROM books ORDER BY id")

    # mappings() permet de récupérer les résultats sous forme de dictionnaires 
    # au lieu de tuples, ce qui facilite la création des objets BookSummary
    rows = session.execute(stmt).mappings().all()
    return [BookSummary(**row) for row in rows]

    # En python ** permet de décompresser un dictionnaire en arguments nommés.

    # row = {"id": 1, "title": "Python 101"}
    # BookSummary(**row)

    # équivalent à :
    # BookSummary(id=1, title="Python 101")
