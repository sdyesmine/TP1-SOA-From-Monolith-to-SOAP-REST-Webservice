import pytest
from db import validate_book


def test_valid_book():
    # Ne doit pas lever d'erreur
    validate_book(1, "Dune", "Frank Herbert", 5, 3.5)


def test_negative_stock():
    with pytest.raises(ValueError, match="stock"):
        validate_book(2, "Dune", "Frank Herbert", -1, 3.5)


def test_negative_price():
    with pytest.raises(ValueError, match="prix"):
        validate_book(3, "Dune", "Frank Herbert", 5, -1.0)


def test_invalid_id():
    with pytest.raises(ValueError, match="ID"):
        validate_book(-5, "Dune", "Frank Herbert", 5, 3.5)