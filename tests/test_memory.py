"""Tests for short-term and long-term memory."""
import os
import tempfile
import pytest

from app.memory.short_term import ShortTermMemory
from app.memory.long_term import JsonLongTermMemory
from app.memory.memory_manager import MemoryManager


# ── ShortTermMemory ───────────────────────────────────────────────────────────

def test_short_term_add_and_retrieve():
    mem = ShortTermMemory()
    mem.add_message("user", "hello")
    mem.add_message("assistant", "hi there")
    history = mem.get_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["content"] == "hi there"


def test_short_term_max_messages():
    mem = ShortTermMemory()
    for i in range(25):
        mem.add_message("user", f"message {i}")
    assert len(mem.get_history()) == ShortTermMemory.MAX_MESSAGES


def test_short_term_clear():
    mem = ShortTermMemory()
    mem.add_message("user", "hello")
    mem.clear()
    assert mem.get_history() == []


# ── JsonLongTermMemory ────────────────────────────────────────────────────────

@pytest.fixture
def long_term():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    os.unlink(path)  # Remove so JsonLongTermMemory starts fresh (not an empty file)
    mem = JsonLongTermMemory(path=path)
    yield mem
    if os.path.exists(path):
        os.unlink(path)


def test_long_term_store_and_retrieve(long_term):
    long_term.store("budget_goal", "spend less than $500 on food")
    results = long_term.retrieve("budget")
    assert len(results) == 1
    assert "500" in results[0]


def test_long_term_retrieve_no_match(long_term):
    long_term.store("goal", "save for vacation")
    results = long_term.retrieve("budget")
    assert results == []


def test_long_term_clear(long_term):
    long_term.store("key", "value")
    long_term.clear()
    assert long_term.retrieve("key") == []


# ── MemoryManager ─────────────────────────────────────────────────────────────

@pytest.fixture
def manager(long_term):
    return MemoryManager(short_term=ShortTermMemory(), long_term=long_term)


def test_manager_add_conversation(manager):
    manager.add_conversation("user", "how much did I spend?")
    ctx = manager.get_context("spending")
    assert len(ctx["conversation"]) == 1


def test_manager_store_fact(manager):
    manager.store_fact("budget_goal", "keep food under $300")
    ctx = manager.get_context("budget")
    assert any("300" in f for f in ctx["facts"])


def test_manager_clear_all(manager):
    manager.add_conversation("user", "hello")
    manager.store_fact("key", "value")
    manager.clear_all()
    ctx = manager.get_context("anything")
    assert ctx["conversation"] == []
    assert ctx["facts"] == []
