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
        # Проверяем соединение (чтобы demo не упало, если БД выключена)
        conn.connect()
        db_adapter = PartRepDBAdapter(PartRepDB(conn))
        print("Успешное подключение к БД.")
    except Exception as e:
        print(f"Ошибка подключения к БД: {e}")
        return

    # 3. Создаем Composite.
    # БД - главная (primary), файлы - реплики (replicas).
    composite = CompositePartRepository(db_adapter, rep_json, rep_yaml)
    print("Архитектура: БД (Primary) -> JSON -> YAML\n")

    # --- СЦЕНАРИЙ 1: ДОБАВЛЕНИЕ ---
    print("--- 1. Добавляем деталь через БД ---")
    p1 = Part("SYNC-1", "Синхронный фильтр", 1500, "Bosch", 1.2, 12)

    # Вызываем add у Composite. Он создаст в БД и раздаст ID файлам.
    new_id = composite.add(p1)
    composite.flush()  # Сохраняем JSON и YAML на диск

    print(f"Создана деталь с ID = {new_id}")

    # ПРОВЕРКА:
    print(f"Из БД  : {db_adapter.get_by_id(new_id)}")
    print(f"Из JSON: {rep_json.get_by_id(new_id)}")
    print(f"Из YAML: {rep_yaml.get_by_id(new_id)}")

    # --- СЦЕНАРИЙ 2: ОБНОВЛЕНИЕ ---
    print("\n--- 2. Обновляем деталь (меняем цену) ---")
    p1_updated = Part("SYNC-1", "Синхронный фильтр (NEW)", 2000, "Bosch", 1.2, 12)

    composite.update(new_id, p1_updated)
    composite.flush()

    # ПРОВЕРКА:
    print(f"Новая цена в БД  : {db_adapter.get_by_id(new_id).price}")
    print(f"Новая цена в JSON: {rep_json.get_by_id(new_id)['price']}")

    # --- СЦЕНАРИЙ 3: УДАЛЕНИЕ ---
    print("\n--- 3. Удаляем деталь ---")
    composite.delete(new_id)
    composite.flush()

    # ПРОВЕРКА:
    print(f"Количество в БД  : {db_adapter.get_count()}")
    print(f"Количество в JSON: {rep_json.get_count()}")
    print(f"Количество в YAML: {rep_yaml.get_count()}")



if __name__ == "__main__":
    main()