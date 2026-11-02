"""Adapter: превращает PartRepDB в PartRepository."""

from ..part import Part
from ..dto import ShortPartDTO, _DTO_TOKEN
from .base import PartRepository
from .db_rep import PartRepDB


class PartRepDBAdapter(PartRepository):
    """
    Адаптер: dict в Part.
    Наследует PartRepository делегирует PartRepDB.
    """

    def __init__(self, db_rep: PartRepDB):
        self._db = db_rep

    # ---------- перевод ----------

    @staticmethod
    def _row_to_part(row: dict) -> Part:
        return Part.from_dict({
            "article": row["article"],
            "name": row["name"],
            "price": row["price"],
            "manufacturer": row["manufacturer"],
            "weight": row["weight"],
            "warranty_months": row["warranty_months"],
        })

    @staticmethod
    def _row_to_dto(row: dict) -> ShortPartDTO:
        data = {
            "id": row["id"],
            "article": row["article"],
            "name": row["name"],
            "price": float(row["price"]),
        }
        return ShortPartDTO(tuple(data.keys()), data, _token=_DTO_TOKEN)

    @staticmethod
    def _part_to_row(part: Part) -> dict:
        return {
            "article": part.article,
            "name": part.name,
            "price": part.price,
            "manufacturer": part.manufacturer,
            "weight": part.weight,
            "warranty_months": part.warranty_months,
        }

    # ---------- PartRepository ----------

    def add_with_id(self, id_: int, part: Part) -> int:
        return self._db.insert_with_id(id_, self._part_to_row(part))
    
    def get_by_id(self, id_: int) -> Part:
        row = self._db.select_by_id(id_)
        if row is None:
            raise KeyError(f"Part with id={id_} not found")
        return self._row_to_part(row)

    def get_k_n_short_list(self, k: int, n: int) -> list[ShortPartDTO]:
        if k <= 0 or n <= 0:
            raise ValueError("k и n должны быть положительными")
        rows = self._db.select_page(k, (n - 1) * k)
        return [self._row_to_dto(r) for r in rows]

    def add(self, part: Part) -> int:
        return self._db.insert(self._part_to_row(part))

    def update(self, id_: int, part: Part) -> None:
        self._db.update_record(id_, self._part_to_row(part))

    def delete(self, id_: int) -> None:
        self._db.delete_record(id_)

    def get_count(self) -> int:
        return self._db.count()

    def sort_by(self, field: str) -> list[Part]:
        rows = self._db.sort_by(field)
        return [self._row_to_part(r) for r in rows]