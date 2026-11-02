from abc import ABC, abstractmethod


class PartRepository(ABC):
    """Общий контракт для всех репозиториев Part."""

    @abstractmethod
    def get_by_id(self, id_: int):
        ...

    @abstractmethod
    def get_k_n_short_list(self, k: int, n: int) -> list:
        ...

    @abstractmethod
    def add(self, part) -> int:
        ...

    @abstractmethod
    def update(self, id_: int, part) -> None:
        ...

    @abstractmethod
    def delete(self, id_: int) -> None:
        ...

    @abstractmethod
    def get_count(self) -> int:
        ...
    @abstractmethod
    def add_with_id(self, id_: int, part) -> int:
        ...