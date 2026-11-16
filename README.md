# Лабораторные работы №1 и №2 — Архитектура проекта

Данный документ содержит полную архитектуру проекта, разделенную по лабораторным работам и логическим веткам. Нажмите на название диаграммы, чтобы раскрыть её.

<details>
<summary><b>🌟 ОБЩАЯ АРХИТЕКТУРА ПРОЕКТА (ЛР1 + ЛР2)</b> (нажмите, чтобы развернуть)</summary>

<br>
Здесь представлена полная картина взаимодействия всех компонентов. Видно, как доменная сущность `Part` (ЛР1) отделена от слоя хранения данных (`PartRepository`). Паттерн `Composite` связывает несколько хранилищ вместе, а `Decorator` позволяет динамически фильтровать данные.

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
        +add_with_id(id, part)
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

    %% ================== ЛР2: Компоновщик (Синхронизация) ==================
    class CompositePartRepository {
        -PartRepository _primary
        -list _replicas
        +add(part)
        +export_to(source, targets)
        +resync()
    }

    PartRepository <|-- CompositePartRepository
    CompositePartRepository o-- "*" PartRepository : delegates to (primary & replicas)

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
        +add_with_id(id, part)
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
        +add_with_id(id, part)
    }
    class PartRepDBAdapter {
        -PartRepDB _db
        +get_by_id(id) Part
        +add(part) int
        +add_with_id(id, part) int
    }
    class PartRepDB {
        -DBConnection _conn
        +select_by_id(id) dict
        +insert(record) int
        +insert_with_id(id, record) int
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
Паттерн Декоратор позволяет добавить фильтрацию и сортировку поверх любого репозитория, не меняя код самого репозитория.

```mermaid
classDiagram
    class PartRepository {
        <<abstract>>
        +get_k_n_short_list(k, n)
        +get_count()
        +add_with_id(id, part)
    }
    class PartRepositoryDecorator {
        <<abstract>>
        #PartRepository _wrapped
        +get_k_n_short_list(k, n)
        +get_count()
        +add_with_id(id, part)
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

<details>
<summary><b>4. Ветка Компоновщика (Синхронизация хранилищ)</b> (нажмите, чтобы развернуть)</summary>

<br>
Паттерн Компоновщик (Composite) позволяет работать с группой репозиториев как с единым целым. В данном случае он берет ID из Primary (БД) и синхронизирует данные с репликами (файлами JSON/YAML).

```mermaid
classDiagram
    class PartRepository {
        <<abstract>>
        +add(part) int
        +add_with_id(id, part) int
    }
    
    class CompositePartRepository {
        -PartRepository _primary
        -list _replicas
        +add(part) int
        +add_with_id(id, part) int
        +update(id, part)
        +delete(id)
        +resync()
        +export_to(source_repo, target_repos)
    }

    PartRepository <|-- CompositePartRepository
    CompositePartRepository o-- "1" PartRepository : primary
    CompositePartRepository o-- "*" PartRepository : replicas
```

</details>

## Лабораторная работа №3 (MVC и Observer)</b>

### Диаграммы классов по пунктам:
<details>
<summary><b> Пункт 1: Базовый MVC + Read</b> (нажмите, чтобы развернуть)</summary>

<br>
На этой диаграмме показано разделение ответственности по паттерну MVC. Контроллер обрабатывает HTTP-запросы и связывает Представление (HTML-шаблоны) с Моделью (Репозиториями). Паттерн Наблюдатель используется на стороне Модели (через `Refresher`) для синхронизации данных.

```mermaid
classDiagram
    class MainController {
        -DBConnection _conn
        -PartRepDBAdapter _db_rep
        +do_GET()
        +_send_html(html)
    }

    class Views {
        <<module>>
        +render_main_page(parts, message)
        +render_view_page(part)
    }

    class PartRepository {
        <<interface>>
        +get_by_id(id)
        +get_k_n_short_list(k, n)
        +get_count()
    }
    class PartRepDBAdapter
    class PartRepDB
    class DBConnection {
        <<Singleton>>
    }

    class Refresher {
        <<Observer Pattern>>
        +make(part, producer)
        +purge()
    }

    MainController --> Views : calls to render
    MainController --> PartRepository : requests data
    PartRepository <|-- PartRepDBAdapter
    PartRepDBAdapter o-- PartRepDB
    PartRepDB o-- DBConnection
    MainController ..> Refresher : uses for state update
```
</details>

<details>
<summary><b> Пункт 2: Добавление записи</b> (нажмите, чтобы развернуть)</summary>

<br>
Для выполнения требования "для нового окна — новый контроллер" мы выделили `AddController`. Главный контроллер делегирует ему обработку маршрута `/add`.

```mermaid
classDiagram
    class MainController {
        +do_GET()
        +do_POST()
    }
    class AddController {
        -PartRepDBAdapter _db_rep
        +show_form()
        +handle_post()
    }
    class Views {
        +render_main_page()
        +render_add_form()
        +render_redirect()
    }
    MainController --> AddController : delegates /add
    MainController --> Views
    AddController --> Views
    AddController --> PartRepDBAdapter
```
</details>

<details>
<summary><b> Пункт 3: Редактирование</b> (нажмите, чтобы развернуть)</summary>

<br>
По аналогии с добавлением создан `EditController`. Теперь `MainController` выступает как маршрутизатор, который передает управление нужному контроллеру в зависимости от URL.

```mermaid
classDiagram
    class MainController {
        -PartRepDBAdapter _db_rep
        -AddController _add_ctrl
        -EditController _edit_ctrl
        +do_GET()
        +do_POST()
    }

    class AddController {
        +show_form(handler)
        +handle_post(handler)
    }

    class EditController {
        -PartRepDBAdapter _db_rep
        +show_form(handler, query)
        +handle_post(handler)
    }

    class Views {
        <<module>>
        +render_main_page()
        +render_view_page()
        +render_add_form()
        +render_edit_form()
        +render_redirect()
    }

    class PartRepository {
        <<interface>>
    }
    class PartRepDBAdapter

    MainController --> AddController : delegates /add
    MainController --> EditController : delegates /edit
    MainController --> Views : renders
    AddController --> Views
    EditController --> Views : renders form
    EditController --> PartRepository : updates data
```
</details>

<details>
<summary><b> Пункт 4: Универсальная форма</b> (нажмите, чтобы развернуть)</summary>

<br>
Рефакторинг: вместо двух разных View-функций для добавления и редактирования, создана одна универсальная `render_form`. Различие в поведении (пустая/заполненная форма) теперь полностью контролируется контроллерами.

```mermaid
classDiagram
    class MainController {
        -PartRepDBAdapter _db_rep
        -AddController _add_ctrl
        -EditController _edit_ctrl
    }
    class AddController {
        +show_form(handler)
        +handle_post(handler)
    }
    class EditController {
        +show_form(handler, query)
        +handle_post(handler)
    }
    class Views {
        <<module>>
        +render_main_page()
        +render_view_page()
        +render_form(part=None, error="")
        +render_redirect()
    }
    MainController --> AddController : delegates /add
    MainController --> EditController : delegates /edit
    MainController --> Views
    AddController --> Views : render_form(part=None)
    EditController --> Views : render_form(part=dict)
```
</details>

### Диаграммы последовальности по пунктам:
<details>
<summary><b> Пункт 1: Read / Просмотр </b> (нажмите, чтобы развернуть)</summary>

<br>
Сценарий: Пользователь открывает главную страницу, видит список, затем нажимает "Подробнее" на одной из деталей.

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant Controller as MainController
    participant Repo as PartRepository (Model)
    participant View as Views

    %% Открытие главной страницы
    User->>Browser: Вводит URL (localhost:8000)
    Browser->>Controller: HTTP GET /
    activate Controller
    
    Controller->>Repo: get_count()
    Repo-->>Controller: count
    Controller->>Repo: get_k_n_short_list(count, 1)
    Repo-->>Controller: list[ShortPartDTO]
    
    Controller->>View: render_main_page(dtos)
    activate View
    View-->>Controller: HTML string
    deactivate View
    
    Controller-->>Browser: HTTP 200 (HTML)
    deactivate Controller
    Browser-->>User: Отображает таблицу

    %% Просмотр подробностей
    User->>Browser: Клик на "Подробнее"
    Browser->>Controller: HTTP GET /view?id=1
    activate Controller
    
    Controller->>Repo: get_by_id(1)
    Repo-->>Controller: Part object
    
    Controller->>View: render_view_page(part_dict)
    activate View
    View-->>Controller: HTML string
    deactivate View
    
    Controller-->>Browser: HTTP 200 (HTML)
    deactivate Controller
    Browser-->>User: Отображает карточку детали
```
</details>

<details>
<summary><b> Пункт 2: Create / Добавление  </b> (нажмите, чтобы развернуть)</summary>

<br>
Сценарий добавления. Показана работа валидации: если данные не проходят, пользователь остается на форме.

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant MainCtrl as MainController
    participant AddCtrl as AddController
    participant Model as PartRepDBAdapter
    participant View as Views

    User->>Browser: Клик "Добавить запись"
    Browser->>MainCtrl: GET /add
    MainCtrl->>AddCtrl: show_form()
    AddCtrl->>View: render_add_form()
    View-->>AddCtrl: HTML
    AddCtrl-->>Browser: HTTP 200 (Форма)

    User->>Browser: Заполняет и жмет "Сохранить"
    Browser->>MainCtrl: POST /add
    MainCtrl->>AddCtrl: handle_post(request)
    AddCtrl->>Model: Part(...) - Валидация
    alt Валидация ОК
        AddCtrl->>Model: add(part)
        AddCtrl->>View: render_redirect("/")
        AddCtrl-->>Browser: HTTP 200 (Redirect)
        Browser->>MainCtrl: GET /
        MainCtrl-->>Browser: Обновленная таблица
    else Ошибка
        AddCtrl->>View: render_add_form(error)
        AddCtrl-->>Browser: HTTP 200 (Форма с ошибкой)
    end
```
</details>

<details>
<summary><b> Пункт 3: Update / Редактирование</b> (нажмите, чтобы развернуть)</summary>

<br>
Сценарий редактирования. Сначала контроллер загружает данные (GET), затем сохраняет их (POST).

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant MainCtrl as MainController
    participant EditCtrl as EditController
    participant Model as Part / Repo
    participant View as Views

    User->>Browser: Клик "Редактировать" (id=1)
    Browser->>MainCtrl: GET /edit?id=1
    MainCtrl->>EditCtrl: show_form(query)
    EditCtrl->>Model: get_by_id(1)
    Model-->>EditCtrl: Part
    EditCtrl->>View: render_edit_form(part)
    View-->>EditCtrl: HTML
    EditCtrl-->>Browser: HTML (Форма с данными)
    Browser-->>User: Форма редактирования

    User->>Browser: Изменение данных и Submit
    Browser->>MainCtrl: POST /edit (data)
    MainCtrl->>EditCtrl: handle_post(request)
    EditCtrl->>Model: Part(...)
    
    alt Данные валидны
        EditCtrl->>Model: update(id, part)
        EditCtrl->>View: render_redirect("/")
        EditCtrl-->>Browser: HTTP 200 (Redirect)
        Browser->>MainCtrl: GET /
        MainCtrl-->>Browser: Обновленная таблица
    else Ошибка валидации
        Model-->>EditCtrl: Exception
        EditCtrl->>View: render_edit_form(part_data, error)
        EditCtrl-->>Browser: HTTP 200 (Форма с ошибкой)
        Browser-->>User: Форма (данные сохранены, видна ошибка)
    end
```
</details>

<details>
<summary><b> Пункт 4: Универсальная форма </b> (нажмите, чтобы развернуть)</summary>

<br>
Сценарий: показываем, как один и тот же `render_form` используется для двух разных сценариев (Add и Edit).

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant MainCtrl as MainController
    participant Ctrl as Add/Edit Controller
    participant View as Views

    alt Сценарий "Добавление"
        User->>Browser: GET /add
        Browser->>MainCtrl: HTTP Request
        MainCtrl->>Ctrl: show_form(handler)
        Note over Ctrl: part_data = None
        Ctrl->>View: render_form(part=None)
        View-->>Browser: Пустая форма (HTML)
        
    else Сценарий "Редактирование"
        User->>Browser: GET /edit?id=1
        Browser->>MainCtrl: HTTP Request
        MainCtrl->>Ctrl: show_form(handler, query)
        Note over Ctrl: part_data = dict(id=1, ...)
        Ctrl->>View: render_form(part=dict)
        View-->>Browser: Заполненная форма (HTML)
    end
    
    Browser-->>User: Отображение одной и той же View
```
</details>