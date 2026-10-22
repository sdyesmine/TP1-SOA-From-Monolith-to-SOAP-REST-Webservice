"""API REST avec FastAPI.
Lancer : uvicorn main:app --reload
Docs   : http://localhost:8000/docs
"""
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

import db

app = FastAPI(title="BiblioTech API", version="1.0.0")

@app.on_event("startup")
def startup():
    db.init_db()

# ---------- Modèles Pydantic (validation) ----------
class BookIn(BaseModel):
    id: int = Field(..., gt=0, description="L'ID doit être supérieur à 0")
    title: str = Field(..., min_length=1, description="Le titre ne peut pas être vide")
    author: str = Field(..., min_length=1, description="L'auteur ne peut pas être vide")
    available_copies: int = Field(..., ge=0, description="Le stock ne peut pas être négatif")
    rental_price: float = Field(..., ge=0, description="Le prix ne peut pas être négatif")

class BookUpdate(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    available_copies: int = Field(..., ge=0)
    rental_price: float = Field(..., ge=0)

class BookOut(BookIn):
    pass

# ---------- Endpoints ----------
@app.get("/books", response_model=list[BookOut])
def get_books():
    """Liste tous les livres."""
    # Note: Votre db.py doit avoir une fonction get_all_books(), sinon adaptez selon votre implémentation
    try:
        from db import SessionLocal, Book
        session = SessionLocal()
        books = session.query(Book).all()
        session.close()
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/books", status_code=status.HTTP_201_CREATED, response_model=BookOut)
def create_book(book: BookIn):
    """Création d'un livre (201, 409 si l'ID existe)."""
    try:
        # Vérifie si le livre existe déjà
        try:
            db.get_book(book.id)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="L'ID existe déjà")
        except LookupError:
            pass # C'est bon, il n'existe pas
            
        db.create_book(book.id, book.title, book.author, book.available_copies, book.rental_price)
        return book
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.put("/books/{book_id}", response_model=BookOut)
def update_book(book_id: int, book: BookUpdate):
    """Modification d'un livre (200, 404 si introuvable)."""
    try:
        db.update_book(book_id, book.title, book.author, book.available_copies, book.rental_price)
        return db.get_book(book_id)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    """Suppression d'un livre (204, 404 si introuvable)."""
    try:
        db.delete_book(book_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except LookupError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))