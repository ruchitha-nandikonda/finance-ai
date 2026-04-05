"""User authentication with hashed passwords stored in SQLite."""
from __future__ import annotations

import hashlib
import os
import sqlite3
import uuid
from dataclasses import dataclass


@dataclass
class User:
    id: str
    username: str
    email: str


class AuthService:
    def __init__(self, db_path: str = "./data/transactions.db") -> None:
        self._db_path = db_path
        self._init_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _init_table(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

    def _hash(self, password: str) -> str:
        salt = "finance_agent_salt"
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

    def signup(self, username: str, email: str, password: str) -> User | str:
        """Returns User on success, or an error string."""
        if len(password) < 6:
            return "Password must be at least 6 characters."
        uid = str(uuid.uuid4())
        try:
            with self._connect() as conn:
                from datetime import date
                conn.execute(
                    "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                    (uid, username.strip(), email.strip().lower(), self._hash(password), date.today().isoformat()),
                )
            return User(id=uid, username=username, email=email)
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                return "Username already taken."
            return "Email already registered."

    def login(self, username: str, password: str) -> User | str:
        """Returns User on success, or an error string."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, email, password_hash FROM users WHERE username = ?",
                (username.strip(),),
            ).fetchone()
        if not row:
            return "Username not found."
        if row[3] != self._hash(password):
            return "Incorrect password."
        return User(id=row[0], username=row[1], email=row[2])

    def get_user(self, user_id: str) -> User | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, username, email FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        return User(id=row[0], username=row[1], email=row[2]) if row else None
