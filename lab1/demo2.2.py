from autopartsLab1 import (
    Part, PartRepJSON, PartRepYAML,
    DBConnection, PartRepDB, PartRepDBAdapter,
    CompositePartRepository
)

def main():
    print("=== Демонстрация синхронизации БД, JSON и YAML ===\n")

    # 1. Инициализация файловых репозиториев
    rep_json = PartRepJSON("parts.json")
    rep_yaml = PartRepYAML("parts.yaml")

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
    composite = CompositePartRepository(db_adapter, rep_json, rep_yaml)
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
    print(f"Из JSON: {rep_json.get_by_id(new_id).name}")
    print(f"Из YAML: {rep_yaml.get_by_id(new_id).name}")

    # --- 2. ОБНОВЛЕНИЕ ---
    print("\n--- 2. Обновляем деталь (меняем цену) ---")
    p1_updated = Part(rand_art, "Синхронный фильтр (NEW)", 2000, "Bosch", 1.2, 12)

    composite.update(new_id, p1_updated)
    composite.flush()

    # ПРОВЕРКА (обращаемся через точку .price):
    print(f"Новая цена в БД  : {db_adapter.get_by_id(new_id).price}")
    print(f"Новая цена в JSON: {rep_json.get_by_id(new_id).price}")
    print(f"Новая цена в YAML: {rep_yaml.get_by_id(new_id).price}")
"""
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
        rep_json.get_by_id(new_id)
        print("ОШИБКА: Объект всё еще в JSON!")
    except KeyError:
        print("В JSON его нет.")

"""


if __name__ == "__main__":
    main()