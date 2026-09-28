"""SQLite persistence for the Streamlit item manager."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Final


DATABASE_PATH: Final = Path(__file__).with_name("items.db")
SAMPLE_ITEMS: tuple[tuple[str, int, int], ...] = (
    ("礦泉水", 20, 15),
    ("咖啡", 45, 8),
    ("筆記本", 60, 12),
)


def _connect(db_path: str | Path = DATABASE_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def _validate_item(name: str, price: int, quantity: int) -> tuple[str, int, int]:
    cleaned_name = name.strip() if isinstance(name, str) else ""
    if not cleaned_name:
        raise ValueError("商品名稱不可空白")
    if isinstance(price, bool) or not isinstance(price, int) or price < 0:
        raise ValueError("價格必須是零或正整數")
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
        raise ValueError("數量必須是零或正整數")
    return cleaned_name, price, quantity


def initialize_database(db_path: str | Path = DATABASE_PATH) -> None:
    """Create the table and seed samples only when the table is first created."""
    connection = _connect(db_path)
    try:
        table_exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'items'"
        ).fetchone()

        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL CHECK (price >= 0),
                    quantity INTEGER NOT NULL CHECK (quantity >= 0)
                )
                """
            )
            if table_exists is None:
                connection.executemany(
                    "INSERT INTO items (name, price, quantity) VALUES (?, ?, ?)",
                    SAMPLE_ITEMS,
                )
    finally:
        connection.close()


def create_item(
    name: str,
    price: int,
    quantity: int,
    db_path: str | Path = DATABASE_PATH,
) -> int:
    name, price, quantity = _validate_item(name, price, quantity)
    connection = _connect(db_path)
    try:
        with connection:
            cursor = connection.execute(
                "INSERT INTO items (name, price, quantity) VALUES (?, ?, ?)",
                (name, price, quantity),
            )
            return int(cursor.lastrowid)
    finally:
        connection.close()


def list_items(db_path: str | Path = DATABASE_PATH) -> list[dict[str, int | str]]:
    connection = _connect(db_path)
    try:
        rows = connection.execute(
            "SELECT id, name, price, quantity FROM items ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def update_item(
    item_id: int,
    name: str,
    price: int,
    quantity: int,
    db_path: str | Path = DATABASE_PATH,
) -> bool:
    name, price, quantity = _validate_item(name, price, quantity)
    connection = _connect(db_path)
    try:
        with connection:
            cursor = connection.execute(
                """
                UPDATE items
                SET name = ?, price = ?, quantity = ?
                WHERE id = ?
                """,
                (name, price, quantity, item_id),
            )
            return cursor.rowcount > 0
    finally:
        connection.close()


def delete_item(item_id: int, db_path: str | Path = DATABASE_PATH) -> bool:
    connection = _connect(db_path)
    try:
        with connection:
            cursor = connection.execute("DELETE FROM items WHERE id = ?", (item_id,))
            return cursor.rowcount > 0
    finally:
        connection.close()


def reset_sample_items(db_path: str | Path = DATABASE_PATH) -> None:
    """Replace every item with the three samples in one atomic transaction."""
    connection = _connect(db_path)
    try:
        with connection:
            connection.execute("DELETE FROM items")
            connection.execute("DELETE FROM sqlite_sequence WHERE name = ?", ("items",))
            connection.executemany(
                "INSERT INTO items (name, price, quantity) VALUES (?, ?, ?)",
                SAMPLE_ITEMS,
            )
    finally:
        connection.close()
