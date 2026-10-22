import os
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://library:library@localhost:5432/library")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    available_copies = Column(Integer, nullable=False, default=0)
    rental_price = Column(Float, nullable=False, default=0.0)

def init_db():
    # Crée les tables dans la base de données
    Base.metadata.create_all(bind=engine)

def validate_book(book_id, title, author, copies, price):
    if book_id <= 0 or copies < 0 or price < 0 or not title or not author:
        raise ValueError("Données invalides")

def create_book(book_id, title, author, copies, price):
    validate_book(book_id, title, author, copies, price)
    session = SessionLocal()
    if session.query(Book).filter(Book.id == book_id).first():
        session.close()
        raise ValueError("Le livre existe déjà")
    
    new_book = Book(id=book_id, title=title, author=author, available_copies=copies, rental_price=price)
    session.add(new_book)
    session.commit()
    session.close()

def get_book(book_id):
    session = SessionLocal()
    book = session.query(Book).filter(Book.id == book_id).first()
    session.close()
    if not book:
        raise LookupError("Livre introuvable")
    return {"id": book.id, "title": book.title, "author": book.author, "available_copies": book.available_copies, "rental_price": book.rental_price}

def update_book(book_id, title, author, copies, price):
    validate_book(book_id, title, author, copies, price)
    session = SessionLocal()
    book = session.query(Book).filter(Book.id == book_id).first()
    if not book:
        session.close()
        raise LookupError("Livre introuvable")
    
    book.title = title
    book.author = author
    book.available_copies = copies
    book.rental_price = price
    session.commit()
    session.close()

def delete_book(book_id):
    session = SessionLocal()
    book = session.query(Book).filter(Book.id == book_id).first()
    if not book:
        session.close()
        raise LookupError("Livre introuvable")
    
    session.delete(book)
    session.commit()
    session.close()