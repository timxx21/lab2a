"""Демонстрация ЛР2: JSON, YAML, DB, декоратор."""

from autopartsLab1 import (
    Part,
    PartRepJSON,
    PartRepYAML,
    DBConnection,
    PartRepDB,
    PartRepDBAdapter,
    FilterSortDecorator,
)


def demo_files():
    print("=== JSON ===")
    rep = PartRepJSON("parts.json")
    id1 = rep.add(Part("A5", "Диск", 4500, "Bosch", 5.2, 12))
    id2 = rep.add(Part("B5", "Фильтр", 800, "Mann", 0.3, 6))
    id3 = rep.add(Part("C5", "Свеча", 300, "NGK", 0.1, 6))
    rep.write()

    print("count:", rep.get_count())
    print("by id:", rep.get_by_id(id1))
    print("page 1:", rep.get_k_n_short_list(2, 1))
    print("page 2:", rep.get_k_n_short_list(2, 2))

    rep.sort_by("price")
    print("sorted by price:", rep.get_k_n_short_list(10, 1))

    rep.update(id2, Part("B4", "Фильтр премиум", 1200, "Mann", 0.3, 6))
    rep.delete(id3)
    print("after update+delete, count:", rep.get_count())

    print("\n=== YAML ===")
    rep_y = PartRepYAML("parts.yaml")
    rep_y.add(Part("D6", "Амортизатор", 3500, "Kayaba", 2.1, 12))
    rep_y.write()
    print("count:", rep_y.get_count())


def demo_db():
    print("\n=== DB ===")
    conn = DBConnection(
        host="localhost", user="root",
        password="pass", database="autoparts",
    )
    db = PartRepDB(conn)
    rep = PartRepDBAdapter(db)

    new_id = rep.add(Part("E9", "Помпа", 2000, "Hepu", 1.8, 18))
    print("added id:", new_id)
    print("by id:", rep.get_by_id(new_id))
    print("count:", rep.get_count())
    print("page:", rep.get_k_n_short_list(5, 1))

    new_id = rep.add(Part("E10", "Помпа дешманская", 500, "Hepu", 1.8, 18))
    print("added id:", new_id)
    print("by id:", rep.get_by_id(new_id))
    print("count:", rep.get_count())
    print("page:", rep.get_k_n_short_list(5, 1))
    print("\n=== Decorator: дорогие детали, сортировка по цене ===")
    filtered = FilterSortDecorator(
        rep,
        filter_fn=lambda d: d["price"] > 1000,
        sort_key="price",
    )
    print("count:", filtered.get_count())
    print("page:", filtered.get_k_n_short_list(10, 1))


if __name__ == "__main__":
    demo_files()
    demo_db()