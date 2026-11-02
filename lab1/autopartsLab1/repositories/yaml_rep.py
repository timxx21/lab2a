"""то же самое"""

from .file_rep import PartRepFile
from .serializers import SerializerRegistry


class PartRepYAML(PartRepFile):
    def __init__(self, path: str):
        super().__init__(path, SerializerRegistry.get("yaml"))