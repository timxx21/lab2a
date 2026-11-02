from .part import Part
from .observer import Refresher

class PartManager:
    def __init__(self, refresher: Refresher):
        self._parts = {}
        self._refresher = refresher

    def add(self, part: Part):
        self._parts[part.article] = part

    def remove(self, part: Part):
        self._parts.pop(part.article, None)
        part.detach_all()          # отписать наблюдателей
        self._refresher.remove_part(part)   # убрать из менеджера

    def get(self, article: str) -> Part:
        return self._parts[article]

    def __len__(self):
        return len(self._parts)