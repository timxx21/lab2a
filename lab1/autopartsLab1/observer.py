from .dto import ShortPartDTO, _DTO_TOKEN

class LiveProjection:

    def __init__(self, part, producer):
        self._part = part
        self._producer = producer
        self._dto = self._build()
        part.attach(self)

    @property
    def is_alive(self) -> bool:
        return self._part is not None

    def _build(self) -> ShortPartDTO:
        data = self._producer(self._part)
        return ShortPartDTO(tuple(data.keys()), data, _token=_DTO_TOKEN)

    def update(self, subject):
        if self._part is None:
            return
        if subject is self._part:
            self._dto = self._build()

    def close(self):
        if self._part is not None:
            self._part.detach(self)
            self._part = None

# доступ к дто

    @property
    def value(self):
        return self._dto, "Обьект удалён из базы"


    @property
    def fields(self):
        return self._dto.fields

    def to_dict(self):
        return self._dto.to_dict()

    def get(self, key, default=None):
        return self._dto.get(key, default)

    def __getitem__(self, key):
        return self._dto[key]

    def __contains__(self, key):
        return key in self._dto

    def __eq__(self, other):
        if isinstance(other, LiveProjection):
            other = other._dto
        return self._dto == other

    def __str__(self):
        return str(self._dto)

    # отписка

    def close(self):
        if self._part is not None:
            self._part.detach(self)
            self._part = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class Refresher:

    def __init__(self):
        self._live = []

    def _purge_dead(self):
        self._live = [lv for lv in self._live if lv.is_alive]

    def make(self, part, producer) -> LiveProjection:
        self._purge_dead()
        lv = LiveProjection(part, producer)
        self._live.append(lv)
        return lv

    def refresh_all(self):
        self._purge_dead()
        for lv in list(self._live):
            if lv._part is not None:
                lv.update(lv._part)

    def refresh_part(self, part):
        self._purge_dead()
        for lv in list(self._live):
            if lv._part is part:
                lv.update(part)

    def remove_part(self, part):
       #убрать проекции конкретного парт
        for lv in list(self._live):
            if lv._part is part:
                lv.close()
        self._purge_dead()

    def close(self):
        for lv in list(self._live):
            lv.close()
        self._live.clear()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def __len__(self):
        return len(self._live)

