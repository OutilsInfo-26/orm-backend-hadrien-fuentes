# API REST avec SQL brut et ORM (FastAPI + SQLAlchemy)

Mini projet pour illustrer trois styles de requetes sur une base Postgres :
- SQL brut (via `text()`)
- ORM simple
- ORM avec jointure

Les schemas Pydantic servent a valider les donnees en entree et en sortie.
Le `docker-compose.yml` demarre deux services : `api` et `db` (Postgres).

## Demarrage ultra simple
1. Installer Docker Desktop (ou Docker Engine).
2. Dans ce dossier, lancer : `docker compose up --build -d`
3. Installer les dependances dans le conteneur : `docker compose exec api sh -lc "uv sync --no-dev --frozen || uv sync --no-dev"`
4. Lancer le serveur (avec reload) : `docker compose exec api sh -lc "uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"` (laisser ce terminal ouvert)
5. Ouvrir http://localhost:8000/docs pour tester les endpoints.

La base Postgres est creee automatiquement au demarrage avec quelques donnees de depart.

Pour arreter :
- Dans le terminal uvicorn : `Ctrl+C`
- Puis : `docker compose down`

## Endpoints disponibles
- `GET /ping` -> `{"status":"ok","message":"API is running"}`

### SQL brut
- `GET /raw/books` -> requete SQL simple (id + title)

### ORM simple
- `GET /orm/authors` -> liste des auteurs
- `POST /orm/authors` -> cree un auteur
- `GET /orm/books` -> liste des livres
- `POST /orm/books` -> cree un livre (valide author_id)

### ORM avec jointure
- `GET /orm/books-with-authors` -> livres + nom auteur (join)

### Exemples rapides
- `GET http://localhost:8000/raw/books`
- `GET http://localhost:8000/orm/books-with-authors`
- `POST http://localhost:8000/orm/books`
  ```json
  {
    "title": "Computers and Programs",
    "pages": 180,
    "author_id": 1
  }
  ```

## Validation automatique
Les schemas Pydantic imposent :
- `name` et `title` avec longueur minimale
- `pages` strictement positif
- `author_id` positif

Une requete invalide renvoie une erreur 422 visible dans Swagger UI.

## Structure du projet
- `app/main.py` : application FastAPI + routers
- `app/db.py` : moteur Postgres, session, init de la base
- `app/models.py` : modeles ORM SQLAlchemy
- `app/schemas.py` : schemas Pydantic (validation)
- `app/raw_sql.py` : exemple SQL brut
- `app/orm_simple.py` : exemple ORM simple
- `app/orm_join.py` : exemple ORM avec jointure
- `Dockerfile` + `docker-compose.yml`
- `pyproject.toml`

## Objectifs pedagogiques
- Voir la difference entre SQL brut et ORM
- Comprendre comment une jointure ORM se traduit en JSON
- Utiliser des schemas pour valider les donnees

## MLD
```mermaid
erDiagram
    PUBLISHERS {
        int id PK
        string name "unique, varchar(150)"
    }

    AUTHORS {
        int id PK
        string name "unique, varchar(100)"
    }

    BOOKS {
        int id PK
        string title "varchar(200)"
        int pages
        int author_id FK
        int publisher_id FK "nullable"
    }

    TAGS {
        int id PK
        string name "unique, varchar(50)"
    }

    BOOK_TAGS {
        int book_id PK, FK
        int tag_id  PK, FK
        date tagged_at
    }

    AUTHORS ||--o{ BOOKS : "author_id"
    PUBLISHERS ||--o{ BOOKS : "publisher_id (optional)"

    BOOKS ||--o{ BOOK_TAGS : "book_id"
    TAGS  ||--o{ BOOK_TAGS : "tag_id"
```
