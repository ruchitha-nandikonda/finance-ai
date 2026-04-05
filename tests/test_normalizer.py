"""Tests for the smart bank CSV normalizer."""
import pytest
from app.services.csv_normalizer import BankCSVNormalizer


@pytest.fixture
def normalizer():
    return BankCSVNormalizer()


def test_generic_csv(normalizer):
    csv = "date,description,amount\n2026-01-15,Starbucks,6.75\n2026-01-16,Netflix,15.99"
    result = normalizer.normalize(csv)
    assert len(result.rows) == 2
    assert result.rows[0]["amount"] == 6.75
    assert result.rows[1]["description"] == "Netflix"
    assert result.bank == "Generic"


def test_chase_format(normalizer):
    csv = "Transaction Date,Post Date,Description,Category,Type,Amount,Memo\n01/15/2026,01/16/2026,Uber,,,-34.50,"
    result = normalizer.normalize(csv)
    assert len(result.rows) == 1
    assert result.rows[0]["amount"] == 34.50
    assert result.bank == "Chase"


def test_capital_one_format(normalizer):
    csv = "Transaction Date,Posted Date,Card No.,Description,Category,Debit,Credit\n2026-01-15,2026-01-16,1234,Amazon,,45.00,"
    result = normalizer.normalize(csv)
    assert len(result.rows) == 1
    assert result.rows[0]["amount"] == 45.00
    assert result.bank == "Capital One"


def test_strips_currency_symbols(normalizer):
    csv = "date,description,amount\n2026-01-15,Target,$89.30"
    result = normalizer.normalize(csv)
    assert result.rows[0]["amount"] == 89.30


def test_various_date_formats(normalizer):
    csv = "date,description,amount\n01/15/2026,Starbucks,6.75"
    result = normalizer.normalize(csv)
    assert result.rows[0]["date"].year == 2026
    assert result.rows[0]["date"].month == 1
    assert result.rows[0]["date"].day == 15


def test_skips_zero_amount_rows(normalizer):
    csv = "date,description,amount\n2026-01-15,Starbucks,6.75\n2026-01-16,Transfer,0"
    result = normalizer.normalize(csv)
    assert len(result.rows) == 1
    assert result.skipped == 1


def test_missing_date_column_raises(normalizer):
    csv = "description,amount\nStarbucks,6.75"
    with pytest.raises(ValueError, match="date column"):
        normalizer.normalize(csv)


def test_missing_description_column_raises(normalizer):
    csv = "date,amount\n2026-01-15,6.75"
    with pytest.raises(ValueError, match="description column"):
        normalizer.normalize(csv)
