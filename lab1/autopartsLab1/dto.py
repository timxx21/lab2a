_DTO_TOKEN = object()


class ShortPartDTO:
    __slots__ = ("_fields", "_data")

    def __init__(self, fields, data, *, _token=None):
        if _token is not _DTO_TOKEN:
            raise TypeError("Создавайте DTO только через ShortPart.<method>(part).")
        self._fields = tuple(fields)
        self._data = dict(data)

    @property
    def fields(self):
        return self._fields

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def __contains__(self, key):
        return key in self._data

    def to_dict(self):
        return dict(self._data)

    def __repr__(self):
        pairs = ", ".join(f"{k}={v!r}" for k, v in self._data.items())
        return f"ShortPartDTO({pairs})"

    def __str__(self):
        pairs = ", ".join(f"{k}={v}" for k, v in self._data.items())
        return f"ShortPartDTO[{pairs}]"

    def __eq__(self, other):
        if not isinstance(other, ShortPartDTO):
            return NotImplemented
        return self._fields == other._fields and self._data == other._data

    def __hash__(self):
        return hash((self._fields, tuple(sorted(self._data.items()))))


def as_projection(fn):

    def wrapper(part):
        data = fn(part)
        return ShortPartDTO(tuple(data.keys()), data, _token=_DTO_TOKEN)
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper
