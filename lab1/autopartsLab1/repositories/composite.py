from .base import PartRepository


class CompositePartRepository(PartRepository):
    """
    Объединяет несколько репозиториев.
    Чтение идет из primary.
    Запись идет во все репозитории (primary + replicas).
    """

    def __init__(self, primary: PartRepository, *replicas: PartRepository):
        self._primary = primary
        self._replicas = list(replicas)

    # --- Чтение (только из primary) ---
    def get_by_id(self, id_: int):
        return self._primary.get_by_id(id_)

    def get_k_n_short_list(self, k: int, n: int):
        return self._primary.get_k_n_short_list(k, n)

    def get_count(self) -> int:
        return self._primary.get_count()

    # --- Запись (во все) ---
    def add(self, part) -> int:
        # 1. Добавляем в БД (она генерирует ID)
        id_ = self._primary.add(part)
        # 2. Синхронизируем с остальными
        self._sync_add(id_, part)
        return id_

    def add_with_id(self, id_: int, part) -> int:
        id_ = self._primary.add_with_id(id_, part)
        self._sync_add(id_, part)
        return id_

    def update(self, id_: int, part) -> None:
        # 1. Обновляем в БД
        self._primary.update(id_, part)
        # 2. Обновляем в файлах
        for rep in self._replicas:
            try:
                rep.update(id_, part)
            except KeyError:
                rep.add_with_id(id_, part) # Если в файле не было — создаем

    def delete(self, id_: int) -> None:
        # 1. Удаляем из БД
        self._primary.delete(id_)
        # 2. Удаляем из файлов
        for rep in self._replicas:
            try:
                rep.delete(id_)
            except KeyError:
                pass

    # --- Служебные методы ---
    def _sync_add(self, id_: int, part) -> None:
        for rep in self._replicas:
            try:
                rep.add_with_id(id_, part)
            except ValueError:
                pass # Уже существует

    def flush(self) -> None:
        """Сохранить данные на диск (вызвать write у файловых репо)."""
        for rep in [self._primary] + self._replicas:
            if hasattr(rep, "write"):
                rep.write()

    def resync(self) -> None:
        """
        Полностью перезаписывает реплики (файлы) данными из primary (БД).
        Удаляет из файлов всё, чего нет в БД.
        """
        total = self._primary.get_count()
        if total == 0:
            primary_items = []
        else:
            dtos = self._primary.get_k_n_short_list(total, 1)
            primary_items = [(dto["id"], self._primary.get_by_id(dto["id"])) for dto in dtos]

        for rep in self._replicas:
            current_count = rep.get_count()
            if current_count > 0:
                current_dtos = rep.get_k_n_short_list(current_count, 1)
                for dto in current_dtos:
                    rep.delete(dto["id"])

            for id_, part in primary_items:
                rep.add_with_id(id_, part)