
from ..dto import ShortPartDTO
from .base import PartRepository


class PartRepositoryDecorator(PartRepository):

    def __init__(self, wrapped: PartRepository):
        self._wrapped = wrapped

    def get_by_id(self, id_: int):
        return self._wrapped.get_by_id(id_)

    def get_k_n_short_list(self, k: int, n: int):
        return self._wrapped.get_k_n_short_list(k, n)

    def add(self, part) -> int:
        return self._wrapped.add(part)

    def update(self, id_: int, part) -> None:
        return self._wrapped.update(id_, part)

    def delete(self, id_: int) -> None:
        return self._wrapped.delete(id_)

    def get_count(self) -> int:
        return self._wrapped.get_count()

    def add_with_id(self, id_: int, part) -> int:
        return self._wrapped.add_with_id(id_, part)

class FilterSortDecorator(PartRepositoryDecorator):
    """
    добавляет фильтр и сортировку в
    get_k_n_short_list и get_count.
    Работает поверх любого PartRepository.
    """

    def __init__(self, wrapped: PartRepository,
                 filter_fn=None, sort_key=None):
        super().__init__(wrapped)
        self._filter = filter_fn
        self._sort_key = sort_key

    def _fetch_all(self) -> list[ShortPartDTO]:
        total = self._wrapped.get_count()
        if total == 0:
            return []
        return self._wrapped.get_k_n_short_list(total, 1)

    def _apply(self) -> list[ShortPartDTO]:
        items = self._fetch_all()
        if self._filter is not None:
            items = [d for d in items if self._filter(d)]
        if self._sort_key is not None:
            items = sorted(items, key=lambda d: d[self._sort_key])
        return items

    def get_k_n_short_list(self, k: int, n: int) -> list[ShortPartDTO]:
        if k <= 0 or n <= 0:
            raise ValueError("k и n должны быть положительными")
        items = self._apply()
        start = (n - 1) * k
        return items[start:start + k]

    def get_count(self) -> int:
        return len(self._apply())