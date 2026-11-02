from .dto import ShortPartDTO, _DTO_TOKEN
from .observer import LiveProjection


def _to_snapshot(data: dict) -> ShortPartDTO:
    return ShortPartDTO(tuple(data.keys()), data, _token=_DTO_TOKEN)

def as_projection(fn):

    def wrapper(part):
        data = fn(part)
        return ShortPartDTO(tuple(data.keys()), data, _token=_DTO_TOKEN)
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper

class ShortPart:
    @staticmethod
    def _short_data(part) -> dict:
        return {
            "article": part.article,
            "name": part.name,
            "price": part.price,
        }

    @staticmethod
    def _warranty_data(part) -> dict:
        return {
            "article": part.article,
            "manufacturer": part.manufacturer,
            "warranty_months": part.warranty_months,
        }

    # строковые / кортежные проекции
    @staticmethod
    def as_string(part): return f"{part.article} — {part.name} ({part.price} руб.)"

    @staticmethod
    def as_tuple(part): return part.article, part.name, part.price

    # DTO-проекции
    @staticmethod
    def live_short_dto(part) -> LiveProjection:
        return LiveProjection(part, ShortPart._short_data)

    @staticmethod
    def live_warranty_dto(part) -> LiveProjection:
        return LiveProjection(part, ShortPart._warranty_data)

    @staticmethod
    def short_dto(part) -> ShortPartDTO:
        return _to_snapshot(ShortPart._short_data(part))

    @staticmethod
    def warranty_dto(part) -> ShortPartDTO:
        return _to_snapshot(ShortPart._warranty_data(part))