from autopartsLab1 import (
    Part, PartRepJSON, PartRepYAML,
    DBConnection, PartRepDB, PartRepDBAdapter,
    CompositePartRepository, FilterSortDecorator
)

def main():
    print("=== Демонстрация синхронизации БД, JSON и YAML ===\n")

    # 1. Инициализация файловых репозиториев
    backup_json = PartRepJSON("backup_parts.json")
    backup_yaml = PartRepYAML("backup_parts.yaml")


    # 2. Инициализация БД
    try:
        conn = DBConnection(host="localhost", user="root", password="pass", database="autoparts")
        conn.connect()
        db_adapter = PartRepDBAdapter(PartRepDB(conn))
        print("Успешное подключение к БД MySQL.")
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return

    # 3. Создаем Composite
    composite = CompositePartRepository(db_adapter, backup_json, backup_yaml)
    print("Синхронизация файлов с базой данных...")
    composite.resync()
    composite.flush()
    print("Файлы JSON и YAML приведены в соответствие с БД.\n")

    print("--- 1. Добавляем деталь через БД ---")
    # Используем уникальный артикул, чтобы избежать ошибки дубликата
    import random
    rand_art = f"SYNC-{random.randint(1000, 9999)}"
    p1 = Part(rand_art, "Синхронный фильтр", 1500, "Bosch", 1.2, 12)

    new_id = composite.add(p1)
    composite.flush()

    print(f"Создана деталь с ID = {new_id}")

    # ПРОВЕРКА:
    print(f"Из БД  : {db_adapter.get_by_id(new_id).name}")
    print(f"Из JSON: {backup_json.get_by_id(new_id).name}")
    print(f"Из YAML: {backup_yaml.get_by_id(new_id).name}")

    # --- 2. ОБНОВЛЕНИЕ ---
    print("\n--- 2. Обновляем деталь (меняем цену) ---")
    p1_updated = Part(rand_art, "Синхронный фильтр (NEW)", 2000, "Bosch", 1.2, 12)

    composite.update(new_id, p1_updated)
    composite.flush()

    # ПРОВЕРКА (обращаемся через точку .price):
    print(f"Новая цена в БД  : {db_adapter.get_by_id(new_id).price}")
    print(f"Новая цена в JSON: {backup_json.get_by_id(new_id).price}")
    print(f"Новая цена в YAML: {backup_yaml.get_by_id(new_id).price}")

    # --- 3. УДАЛЕНИЕ ---
    print("\n--- 3. Удаляем деталь ---")
    composite.delete(new_id)
    composite.flush()

    # ПРОВЕРКА:
    print(f"Элемент удален. Проверка (должно быть KeyError):")
    try:
        db_adapter.get_by_id(new_id)
        print("ОШИБКА: Объект всё еще в БД!")
    except KeyError:
        print("В БД его нет.")

    try:
        backup_json.get_by_id(new_id)
        print("ОШИБКА: Объект всё еще в JSON!")
    except KeyError:
        print("В JSON его нет.")

    print("\n--- 4. ЭКСПОРТ С ПОМОЩЬЮ ПАТТЕРНА ДЕКОРАТОР ---")
    print("Задача: Выгрузить из БД в ОТДЕЛЬНЫЕ файлы только детали с ценой > 2000.")


    db_filtered = FilterSortDecorator(
        wrapped=db_adapter,
        filter_fn=lambda dto: dto["price"] > 2000,
        sort_key="price"
    )

    # СОЗДАЕМ ЭКСПОРТНЫЕ ФАЙЛЫ
    export_json = PartRepJSON("export_parts.json")
    export_yaml = PartRepYAML("export_parts.yaml")

    # ВЫЗЫВАЕМ НОВЫЙ МЕТОД КОМПОЗИТА
    composite.export_to(
        source_repo=db_filtered,
        target_repositories=[export_json, export_yaml]
    )


if __name__ == "__main__":
    main()