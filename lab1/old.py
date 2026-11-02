import json

import csv
import io

class Part:
    def __init__(self, article: str, name: str, price: float,
                 manufacturer: str, weight: float, warranty_months: int):
        self._article = self.validate_article(article)
        self._name = self.validate_name(name)
        self._price = self.validate_price(price)
        self._manufacturer = self.validate_manufacturer(manufacturer)
        self._weight = self.validate_weight(weight)
        self._warranty_months = self.validate_warranty(warranty_months)

        self._observers = []

# выносим повторы кода из валидаторов в методы
    @staticmethod
    def _require_nonempty_str(value, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} не может быть пустым")
        return value.strip()

    @staticmethod
    def _require_positive_number(value, field: str, cast=float):
        try:
            v = cast(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field} должно быть числом")
        if v <= 0:
            raise ValueError(f"{field} должно быть положительным")
        return v

    @staticmethod
    def _require_nonnegative_int(value, field: str) -> int:
        try:
            v = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"{field} должно быть целым числом")
        if v < 0:
            raise ValueError(f"{field} не может быть отрицательным")
        return v


# сами валидаторы
    @staticmethod
    def validate_article(value) -> str:
        return Part._require_nonempty_str(value, "Артикул").upper()

    @staticmethod
    def validate_name(value) -> str:
        return Part._require_nonempty_str(value, "Название")

    @staticmethod
    def validate_price(value) -> float:
        return Part._require_positive_number(value, "Цена")

    @staticmethod
    def validate_manufacturer(value) -> str:
        return Part._require_nonempty_str(value, "Производитель")

    @staticmethod
    def validate_weight(value) -> float:
        return Part._require_positive_number(value, "Вес")

    @staticmethod
    def validate_warranty(value) -> int:
        return Part._require_nonnegative_int(value, "Гарантия")

# геттеры
    @property
    def article(self) -> str:
        return self._article

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price

    @property
    def manufacturer(self) -> str:
        return self._manufacturer

    @property
    def weight(self) -> float:
        return self._weight

    @property
    def warranty_months(self) -> int:
        return self._warranty_months

# наблюдатели
    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self):
        for obs in list(self._observers):
            try:
                obs.update(self)
            except Exception as e:
                print(f"[Part] Ошибка наблюдателя {obs!r}: {e}")

# сеттеры
    @article.setter
    def article(self, value):
        new = self.validate_article(value)
        if new != self._article:
            self._article = new
            self._notify()

    @name.setter
    def name(self, value):
        new = self.validate_name(value)
        if new != self._name:
            self._name = new
            self._notify()

    @price.setter
    def price(self, value):
        new = self.validate_price(value)
        if new != self._price:
            self._price = new
            self._notify()

    @manufacturer.setter
    def manufacturer(self, value):
        new = self.validate_manufacturer(value)
        if new != self._manufacturer:
            self._manufacturer = new
            self._notify()

    @weight.setter
    def weight(self, value):
        new = self.validate_weight(value)
        if new != self._weight:
            self._weight = new
            self._notify()

    @warranty_months.setter
    def warranty_months(self, value):
        new = self.validate_warranty(value)
        if new != self._warranty_months:
            self._warranty_months = new
            self._notify()


# перегрузка конструктора
  #  @classmethod
   # def from_string(cls, s: str) -> "Part":
     #   parts = [p.strip() for p in s.split(";")]
      #  if len(parts) != 6:
       #     raise ValueError("Ожидается 6 полей через ';'")
        #return cls(parts[0], parts[1], float(parts[2]),
         #          parts[3], float(parts[4]), int(parts[5]))

  #  @classmethod
   # def from_json(cls, data: str) -> "Part":
    #    obj = json.loads(data)
     #   return cls(obj["article"], obj["name"], obj["price"],
      #             obj["manufacturer"], obj["weight"],
       #            obj["warranty_months"])

    @classmethod
    def from_dict(cls, data: dict) -> "Part":
        required = ("article", "name", "price", "manufacturer", "weight", "warranty_months")
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"Отсутствуют поля: {missing}")
        return cls(article = data["article"],name = data["name"],price = data["price"],
        manufacturer = data["manufacturer"],weight = data["weight"],warranty_months = data["warranty_months"])

# полный вывод и проверка на равенство
    def __str__(self) -> str:
        return (f"Part(article={self._article}, name={self._name}, "
                f"price={self._price}, "
                f"manufacturer={self._manufacturer}, "
                f"weight={self._weight}, "
                f"warranty_months={self._warranty_months})")

    def __eq__(self, other):
        if not isinstance(other, Part):
            return NotImplemented
        return self._article == other._article

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


class ShortPart:


    # строковые / кортежные проекции (как раньше)
    @staticmethod
    def as_string(part): return f"{part.article} — {part.name} ({part.price} руб.)"

    @staticmethod
    def as_tuple(part): return part.article, part.name, part.price

    # DTO-проекции
    @staticmethod
    @as_projection
    def short_dto(part):
        return {"article": part.article, "name": part.name, "price": part.price}

    @staticmethod
    @as_projection
    def warranty_dto(part):
        return {
            "article": part.article,
            "manufacturer": part.manufacturer,
            "warranty_months": part.warranty_months,
        }


# замечательный паттерн проектор
'''class ShortPart:

    # строка
    @staticmethod
    @as_projection

    def as_string(part: Part) -> str:

        return f"{part.article} — {part.name} ({part.price} руб.)"

    # кортеж
    @staticmethod
    def as_tuple(part: Part) -> tuple:
        return part.article, part.name, part.price

    # словарь
    @staticmethod
    def as_dict(part: Part) -> dict:
        return {
            "article": part.article,
            "name": part.name,
            "price": part.price,
        }

    # прайс-лист
    @staticmethod
    def price_line(part: Part) -> str:
        return f"{part.article}: {part.price} руб."

    # карточка гарантии
    @staticmethod
    def warranty_card(part: Part) -> str:
        return f"{part.article} — гарантия {part.warranty_months} мес."

    # краткое описание
    @staticmethod
    def for_supplier_email(part: Part) -> str:
        return (f"Товар: {part.name} (арт. {part.article}), "
                f"производитель: {part.manufacturer}")'''

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




if __name__ == "__main__":
    p = Part("ab-123", "Тормозной диск", 4500, "Bosch", 5.2, 12)
    print("Полная  :", p)
    print("Краткая :", ShortPart.as_string(p))
    d = ShortPart.short_dto(p)
    print((type(d)))
    print(d)
    d2 = ShortPart.warranty_dto(p)
    print((type(d2)))
    print(d2)
    print("\nПерегрузка конструктора")
    p2 = PartParser.parse("CD-456; Фильтр масляный; 800; Mann; 0.3; 6", "string")
    p3 = PartParser.parse(
        '{"article":"AB-123","name":"Тормозной диск","price":4500,'
        '"manufacturer":"Bosch","weight":5.2,"warranty_months":12}', "json"
    )
    p5 = PartParser.parse(
        "article,name,price,manufacturer,weight,warranty_months\n"
        "GH-012,Ремень ГРМ,1200,Gates,0.4,24",
        "csv",
    )
    p6 = PartParser.parse("IJ-345,Амортизатор,3500,Kayaba,2.1,12", "csv")

    # пробуем формат без парсера''

    '''p7 = PartParser.parse("KL-678|Помпа|5000|Hepu|1.8|18", "pipe")
    print("pipe        :", p7)'''



    print("from_string :", p2)
    print("from_json   :", p3)

    print(" csv        :", p5)
    print("csv б/головы:", p6)

    print("\nСравнение объектов ")
    print("p == p3 :", p == p3)
    print("p == p2 :", p == p2)

    print("\nПочему проекция это круто и изящно?")
    print("До изменения     :", ShortPart.as_string(p))
    p.name = "Тормозной диск (усиленный)"
    p.price = 5200
    print("После изменения  :", ShortPart.as_string(p))


    print("\nНевозможность создать невалидный объект")
    cases = [
        ("пустой артикул",     lambda: Part("",   "X", 100, "Y", 1,  1)),
        ("пустое название",    lambda: Part("A1", "",  100, "Y", 1,  1)),
        ("отрицательная цена", lambda: Part("A1", "X", -5,  "Y", 1,  1)),
        ("пустой производитель", lambda: Part("A1", "X", 100, "",  1,  1)),
        ("нулевой вес",        lambda: Part("A1", "X", 100, "Y", 0,  1)),
        ("отрицательная гарантия", lambda: Part("A1", "X", 100, "Y", 1, -1)),
    ]
    for label, call in cases:
        try:
            call()
        except ValueError as e:
            print(f"  {label}: {e}")

    print("\nАртикул нормализуется в валидации (помимо проверки он приводит к uppercase")
    p4 = Part("  xy-9  ", "Свеча", 300, "NGK", 0.1, 6)
    print("Артикул:", p4.article)

