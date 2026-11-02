"""обертка обращающаяся к сериалайзеру"""

from .file_rep import PartRepFile
from .serializers import SerializerRegistry


class PartRepJSON(PartRepFile):
    def __init__(self, path: str):
        super().__init__(path, SerializerRegistry.get("json"))