"""Tests for recurring transaction detection."""
import os
import tempfile
import sqlite3
import pytest

from app.services.recurring_detector import RecurringDetector


@pytest.fixture
def db_with_transactions():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE transactions (
            id TEXT PRIMARY KEY, date TEXT, description TEXT,
            amount REAL, category TEXT, source TEXT
        )
    """)
    rows = [
        ("1", "2026-01-15", "Netflix", 15.99, "entertainment", "csv"),
        ("2", "2026-02-15", "Netflix", 15.99, "entertainment", "csv"),
        ("3", "2026-03-15", "Netflix", 15.99, "entertainment", "csv"),
        ("4", "2026-01-01", "Spotify", 9.99, "entertainment", "csv"),
        ("5", "2026-02-01", "Spotify", 9.99, "entertainment", "csv"),
        ("6", "2026-01-10", "Grocery Store", 87.50, "food", "csv"),
        ("7", "2026-01-20", "Grocery Store", 200.00, "food", "csv"),  # High variance — not recurring
    ]
    conn.executemany("INSERT INTO transactions VALUES (?,?,?,?,?,?)", rows)
    conn.commit()
    conn.close()

    yield db_path
    os.unlink(db_path)


def test_detects_netflix(db_with_transactions):
    detector = RecurringDetector(db_path=db_with_transactions)
    results = detector.detect()
    descriptions = [r.description for r in results]
    assert any("Netflix" in d for d in descriptions)


def test_detects_spotify(db_with_transactions):
    detector = RecurringDetector(db_path=db_with_transactions)
    results = detector.detect()
    descriptions = [r.description for r in results]
    assert any("Spotify" in d for d in descriptions)


def test_does_not_flag_high_variance(db_with_transactions):
    detector = RecurringDetector(db_path=db_with_transactions)
    results = detector.detect()
    # Grocery Store has 37% variance — should not be flagged
    descriptions = [r.description for r in results]
    assert not any("Grocery" in d for d in descriptions)


def test_occurrences_count(db_with_transactions):
    detector = RecurringDetector(db_path=db_with_transactions)
    results = detector.detect()
    netflix = next((r for r in results if "Netflix" in r.description), None)
    assert netflix is not None
    assert netflix.occurrences == 3
    assert netflix.average_amount == 15.99
