"""базовый файловый репозиторий вся логика формат через делегацию."""

import os

from ..part import Part
from ..dto import ShortPartDTO, _DTO_TOKEN
from .base import PartRepository
from .serializers import Serializer


class PartRepFile(PartRepository):
    """
    РЕПОЗИТОРИЙ PART В ФАЙЛЕ
    Формат джсон или ямл задается сериалайзером.
    """

    def __init__(self, path: str, serializer: Serializer):
        self._path = path
        self._serializer = serializer
        self._items: dict[int, Part] = {}
        self._next_id = 1
        self.read()

    @property
    def path(self) -> str:
        return self._path

    # ---------- Part в dict ----------

    @staticmethod
    def _part_to_dict(part: Part, id_: int) -> dict:
        return {
            "id": id_,
            "article": part.article,
            "name": part.name,
            "price": part.price,
            "manufacturer": part.manufacturer,
            "weight": part.weight,
            "warranty_months": part.warranty_months,
        }

    @staticmethod
    def _dict_to_part(row: dict) -> Part:
        return Part.from_dict({
            k: v for k, v in row.items() if k != "id"
        })

    # ---------- файл ----------

    def read(self) -> None:
        if not os.path.exists(self._path):
            self._items = {}
            self._next_id = 1
            return

        with open(self._path, encoding="utf-8") as f:
            text = f.read()

        if not text.strip():
            self._items = {}
            self._next_id = 1
            return

        rows = self._serializer.load(text)
        self._items = {}
        max_id = 0
        for row in rows:
            id_ = int(row["id"])
            self._items[id_] = self._dict_to_part(row)
            max_id = max(max_id, id_)
        self._next_id = max_id + 1

    def write(self) -> None:
        records = [
            self._part_to_dict(part, id_)
            for id_, part in sorted(self._items.items())
        ]
        text = self._serializer.dump(records)
        with open(self._path, "w", encoding="utf-8") as f:
            f.write(text)

    # ---------- PartRepository ----------

    def add_with_id(self, id_: int, part: Part) -> int:
        if id_ in self._items:
            raise ValueError(f"Part with id={id_} уже существует")

        # Проверка на дубликат артикула
        for existing in self._items.values():
            if existing.article == part.article:
                raise ValueError(f"Part with article={part.article} уже существует")

        self._items[id_] = part
        self._next_id = max(self._next_id, id_ + 1)
        return id_

    def get_by_id(self, id_: int) -> Part:
        if id_ not in self._items:
            raise KeyError(f"Part with id={id_} not found")
        return self._items[id_]

    def get_k_n_short_list(self, k: int, n: int) -> list[ShortPartDTO]:
        if k <= 0 or n <= 0:
            raise ValueError("k и n должны быть положительными")
        ids = sorted(self._items)
        start = (n - 1) * k
        chunk = ids[start:start + k]
        result = []
        for id_ in chunk:
            part = self._items[id_]
            data = {
                "id": id_,
                "article": part.article,
                "name": part.name,
                "price": part.price,
            }
            result.append(
                ShortPartDTO(tuple(data.keys()), data, _token=_DTO_TOKEN)
            )
        return result

    def add(self, part: Part) -> int:
        for existing in self._items.values():
            if existing.article == part.article:
                raise ValueError(
                    f"Деталь с артикулом ={part.article} уже существует"
                )
        id_ = self._next_id
        self._items[id_] = part
        self._next_id += 1
        return id_

    def update(self, id_: int, part: Part) -> None:
        if id_ not in self._items:
            raise KeyError(f"а где {id_} ")
        self._items[id_] = part

    def delete(self, id_: int) -> None:
        if id_ not in self._items:
            raise KeyError(f"а где {id_} ")
        del self._items[id_]

    def get_count(self) -> int:
        return len(self._items)

    # ---------- сортировка ----------

    _SORTABLE = {"article", "name", "price",
                 "manufacturer", "weight", "warranty_months"}

    def sort_by(self, field: str) -> None:
        if field not in self._SORTABLE:
            raise ValueError(f"Сортировка по '{field}' невозможна")
        self._items = dict(sorted(
            self._items.items(),
            key=lambda kv: getattr(kv[1], field),
        ))