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

    def detach_all(self):
        for obs in list(self._observers):
            try:
                obs.close()
            except Exception as e:
                print(f"[Part] Ошибка при отписке {obs!r}: {e}")
        self._observers.clear()

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

