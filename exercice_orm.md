# Exercice : pratiquer ORM + SQL brut (FastAPI)

Objectif : étendre le mini projet ORM pour manipuler des requêtes SQL et ORM, tout en gardant la validation via schemas Pydantic.

---

## Questions de compréhension

Répondez aux questions suivantes avant de commencer l'implémentation.

### Base de données

1. Qu'est-ce qu'une clé primaire et à quoi sert-elle ?
2. Qu'est-ce qu'une clé étrangère ? Donnez un exemple avec les tables du projet.
3. Quelle est la différence entre un `INNER JOIN` et un `LEFT JOIN` ? Quand utilise-t-on l'un plutôt que l'autre ?
4. Qu'est-ce qu'une table de jointure (association) ? Pourquoi en utilise-t-on une dans ce projet ?
5. Quelle est la différence entre une relation 1:N et une relation N:M ?

### Modèles SQLAlchemy (`models.py`)

6. Pourquoi crée-t-on une classe `Base` qui hérite de `DeclarativeBase` au lieu d'hériter directement de `DeclarativeBase` dans chaque modèle ?
7. Comment sont créées les tables en base de données à partir des modèles Python ?
8. Expliquez cette ligne :
   ```python
   id: Mapped[int] = mapped_column(primary_key=True)
   ```
9. Comment indique-t-on qu'un champ peut être `NULL` (optionnel) en base de données avec SQLAlchemy 2.0 ?
10. Expliquez cette ligne :
    ```python
    book_tags: Mapped[list["BookTag"]] = relationship("BookTag", back_populates="book")
    ```
    Que signifie `back_populates` ? Que se passe-t-il si on l'omet ?
11. Dans le modèle `Book`, `publisher_id` est défini comme `ForeignKey` mais il n'y a pas de `relationship` vers `Publisher`. Quelle conséquence cela a-t-il sur les requêtes ?

### Schemas Pydantic (`schemas.py`)

12. À quoi servent les schemas Pydantic dans ce projet ? Pourquoi ne retourne-t-on pas directement les objets SQLAlchemy ?
13. Dans `BookCreate`, expliquez le rôle des `...` dans `Field(...)` et celui de `min_length`, `max_length`.
14. Qu'est-ce que `model_config = {"from_attributes": True}` et dans quel cas est-ce nécessaire ?
15. Quelle est la différence entre `BookCreate` et `BookOut` ? Pourquoi avoir deux schemas séparés ?
16. Dans `AuthorUpdate`, tous les champs sont optionnels (`str | None`). Pourquoi ? Quelle est la différence avec `AuthorCreate` ?

### Routes FastAPI (`orm_simple.py`, `orm_join.py`, etc.)

17. Si le router est défini avec `prefix="/orm"`, pourquoi faut-il appeler `/orm/authors` et non `/authors` ?
18. Quelle est la différence entre un paramètre de route et un paramètre de requête (query parameter) ? Donnez un exemple de chacun.
19. Pourquoi utilise-t-on `PATCH` pour la mise à jour d'un auteur plutôt que `PUT` ?
20. Que fait `payload.model_dump(exclude_unset=True)` dans la route de mise à jour ? Que se passerait-il sans `exclude_unset=True` ?
21. Pourquoi utilise-t-on `session.get(Author, author_id)` plutôt que `session.execute(select(Author).where(Author.id == author_id))` pour chercher un élément par sa clé primaire ?

### ORM et requêtes

22. Expliquez la différence entre `session.add()` et `session.commit()`. Que se passe-t-il si on appelle `session.add()` sans `session.commit()` ?
23. À quoi sert `session.flush()` ? Dans quels cas l'utilise-t-on ?
24. Expliquez la différence entre `joinedload` et `selectinload`. Dans quel cas préfère-t-on l'un à l'autre ?
25. Pourquoi dans FastAPI est-il quasi-obligatoire d'utiliser `selectinload`/`joinedload` lorsqu'on veut retourner des relations ? Que se passe-t-il si on ne le fait pas ?
26. Quelle est la différence entre ces deux approches ?
    ```python
    # Approche A
    select(Book.id, Book.title, Author.name.label("author_name")).join(Author)

    # Approche B
    select(Book).options(joinedload(Book.author))
    ```

---

## Tâches à réaliser

Les tâches suivantes sont à implémenter dans de nouveaux fichiers ou dans les fichiers existants selon la logique du projet.

### Modèle

#### 1. Table `Person`
Créez un modèle `Person` représentant le propriétaire d'un livre.

- Une personne peut posséder plusieurs livres
- Un livre appartient à une seule personne (relation 1:N)
- Attributs minimum : `id`, `first_name`, `last_name`
- Ajoutez le champ `owner_id` dans le modèle `Book` (avec ou sans `relationship`, à vous de choisir et de justifier)
- Ajoutez des données de test dans `init_db()`

### Routes — Persons

#### 2. Créer une personne
`POST /orm/persons`

- Valider les données avec un schema Pydantic
- Retourner la personne créée

#### 3. Lister les personnes
`GET /orm/persons`

- Retourner la liste de toutes les personnes

#### 4. Personnes avec leurs livres (nom seulement)
`GET /orm/persons-with-books`

- Retourner chaque personne avec la liste des titres de ses livres
- Ne pas retourner l'objet `Book` complet — uniquement le titre (string)
- Choisir la bonne stratégie de chargement et justifier votre choix

### Routes — Livres enrichis

#### 5. Livres avec auteur et éditeur
`GET /orm/books-full`

- Retourner chaque livre avec le nom de l'auteur et le nom de l'éditeur
- Rappel : `publisher_id` existe dans `Book` mais il n'y a pas de `relationship` — la jointure doit être faite manuellement

#### 6. Supprimer un livre
`DELETE /orm/books/{book_id}`

- Retourner `204 No Content` si supprimé
- Retourner `404` si le livre n'existe pas

### Routes — Statistiques

#### 7. Statistiques générales
`GET /orm/stats`

Retourner un objet JSON avec :
- Nombre total de livres
- Nombre total d'auteurs
- Nombre total de tags
- Titre et nombre de pages du livre le plus long
- Moyenne du nombre de pages de tous les livres

#### 8. Personnes avec le nombre de livres
`GET /orm/persons-with-book-count`

- Retourner chaque personne avec le nombre de livres qu'elle possède
- Utiliser une aggregation (`COUNT`) — pas de chargement de la liste des livres

---

## Validation avec PgAdmin

- Créez un fichier `validation.sql` avec des requêtes SQL pour vérifier que les données sont correctement insérées, mises à jour et supprimées dans la base de données
- Exécutez ces requêtes dans PgAdmin pour valider les opérations effectuées par votre API
- Contrôler que les jointures fonctionnent correctement en vérifiant les données retournées par les endpoints qui utilisent des jointures
- Contrôler les valeurs des statistiques retournées par les endpoints de statistiques

## Checklist de validation

- Les nouveaux endpoints apparaissent dans Swagger UI (`/docs`)
- Les validations Pydantic renvoient bien `422` si les données sont invalides
- Les routes `404` fonctionnent correctement
- Le `DELETE` retourne bien `204`
- Les statistiques affichent des valeurs correctes
- Les requêtes avec jointure ne font pas de N+1 (vérifier avec les logs SQL si disponible)
