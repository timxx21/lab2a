# Лабораторные работы №1 и №2 — Архитектура проекта

Данный документ содержит полную архитектуру проекта, разделенную по лабораторным работам и логическим веткам. Нажмите на название диаграммы, чтобы раскрыть её.

<details>
<summary><b>🌟 ОБЩАЯ АРХИТЕКТУРА ПРОЕКТА (ЛР1 + ЛР2)</b> (нажмите, чтобы развернуть)</summary>

<br>
Здесь представлена полная картина взаимодействия всех компонентов. Видно, как доменная сущность `Part` (ЛР1) отделена от слоя хранения данных (`PartRepository`), а паттерны Observer, Strategy, Adapter, Singleton и Decorator гармонично дополняют друг друга.

```mermaid
classDiagram
    %% ================== ЛР1: Домен и Обсервер ==================
    class Part {
        -list _observers
        +attach(obs)
        +detach_all()
        +_notify()
    }

    class LiveProjection {
        +update(subject)
        +is_alive : bool
    }
    
    class ShortPartDTO {
        <<immutable>>
    }

    class Refresher {
        +make(part, producer)
        +purge()
    }

    class PartManager {
        -dict _parts
        +add(part)
        +remove(part)
    }

    Part "1" o-- "*" LiveProjection : notify
    LiveProjection --> "1" ShortPartDTO : holds
    Refresher o-- "*" LiveProjection : manages
    PartManager o-- "*" Part : stores
    PartManager o-- Refresher : uses

    %% ================== ЛР2: Интерфейс и Декораторы ==================
    class PartRepository {
        <<abstract>>
        +get_by_id(id)
        +add(part)
        +get_count()
    }

    class PartRepositoryDecorator {
        <<abstract>>
        #PartRepository _wrapped
    }

    class FilterSortDecorator {
        -filter_fn
        -sort_key
    }

    PartRepository <|-- PartRepositoryDecorator
    PartRepositoryDecorator <|-- FilterSortDecorator
    PartRepositoryDecorator o-- PartRepository : wraps

    %% ================== ЛР2: Файлы (Стратегия) ==================
    class PartRepFile {
        <<abstract>>
        #_path
        #_serializer
    }

    class PartRepJSON
    class PartRepYAML

    class Serializer {
        <<interface>>
    }
    
    class JsonSerializer
    class YamlSerializer
    
    class SerializerRegistry {
        +get(name) Serializer
    }

    PartRepository <|-- PartRepFile
    PartRepFile <|-- PartRepJSON
    PartRepFile <|-- PartRepYAML
    PartRepFile o-- Serializer : delegates
    Serializer <|-- JsonSerializer
    Serializer <|-- YamlSerializer
    SerializerRegistry ..> Serializer : creates

    %% ================== ЛР2: База Данных (Адаптер + Синглтон) ==================
    class PartRepDBAdapter {
        -PartRepDB _db
    }

    class PartRepDB {
        -DBConnection _conn
    }

    class DBConnection {
        <<Singleton>>
        -_instance
    }

    PartRepository <|-- PartRepDBAdapter
    PartRepDBAdapter o-- PartRepDB : delegates
    PartRepDB o-- DBConnection : uses
    
    %% Зависимости от домена (что возвращают репозитории)
    PartRepository ..> Part : returns
    PartRepository ..> ShortPartDTO : returns
```

</details>

## Лабораторная работа №1 (Домен и Observer)

<details>
<summary><b>1. Ядро: Домен и живые проекции (Observer)</b> (нажмите, чтобы развернуть)</summary>

<br>
На этой диаграмме видно, как `Part` (Subject) уведомляет `LiveProjection` (Observer) об изменениях, а `Refresher` управляет их жизненным циклом.

```mermaid
classDiagram
    class Part {
        -list _observers
        -_article
        -_name
        -_price
        +attach(obs)
        +detach(obs)
        +detach_all()
        +_notify()
    }
    class LiveProjection {
        -Part _part
        -ShortPartDTO _dto
        +update(subject)
        +is_alive : bool
        +close()
    }
    class ShortPartDTO {
        <<immutable>>
        +fields
        +to_dict()
    }
    class Refresher {
        -list _live
        +make(part, producer)
        +purge()
        +remove_part(part)
    }
    class ShortPart {
        <<factory>>
        +_short_data(part)
        +_warranty_data(part)
        +live_short_dto(part)
    }
    Part "1" o-- "*" LiveProjection : notify
    LiveProjection --> "1" ShortPartDTO : holds
    Refresher o-- "*" LiveProjection : manages
    ShortPart ..> LiveProjection : creates
    ShortPart ..> ShortPartDTO : creates
```

</details>

<details>
<summary><b>2. Вспомогательные ветки: Парсеры и Менеджер</b> (нажмите, чтобы развернуть)</summary>

<br>
Инструменты для создания объекта из разных форматов и in-memory репозиторий для демонстрации.

```mermaid
classDiagram
    class Part {
        +from_dict(data)
    }
    class PartParser {
        -dict _parsers
        +register(name)
        +parse(data, fmt) Part
        +available()
    }
    class PartManager {
        -dict _parts
        -Refresher _refresher
        +add(part)
        +remove(part)
        +get(article)
    }
    class Refresher
    PartParser ..> Part : creates
    PartManager o-- "*" Part : stores
    PartManager o-- Refresher : uses
```

</details>

## Лабораторная работа №2 (Репозитории)

<details>
<summary><b>1. Ветка работы с файлами (Стратегия и Реестр)</b> (нажмите, чтобы развернуть)</summary>

<br>
Показывает, как решается проблема дублирования кода между JSON и YAML. Вся логика в базовом `PartRepFile`, а формат вынесен в стратегии `Serializer`.

```mermaid
classDiagram
    class PartRepository {
        <<abstract>>
        +get_by_id(id)
        +add(part)
        +get_count()
    }
    class PartRepFile {
        <<abstract>>
        #_path
        #_serializer
        +read()
        +write()
    }
    class PartRepJSON
    class PartRepYAML
    class Serializer {
        <<interface>>
        +dump(records)
        +load(text)
    }
    class JsonSerializer
    class YamlSerializer
    class SerializerRegistry {
        +register(name)
        +get(name) Serializer
    }
    PartRepository <|-- PartRepFile
    PartRepFile <|-- PartRepJSON
    PartRepFile <|-- PartRepYAML
    PartRepFile o-- Serializer : delegates to
    Serializer <|-- JsonSerializer
    Serializer <|-- YamlSerializer
    SerializerRegistry ..> Serializer : creates
    PartRepJSON ..> SerializerRegistry : uses
    PartRepYAML ..> SerializerRegistry : uses
```

</details>

<details>
<summary><b>2. Ветка работы с БД (Синглтон и Адаптер)</b> (нажмите, чтобы развернуть)</summary>

<br>
`DBConnection` (Синглтон) управляет единственным соединением. `PartRepDBAdapter` (Адаптер) встраивает SQL-репозиторий в общую иерархию.

```mermaid
classDiagram
    class PartRepository {
        <<abstract>>
    }
    class PartRepDBAdapter {
        -PartRepDB _db
        +get_by_id(id) Part
        +add(part) int
    }
    class PartRepDB {
        -DBConnection _conn
        +select_by_id(id) dict
        +insert(record) int
    }
    class DBConnection {
        <<Singleton>>
        -_instance
        +fetch_one()
        +execute_commit()
    }
    PartRepository <|-- PartRepDBAdapter
    PartRepDBAdapter o-- PartRepDB : delegates to
    PartRepDB o-- DBConnection : uses
```

</details>

<details>
<summary><b>3. Ветка Декораторов (Фильтр и Сортировка)</b> (нажмите, чтобы развернуть)</summary>

<br>
Паттерн Декоратор позволяет добавить фильтрацию и сортировку поверх любого репозитория.

```mermaid
classDiagram
    class PartRepository {
        <<abstract>>
        +get_k_n_short_list(k, n)
        +get_count()
    }
    class PartRepositoryDecorator {
        <<abstract>>
        #PartRepository _wrapped
        +get_k_n_short_list(k, n)
        +get_count()
    }
    class FilterSortDecorator {
        -filter_fn
        -sort_key
        +get_k_n_short_list(k, n)
        +get_count()
    }
    PartRepository <|-- PartRepositoryDecorator
    PartRepositoryDecorator <|-- FilterSortDecorator
    PartRepositoryDecorator o-- PartRepository : wraps
```

</details>