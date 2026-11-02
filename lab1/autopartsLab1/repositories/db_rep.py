"""Репозиторий Part в БД: только SQL-запросы, возвращает dict."""

from .db_connection import DBConnection


class PartRepDB:
    """
    Работа с таблицей parts в MySQL.
    Возвращает dict, ничего не знает про Part и DTO.
    """

    def __init__(self, connection: DBConnection):
        self._conn = connection

    def select_by_id(self, id_: int) -> dict | None:
        return self._conn.fetch_one(
            "SELECT id, article, name, price, manufacturer, "
            "weight, warranty_months "
            "FROM parts WHERE id = %s",
            (id_,),
        )

    def select_page(self, limit: int, offset: int) -> list[dict]:
        return self._conn.fetch_all(
            "SELECT id, article, name, price, manufacturer, "
            "weight, warranty_months "
            "FROM parts ORDER BY id LIMIT %s OFFSET %s",
            (limit, offset),
        )

    def insert(self, record: dict) -> int:
        return self._conn.execute_commit(
            "INSERT INTO parts "
            "(article, name, price, manufacturer, weight, warranty_months) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (record["article"], record["name"], record["price"],
             record["manufacturer"], record["weight"],
             record["warranty_months"]),
        )

    def update_record(self, id_: int, record: dict) -> None:
        self._conn.execute_commit(
            "UPDATE parts SET article=%s, name=%s, price=%s, "
            "manufacturer=%s, weight=%s, warranty_months=%s "
            "WHERE id=%s",
            (record["article"], record["name"], record["price"],
             record["manufacturer"], record["weight"],
             record["warranty_months"], id_),
        )
    def insert_with_id(self, id_: int, record: dict) -> int:
        return self._conn.execute_commit(
            "INSERT INTO parts "
            "(id, article, name, price, manufacturer, weight, warranty_months) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (id_, record["article"], record["name"], record["price"],
             record["manufacturer"], record["weight"],
             record["warranty_months"]),
        )

    def delete_record(self, id_: int) -> None:
        self._conn.execute_commit(
            "DELETE FROM parts WHERE id=%s", (id_,),
        )

    def count(self) -> int:
        row = self._conn.fetch_one("SELECT COUNT(*) AS cnt FROM parts")
        return int(row["cnt"])

    _SORTABLE = {"article", "name", "price",
                 "manufacturer", "weight", "warranty_months"}

    def sort_by(self, field: str) -> list[dict]:
        if field not in self._SORTABLE:
            raise ValueError(f"Сортировка по '{field}' невозможна")
        return self._conn.fetch_all(
            f"SELECT id, article, name, price, manufacturer, "
            f"weight, warranty_months FROM parts ORDER BY {field}"
        )