"""Partie 1 - Version monolithique (COMPLETEE)

Completez tous les TODO. Tout doit rester dans ce seul fichier.
Lancer : python app.py  (apres docker compose up -d)
"""
import sys
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
)

# ---------- TODO 1 : connexion a Postgres via SQLAlchemy ----------
DATABASE_URL = "postgresql+psycopg2://library:library@localhost:5433/library" # Port 5433 comme configuré précédemment

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ---------- TODO 2 : table Book ----------
class Book(Base):
    __tablename__ = "books"
    # id (cle primaire, sans autoincrement comme demandé)
    id = Column(Integer, primary_key=True, autoincrement=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    available_copies = Column(Integer, nullable=False, default=0)
    rental_price = Column(Float, nullable=False, default=0.0)

    def to_dict(self):
        """Methode to_dict() qui renvoie un dictionnaire"""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "available_copies": self.available_copies,
            "rental_price": self.rental_price
        }

# Creer la table dans la base
Base.metadata.create_all(bind=engine)


# ---------- TODO 4 : validation ----------
def validate(book_id, title, author, copies, price):
    """Leve ValueError si : id <= 0, titre/auteur vides, copies < 0, prix < 0."""
    if book_id <= 0:
        raise ValueError("L'ID doit être supérieur à 0.")
    if not title.strip() or not author.strip():
        raise ValueError("Le titre et l'auteur ne peuvent pas être vides.")
    if copies < 0:
        raise ValueError("Le nombre d'exemplaires ne peut pas être négatif.")
    if price < 0:
        raise ValueError("Le prix ne peut pas être négatif.")


# ---------- TODO 3 : CRUD ----------
def create_book(book_id, title, author, copies, price):
    validate(book_id, title, author, copies, price)
    db = SessionLocal()
    try:
        existing_book = db.query(Book).filter(Book.id == book_id).first()
        if existing_book:
            raise ValueError(f"Un livre avec l'ID {book_id} existe déjà.")
        
        new_book = Book(id=book_id, title=title, author=author, available_copies=copies, rental_price=price)
        db.add(new_book)
        db.commit()
    finally:
        db.close()

def get_all_books():
    db = SessionLocal()
    try:
        books = db.query(Book).order_by(Book.id).all()
        return [book.to_dict() for book in books]
    finally:
        db.close()

def update_book(book_id, title, author, copies, price):
    validate(book_id, title, author, copies, price)
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise ValueError(f"Le livre avec l'ID {book_id} est introuvable.")
        
        book.title = title
        book.author = author
        book.available_copies = copies
        book.rental_price = price
        db.commit()
    finally:
        db.close()

def delete_book(book_id):
    if book_id <= 0:
        raise ValueError("L'ID doit être supérieur à 0.")
    db = SessionLocal()
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        if not book:
            raise ValueError(f"Le livre avec l'ID {book_id} est introuvable.")
        db.delete(book)
        db.commit()
    finally:
        db.close()


# ---------- TODO 5 : interface PyQt5 minimale ----------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BiblioTech - Monolithe")
        self.resize(700, 500)
        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "Titre", "Auteur", "Exemplaires", "Tarif"])
        layout.addWidget(self.table)

        self.id_in, self.title_in, self.author_in = QLineEdit(), QLineEdit(), QLineEdit()
        self.copies_in, self.price_in = QLineEdit(), QLineEdit()
        self.fields = [self.id_in, self.title_in, self.author_in, self.copies_in, self.price_in]
        form = QFormLayout()
        for label, widget in zip(["ID", "Titre", "Auteur", "Exemplaires", "Tarif"], self.fields):
            form.addRow(label, widget)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        for text, action in [("Ajouter", self.add), ("Modifier", self.edit),
                             ("Supprimer", self.remove), ("Rafraichir", self.refresh)]:
            btn = QPushButton(text)
            btn.clicked.connect(action)
            buttons.addWidget(btn)
        layout.addLayout(buttons)
        
        # BONUS : au clic sur une ligne, remplir le formulaire
        self.table.cellClicked.connect(self.fill_form_from_table)
        
        self.refresh()

    def read_form(self, require_all=True):
        """Lit les champs et convertit. Renvoie un tuple."""
        try:
            # Pour la suppression, on n'a besoin que de l'ID
            b_id = int(self.id_in.text())
            if not require_all:
                return (b_id, "", "", 0, 0.0)
                
            title = self.title_in.text()
            author = self.author_in.text()
            copies = int(self.copies_in.text())
            price = float(self.price_in.text())
            return (b_id, title, author, copies, price)
        except ValueError:
            raise ValueError("Veuillez vérifier que l'ID et les exemplaires sont des entiers, et le tarif un nombre.")

    def add(self):
        try:
            b_id, title, author, copies, price = self.read_form()
            create_book(b_id, title, author, copies, price)
            self.refresh()
            self.clear_form()
        except Exception as e:
            QMessageBox.warning(self, "Erreur d'ajout", str(e))

    def edit(self):
        try:
            b_id, title, author, copies, price = self.read_form()
            update_book(b_id, title, author, copies, price)
            self.refresh()
            self.clear_form()
        except Exception as e:
            QMessageBox.warning(self, "Erreur de modification", str(e))

    def remove(self):
        try:
            b_id, _, _, _, _ = self.read_form(require_all=False)
            delete_book(b_id)
            self.refresh()
            self.clear_form()
        except Exception as e:
            QMessageBox.warning(self, "Erreur de suppression", str(e))

    def refresh(self):
        try:
            books = get_all_books()
            self.table.setRowCount(len(books))
            for row_idx, book in enumerate(books):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(book["id"])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(book["title"]))
                self.table.setItem(row_idx, 2, QTableWidgetItem(book["author"]))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(book["available_copies"])))
                self.table.setItem(row_idx, 4, QTableWidgetItem(str(book["rental_price"])))
        except Exception as e:
            QMessageBox.warning(self, "Erreur de chargement", str(e))

    def fill_form_from_table(self, row, column):
        """BONUS : remplit le formulaire quand on clique sur une ligne"""
        self.id_in.setText(self.table.item(row, 0).text())
        self.title_in.setText(self.table.item(row, 1).text())
        self.author_in.setText(self.table.item(row, 2).text())
        self.copies_in.setText(self.table.item(row, 3).text())
        self.price_in.setText(self.table.item(row, 4).text())
        
    def clear_form(self):
        for field in self.fields:
            field.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
    