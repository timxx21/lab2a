import csv
import io
import json

from .part import Part

class PartParser:
    _parsers:dict = {}
    @classmethod
    def register(cls, name: {str}):
        key = name.lower()
        def decorator(func):
            if key in cls._parsers:
                raise ValueError(f"Формат '{key}' уже есть")
            cls._parsers[key] = func
            return func
        return decorator

    @classmethod
    def parse(cls, data, fmt: str) -> "Part":
        key = fmt.lower()
        if key not in cls._parsers:
            raise ValueError(
                f"Неизвестный формат '{fmt}'"
                f"Доступные форматы : {', '.join(cls.available())}")
        normalized = cls._parsers[key](data)
        return Part.from_dict(normalized)

    @classmethod
    def available(cls) -> list:
        return sorted(cls._parsers)


    # сами парсеры (теперь мы можем читать словари джсон строки и цсв)
@PartParser.register("dict")
def _parse_dict(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Ожидался dict")
    return dict(data)


@PartParser.register("json")
def _parse_json(data: str) -> dict:
    if not isinstance(data, str):
        raise ValueError("Ожидалась JSON-строка")
    return json.loads(data)


@PartParser.register("string")
def _parse_string(data: str) -> dict:
    if not isinstance(data, str):
        raise ValueError("Ожидалась строка")
    parts = [x.strip() for x in data.split(";")]
    if len(parts) != 6:
        raise ValueError("Ожидается 6 полей через ';'")
    return dict(zip(
        ("article", "name", "price", "manufacturer", "weight", "warranty_months"),
        parts,
    ))


@PartParser.register("csv")
def _parse_csv(data: str) -> dict:
    if not isinstance(data, str):
        raise ValueError("Ожидалась CSV-строка")
    rows = [r for r in csv.reader(io.StringIO(data.strip())) if r]
    if not rows:
        raise ValueError("Пустой CSV")

    header = [c.strip().lower() for c in rows[0]]
    expected = ["article", "name", "price",
                "manufacturer", "weight", "warranty_months"]

    if header == expected:
        if len(rows) < 2:
            raise ValueError("CSV с заголовком, но без данных")
        cols, row = header, rows[1]
    else:
        cols, row = expected, rows[0]

    if len(row) != len(cols):
        raise ValueError(f"Ожидается {len(cols)} колонок, получено {len(row)}")
    return {c: v.strip() for c, v in zip(cols, row)}


#если нам нужен новый формат то мы расширяем

"""
@PartParser.register("pipe")
def _parse_pipe(data: str) -> dict:
    parts = [x.strip() for x in data.split("|")]
    if len(parts) != 6:
        raise ValueError("Ожидается 6 полей через '|'")
    return dict(zip(
        ("article", "name", "price", "manufacturer", "weight", "warranty_months"),
        parts,
    ))
"""
