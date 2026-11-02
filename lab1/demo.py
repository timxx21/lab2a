from autopartsLab1 import Part, ShortPart, Refresher, PartParser, PartRepository



def main():
    refresher = Refresher()
    repo = PartRepository(refresher)
    print("\n-------------Создаем обьект")
    p = Part("ab-123", "Тормозной диск", 4500, "Bosch", 5.2, 12)
    repo.add(p)
    print(len(repo), 'количество обьектов')
    print("Полная  :", p)
    print("Краткая :", ShortPart.as_string(p))

    d = ShortPart.short_dto(p)
    print(type(d), d)
    d2 = ShortPart.warranty_dto(p)
    print(type(d2), d2)

    print("\n------------Перегрузка конструктора")
    p2 = PartParser.parse(
        "CD-456; Фильтр масляный; 800; Mann; 0.3; 6", "string"
    )
    repo.add(p2)

    p3 = PartParser.parse(
        '{"article":"AB-123","name":"Тормозной диск","price":4500,'
        '"manufacturer":"Bosch","weight":5.2,"warranty_months":12}',
        "json",
    )
    repo.add(p3)

    p5 = PartParser.parse(
        "article,name,price,manufacturer,weight,warranty_months\n"
        "GH-012,Ремень ГРМ,1200,Gates,0.4,24",
        "csv",
    )
    repo.add(p5)
    p6 = PartParser.parse("IJ-345,Амортизатор,3500,Kayaba,2.1,12", "csv")
    repo.add(p6)

    print("from_string :", p2)
    print("from_json   :", p3)
    print("csv         :", p5)
    print("csv б/головы:", p6)
    print(len(repo), 'количество обьектов')
    print("\nСравнение объектов")
    print("p == p3 :", p == p3)
    print("p == p2 :", p == p2)

    print("\n------------Обсервер")

    live_short = refresher.make(p, ShortPart._short_data)
    live_warranty = refresher.make(p, ShortPart._warranty_data)

    print("обычная проекция до:", live_short)
    print("гарантийная до     :", live_warranty)

    p.price = 5200
    p.name = "Тормозной диск (усиленный)"
    p.warranty_months = 24

    print("обычная проекция после:", live_short)
    print("гарантийная до        :", live_warranty)


    live_short.close()
    live_warranty.close()
    p.price = 1_000_000
    print("после закрытия е изменилось", live_short)

    print("\n------------Тестим изменения проекций")

    pp2 = Part("ab-123", "Тормозной диск", 4500, "Bosch", 5.2, 12)
    repo.add(pp2)
    print(len(repo), 'количество обьектов')
    live_short1 = refresher.make(pp2, ShortPart._short_data)
    live_warranty1 = refresher.make(pp2, ShortPart._warranty_data)

    print(live_short1)
    print(live_warranty1)
    print(len(refresher), 'проекции')


    repo.remove(pp2)
    print("Удалили обьект")
    print(len(repo), 'количество обьектов')
    print("проверяем живы ли наши проекции обьекта")
    print(live_short1.is_alive)
    print(live_warranty1.is_alive)
    print("количество проекций")
    print(len(refresher))

    print("мы все еще можем получить доступ к последнему значению dto")
    print(live_short1)  # последний снимок
    print(live_short1.value) # если обьект удален то будет возвращен кортеж (последнее значение, уведомление)

    print("\n------------------Невозможность создать невалидный объект")
    cases = [
        ("пустой артикул", lambda: Part("", "X", 100, "Y", 1, 1)),
        ("пустое название", lambda: Part("A1", "", 100, "Y", 1, 1)),
        ("отрицательная цена", lambda: Part("A1", "X", -5, "Y", 1, 1)),
        ("пустой производитель", lambda: Part("A1", "X", 100, "", 1, 1)),
        ("нулевой вес", lambda: Part("A1", "X", 100, "Y", 0, 1)),
        ("отрицательная гарантия", lambda: Part("A1", "X", 100, "Y", 1, -1)),
    ]
    for label, call in cases:
        try:
            call()
        except ValueError as e:
            print(f"  {label}: {e}")

    print("\n----Артикул нормализуется в валидации")
    p4 = Part("  xy-9  ", "Свеча", 300, "NGK", 0.1, 6)
    print("Артикул:", p4.article)


if __name__ == "__main__":
    main()