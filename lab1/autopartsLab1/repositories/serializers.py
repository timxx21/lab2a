"""в принципе тот же парсинг что и был в первой лабе"""

import json
from abc import ABC, abstractmethod

import yaml


class Serializer(ABC):
    """превращает список dict в текст и обратно."""

    @abstractmethod
    def dump(self, records: list[dict]) -> str:
        ...

    @abstractmethod
    def load(self, text: str) -> list[dict]:
        ...


class SerializerRegistry:
    """реестр сериализаторов по имени формата"""

    _serializers: dict[str, type[Serializer]] = {}

    @classmethod
    def register(cls, name: str):
        key = name.lower()

        def decorator(klass):
            if key in cls._serializers:
                raise ValueError(f"Сериализатор '{key}' уже зарегистрирован")
            cls._serializers[key] = klass
            return klass

        return decorator

    @classmethod
    def get(cls, name: str) -> Serializer:
        key = name.lower()
        if key not in cls._serializers:
            raise ValueError(
                f"Неизвестный формат '{name}'. "
                f"Доступные: {', '.join(sorted(cls._serializers))}"
            )
        return cls._serializers[key]()

    @classmethod
    def available(cls) -> list[str]:
        return sorted(cls._serializers)


@SerializerRegistry.register("json")
class JsonSerializer(Serializer):
    def dump(self, records: list[dict]) -> str:
        return json.dumps(records, ensure_ascii=False, indent=2)

    def load(self, text: str) -> list[dict]:
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("JSON должен содержать список объектов")
        return data


@SerializerRegistry.register("yaml")
class YamlSerializer(Serializer):
    def dump(self, records: list[dict]) -> str:
        return yaml.safe_dump(records, allow_unicode=True, sort_keys=False)

    def load(self, text: str) -> list[dict]:
        data = yaml.safe_load(text)
        if data is None:
            return []
        if not isinstance(data, list):
            raise ValueError("YAML должен содержать список объектов")
        return data