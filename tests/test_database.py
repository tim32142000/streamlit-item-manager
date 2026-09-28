import sqlite3

import pytest

import database


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test_items.db"
    database.initialize_database(path)
    return path


def test_initialize_creates_schema_and_samples(db_path):
    connection = sqlite3.connect(db_path)
    try:
        columns = connection.execute("PRAGMA table_info(items)").fetchall()
        schema = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'items'"
        ).fetchone()[0]
    finally:
        connection.close()

    assert [column[1] for column in columns] == ["id", "name", "price", "quantity"]
    assert "CHECK (price >= 0)" in schema
    assert "CHECK (quantity >= 0)" in schema
    assert [(item["name"], item["price"], item["quantity"]) for item in database.list_items(db_path)] == list(
        database.SAMPLE_ITEMS
    )


def test_repeated_initialize_does_not_duplicate_samples(db_path):
    database.initialize_database(db_path)
    assert len(database.list_items(db_path)) == 3


def test_create_read_update_and_delete(db_path):
    item_id = database.create_item("  原子筆  ", 25, 4, db_path)
    created = next(item for item in database.list_items(db_path) if item["id"] == item_id)
    assert created == {"id": item_id, "name": "原子筆", "price": 25, "quantity": 4}

    assert database.update_item(item_id, "藍色原子筆", 30, 6, db_path) is True
    updated = next(item for item in database.list_items(db_path) if item["id"] == item_id)
    assert updated == {"id": item_id, "name": "藍色原子筆", "price": 30, "quantity": 6}

    assert database.delete_item(item_id, db_path) is True
    assert all(item["id"] != item_id for item in database.list_items(db_path))


@pytest.mark.parametrize(
    ("name", "price", "quantity", "message"),
    [
        ("  ", 10, 1, "商品名稱不可空白"),
        ("商品", -1, 1, "價格必須是零或正整數"),
        ("商品", 1, -1, "數量必須是零或正整數"),
    ],
)
def test_invalid_items_are_rejected(db_path, name, price, quantity, message):
    with pytest.raises(ValueError, match=message):
        database.create_item(name, price, quantity, db_path)


def test_empty_database_stays_empty_after_initialize(db_path):
    for item in database.list_items(db_path):
        database.delete_item(item["id"], db_path)

    database.initialize_database(db_path)
    assert database.list_items(db_path) == []


def test_reset_replaces_all_items_and_restarts_ids(db_path):
    database.create_item("自訂商品", 99, 1, db_path)

    database.reset_sample_items(db_path)

    items = database.list_items(db_path)
    assert [item["id"] for item in items] == [1, 2, 3]
    assert [(item["name"], item["price"], item["quantity"]) for item in items] == list(
        database.SAMPLE_ITEMS
    )


def test_failed_reset_rolls_back_original_data(db_path, monkeypatch):
    original_items = database.list_items(db_path)
    monkeypatch.setattr(
        database,
        "SAMPLE_ITEMS",
        (("暫存商品", 1, 1), ("無效商品", -1, 1)),
    )

    with pytest.raises(sqlite3.IntegrityError):
        database.reset_sample_items(db_path)

    assert database.list_items(db_path) == original_items


def test_update_and_delete_return_false_for_missing_item(db_path):
    assert database.update_item(9999, "不存在", 1, 1, db_path) is False
    assert database.delete_item(9999, db_path) is False
