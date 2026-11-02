"""Публичный API пакета autopartsLab1."""

# --- ЛР1 ---
from .part import Part
from .dto import ShortPartDTO
from .observer import LiveProjection, Refresher
from .projections import ShortPart
from .parsers import PartParser
from .partmanager import PartManager

# --- ЛР2 ---
from .repositories import (
    PartRepository,
    Serializer,
    SerializerRegistry,
    JsonSerializer,
    YamlSerializer,
    PartRepFile,
    PartRepJSON,
    PartRepYAML,
    DBConnection,
    PartRepDB,
    PartRepDBAdapter,
    PartRepositoryDecorator,
    FilterSortDecorator,
)

__all__ = [
    # ЛР1
    "Part", "ShortPartDTO", "LiveProjection", "Refresher",
    "ShortPart", "PartParser", "PartManager",
    # ЛР2
    "PartRepository", "Serializer", "SerializerRegistry",
    "JsonSerializer", "YamlSerializer",
    "PartRepFile", "PartRepJSON", "PartRepYAML",
    "DBConnection", "PartRepDB", "PartRepDBAdapter",
    "PartRepositoryDecorator", "FilterSortDecorator",
]

__version__ = "0.2.0"