"""Couche donnees (SQLAlchemy) - COMPLETEE."""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://library:library@localhost:5433/library")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    available_copies = Column(Integer, nullable=False, default=0)
    rental_price = Column(Float, nullable=False, default=0.0)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "available_copies": self.available_copies,
            "rental_price": self.rental_price
        }


def init_db():
    Base.metadata.create_all(bind=engine)


def validate_book(book_id, title, author, copies, price):
    if book_id <= 0:
        raise ValueError("L'ID doit être strictement positif.")
    if copies < 0:
        raise ValueError("Le stock ne peut pas être négatif.")
    if price < 0:
        raise ValueError("Le prix ne peut pas être négatif.")
    if not title or not title.strip():
        raise ValueError("Le titre ne peut pas être vide.")
    if not author or not author.strip():
        raise ValueError("L'auteur ne peut pas être vide.")


def create_book(book_id, title, author, copies, price):
    validate_book(book_id, title, author, copies, price)
    db = SessionLocal()
    try:
        if db.query(Book).filter(Book.id == book_id).first():
            raise ValueError(f"Le livre avec l'ID {book_id} existe déjà.")
        new_book = Book(id=book_id, title=title, author=author, 
                        available_copies=copies, rental_price=price)
        db.add(new_book)
        db.commit()
    finally:
        db.close()


def get_book(book_id):
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise LookupError(f"Le livre avec l'ID {book_id} est introuvable.")
        return book.to_dict()
    finally:
        db.close()


def update_book(book_id, title, author, copies, price):
    validate_book(book_id, title, author, copies, price)
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise LookupError(f"Le livre avec l'ID {book_id} est introuvable.")
        book.title = title
        book.author = author
        book.available_copies = copies
        book.rental_price = price
        db.commit()
    finally:
        db.close()


def delete_book(book_id):
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise LookupError(f"Le livre avec l'ID {book_id} est introuvable.")
        db.delete(book)
        db.commit()
    finally:
        db.close()