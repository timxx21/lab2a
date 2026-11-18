# Лабораторные работы №1 и №2 — Архитектура проекта

Данный документ содержит полную архитектуру проекта, разделенную по лабораторным работам и логическим веткам. Нажмите на название диаграммы, чтобы раскрыть её.

<details>
<summary><b>🌟 СКВОЗНАЯ АРХИТЕКТУРА ПРОЕКТА (ЛР1 + ЛР2 + ЛР3)</b> (нажмите, чтобы развернуть)</summary>

<br>
Полная картина взаимодействия всех компонентов. В ЛР3 добавлен Real-Time слой (SSE + Database Triggers), который работает параллельно с MVC.

```mermaid
classDiagram
    direction TB

    %% ================== СЛОЙ 1: ВЕБ-СЛОЙ (MVC) ==================
    namespace WebLayer_MVC {
        class MainController {
            -PartRepDBAdapter _db_rep
            -Refresher _refresher
            +do_GET()
            +do_POST()
        }
        class AddController
        class EditController
        class DeleteController
        class EventController {
            +handle_sse(handler)
        }
        class Views {
            <<module>>
            +render_main_page()
            +render_form()
        }
    }

    MainController --> AddController : delegates
    MainController --> EditController : delegates
    MainController --> DeleteController : delegates
    MainController --> EventController : delegates /events
    MainController ..> Views : renders HTML

    %% ================== СЛОЙ 2: REAL-TIME (OBSERVER / PUB-SUB) ==================
    namespace RealTime_Layer {
        class EventBus {
            <<Singleton>>
            +subscribe() Queue
            +notify(event)
        }
        class DBWatcher {
            <<Thread>>
            +watcher_loop()
        }
    }

    EventController --> EventBus : subscribes
    DBWatcher --> EventBus : notifies
    DBWatcher ..> DBConnection : polls system_status

    %% ================== СЛОЙ 3: ХРАНЕНИЕ (РЕПОЗИТОРИИ) ==================
    namespace StorageLayer_Repositories {
        class PartRepository {
            <<interface>>
            +get_by_id()
            +add(part)
        }
        class FilterSortDecorator {
            -_ranges
            -_sort_key
            +_matches_ranges(dto)
            +get_k_n_short_list()
        }
        class PartRepDBAdapter
        class PartRepFile {
            <<abstract>>
        }
        class PartRepJSON
        class PartRepYAML
    }

    PartRepository <|-- FilterSortDecorator
    PartRepository <|-- PartRepDBAdapter
    PartRepository <|-- PartRepFile
    PartRepFile <|-- PartRepJSON
    PartRepFile <|-- PartRepYAML

    MainController ..> PartRepository : requests data
    MainController ..> FilterSortDecorator : uses for UI

    %% ================== СЛОЙ 4: ДОМЕН (ЛР1) ==================
    namespace DomainLayer_LR1 {
        class Part {
            +attach(obs)
            +detach_all()
        }
        class LiveProjection
        class ShortPartDTO {
            <<immutable>>
        }
        class Refresher
        class DBConnection {
            <<Singleton>>
        }
    }

    PartRepDBAdapter ..> Part : creates/returns
    PartRepDBAdapter --> DBConnection : uses
    PartRepFile ..> Part : creates
    PartRepository ..> ShortPartDTO : returns
    
    Part "1" o-- "*" LiveProjection : notify
    LiveProjection --> "1" ShortPartDTO : holds
    Refresher o-- "*" LiveProjection : manages
    MainController --> Refresher : uses (purge)
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

`FilterSortDecorator` поддерживает фильтр типа «Больше X, меньше Y»: вместо одной лямбды вызывающий код передает словарь `ranges` вида `{'id': ('10', '50'), 'price': ('2000', None)}`. Каждая граница приводится к числу (`_to_number`); пустое значение (`None` или `""`) означает отсутствие границы, поэтому незаполненное поле не сужает выборку. Если введено нечисловое значение, декоратор выбрасывает `ValueError`. Фильтрация по `filter_fn` и по `ranges` применяется совместно, затем результат сортируется по `sort_key` (если задан) и только после этого нарезается на страницу `k/n`.

```mermaid
classDiagram
    class PartRepository {
        <<abstract>>
        +get_by_id(id)
        +get_k_n_short_list(k, n)
        +get_count()
        +update(id, part)
        +delete(id)
        +add_with_id(id, part)
    }
    class PartRepositoryDecorator {
        <<abstract>>
        #PartRepository _wrapped
        +get_by_id(id)
        +get_k_n_short_list(k, n)
        +get_count()
        +update(id, part)
        +delete(id)
    }
    class FilterSortDecorator {
        -filter_fn
        -sort_key
        -dict _ranges
        +_to_number(value)
        +_matches_ranges(dto) bool
        +_fetch_all() list
        +_apply() list
        +get_k_n_short_list(k, n)
        +get_count()
    }
    PartRepository <|-- PartRepositoryDecorator
    PartRepositoryDecorator <|-- FilterSortDecorator
    PartRepositoryDecorator o-- PartRepository : wraps
    FilterSortDecorator ..> ShortPartDTO : filters/sorts
```

`ranges` хранит уже приведенные к `float` границы: `{field: (low, high)}`. Метод `_matches_ranges` проверяет, что значение поля DTO попадает в интервал, а `_apply` возвращает полный отфильтрованный и отсортированный список, из которого `get_k_n_short_list` и `get_count` уже берут нужный срез.

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

<details>
<summary><b>Пункт 5: Удаление</b> (нажмите, чтобы развернуть)</summary>

<br>
Для удаления записи создан отдельный `DeleteController`. Это позволяет разгрузить главный контроллер и сохранить принцип единственной ответственности (SRP). Удаление происходит по ID, полученному из GET-параметра.

```mermaid
classDiagram
    class MainController {
        -PartRepDBAdapter _db_rep
        -AddController _add_ctrl
        -EditController _edit_ctrl
        -DeleteController _del_ctrl
        +do_GET()
    }
    class DeleteController {
        -PartRepDBAdapter _db_rep
        +handle_delete(handler, query)
    }
    class Views {
        <<module>>
        +render_main_page()
        +render_redirect()
    }
    class PartRepository {
        <<interface>>
        +delete(id)
    }
    
    MainController --> DeleteController : delegates /delete
    MainController --> Views
    DeleteController --> PartRepository : deletes data
    DeleteController --> Views : renders redirect
```
</details>

<details>
<summary><b>Пункт 6 и 7: Фильтрация и Сортировка (Декоратор)</b> (нажмите, чтобы развернуть)</summary>

<br>
Для фильтрации и сортировки мы переиспользуем паттерн Декоратор из ЛР2. Главный контроллер не фильтрует данные сам: он лишь собирает из GET-параметров словарь `ranges` (`{'id': (min_id, max_id), 'price': (min_price, None)}`) и имя поля сортировки, а затем оборачивает базовый репозиторий БД в `FilterSortDecorator`. Значения границ передаются строками прямо из полей формы и приводятся к числам внутри декоратора.

```mermaid
classDiagram
    class MainController {
        -PartRepDBAdapter _db_rep
        +do_GET()
        +_send_html(html)
    }
    class FilterSortDecorator {
        -filter_fn
        -sort_key
        -dict _ranges
        +_to_number(value)
        +_matches_ranges(dto) bool
        +_fetch_all() list
        +_apply() list
        +get_k_n_short_list(k, n)
        +get_count()
    }
    class PartRepository {
        <<interface>>
    }
    class Views {
        <<module>>
        +render_main_page(parts, min_price, sort_field, min_id, max_id)
    }

    MainController ..> FilterSortDecorator : creates (if ranges or sort)
    MainController ..> Views : passes current filter values
    FilterSortDecorator o-- PartRepository : wraps
    PartRepository <|-- PartRepDBAdapter
```

Форма на главной странице (`render_main_page`) содержит поля `min_id`, `max_id`, `min_price` и `sort`; после применения фильтра контроллер передает их текущие значения обратно в шаблон, чтобы пользователь видел активные условия.
</details>

<details>
<summary><b>Пункт 8*: Real-Time Observer + SSE</b> (нажмите, чтобы развернуть)</summary>

<br>
Для реализации real-time обновлений (отслеживания изменений из внешних источников) была построена распределенная архитектура на базе паттернов Observer и Pub/Sub.
1. **MySQL:** Триггеры отслеживают изменения в таблице `parts` и обновляют `system_status`.
2. **Watcher (Python Thread):** Фоновый поток опрашивает `system_status`. При изменении вызывает `notify()` на `EventBus`.
3. **EventBus (Singleton):** Шина событий, хранящая очереди подписчиков (`queue.Queue`).
4. **SSE Controller:** Держит соединение с браузером и передает данные в формате `text/event-stream`.

```mermaid
classDiagram
    namespace Database_MySQL {
        class parts {
            +id
            +article
            +name
        }
        class system_status {
            +id
            +last_update
        }
        class Trigger_AFTER_INSERT {
            <<Database Trigger>>
        }
    }
    parts ..> Trigger_AFTER_INSERT : fires
    Trigger_AFTER_INSERT ..> system_status : updates last_update

    namespace Python_Backend {
        class DBWatcher {
            <<Thread>>
            -last_update
            +watcher_loop()
        }
        class EventBus {
            <<Singleton>>
            -_listeners : list~Queue~
            +subscribe() Queue
            +unsubscribe(q)
            +notify(event)
        }
        class EventController {
            +handle_sse(handler)
        }
        class MainController {
            +do_GET()
        }
    }

    DBWatcher --> system_status : SELECT (Polling)
    DBWatcher --> EventBus : notify("data_changed")
    EventBus <-- EventController : subscribe()
    MainController --> EventController : delegates /events

    namespace Frontend_Browser {
        class EventSource_JS {
            <<JavaScript>>
            +onmessage(e)
        }
    }
    
    EventController ..> EventSource_JS : SSE (text/event-stream)
    EventSource_JS ..> BrowserPage : window.location.reload()
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

<details>
<summary><b>Пункт 5: Удаление</b> (нажмите, чтобы развернуть)</summary>

<br>
Сценарий: Пользователь нажимает "Удалить", подтверждает действие во всплывающем окне, запись удаляется из БД, и происходит редирект на обновленную главную страницу.

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant MainCtrl as MainController
    participant DelCtrl as DeleteController
    participant Model as PartRepository
    participant View as Views

    User->>Browser: Клик "Удалить" (id=1)
    Note over Browser: JS confirm() запрашивает подтверждение
    User->>Browser: Нажимает "ОК"
    Browser->>MainCtrl: GET /delete?id=1
    activate MainCtrl
    
    MainCtrl->>DelCtrl: handle_delete(self, query)
    activate DelCtrl
    
    DelCtrl->>Model: delete(1)
    Model-->>DelCtrl: Успех (запись удалена)
    
    DelCtrl->>View: render_redirect("/")
    View-->>DelCtrl: HTML (редирект)
    
    DelCtrl-->>MainCtrl: HTML
    deactivate DelCtrl
    
    MainCtrl-->>Browser: HTTP 200 (Redirect)
    deactivate MainCtrl
    
    Browser->>MainCtrl: GET / (автоматически)
    MainCtrl->>Model: get_k_n_short_list()
    Model-->>MainCtrl: list[DTO]
    MainCtrl->>View: render_main_page(dtos)
    View-->>MainCtrl: HTML
    MainCtrl-->>Browser: HTTP 200 (Обновленная таблица)
    Browser-->>User: Таблица без удаленной записи
```
</details>

<details>
<summary><b>Пункты 6 и 7: Фильтрация и Сортировка</b> (нажмите, чтобы развернуть)</summary>

<br>
Сценарий: пользователь задает диапазоны в форме главной страницы («ID от / до», «Цена от») и выбирает поле сортировки. Контроллер превращает параметры в `ranges` и передает их декоратору; сам декоратор приводит границы к числам, отсекает записи вне диапазона и сортирует результат.

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant MainCtrl as MainController
    participant Decorator as FilterSortDecorator
    participant DB as PartRepDBAdapter

    User->>Browser: ID от 10 до 50, цена от 2000, сортировка по цене
    Browser->>MainCtrl: GET /?min_id=10&max_id=50&min_price=2000&sort=price
    MainCtrl->>MainCtrl: ranges = {'id': ('10', '50'), 'price': ('2000', None)}

    alt ranges или sort заданы
        MainCtrl->>Decorator: FilterSortDecorator(DB, sort_key='price', ranges=ranges)
        Note over Decorator: _to_number() превращает границы в float,<br/>пустая граница = None (без ограничения)
    end

    MainCtrl->>Decorator: get_count()
    Decorator->>Decorator: _apply()
    Decorator->>DB: get_count()
    DB-->>Decorator: total
    Decorator->>DB: get_k_n_short_list(total, 1) (получить ВСЕ)
    DB-->>Decorator: list[ShortPartDTO]
    Decorator->>Decorator: _matches_ranges() — отсеять вне диапазонов
    Decorator->>Decorator: sorted() по sort_key
    Decorator-->>MainCtrl: count (после фильтрации)

    MainCtrl->>Decorator: get_k_n_short_list(count, 1)
    Decorator->>Decorator: _apply() → срез [0:count]
    Decorator-->>MainCtrl: отфильтрованный list[ShortPartDTO]

    MainCtrl->>MainCtrl: render_main_page(dtos, min_price, sort_field, min_id, max_id)
    MainCtrl-->>Browser: HTML (таблица + форма с активными условиями)
    Browser-->>User: Только записи в заданных диапазонах, отсортированные
```

Если пользователь ввел нечисловое значение, `_to_number` выбрасывает `ValueError` с сообщением о некорректном фильтре; пустые поля формы в `ranges` не попадают и выборку не сужают.

</details>

<details>
<summary><b>Пункт 8*: Real-Time Update</b> (нажмите, чтобы развернуть)</summary>

<br>
Сценарий: Внешний скрипт (например, `demo.py`) меняет данные в БД. Веб-сервер узнает об этом и автоматически перезагружает страницу у пользователя.

```mermaid
sequenceDiagram
    actor User
    participant Browser
    participant SSE_Ctrl as EventController
    participant Bus as EventBus
    participant Watcher as DBWatcher (Thread)
    participant DB as MySQL Database
    participant External as demo.py (External)

    %% 1. Установка соединения
    User->>Browser: Открывает страницу
    Browser->>SSE_Ctrl: GET /events
    activate SSE_Ctrl
    SSE_Ctrl->>Bus: subscribe()
    Bus-->>SSE_Ctrl: Queue
    Note over SSE_Ctrl: Соединение удерживается открытым (SSE)

    %% 2. Фоновый процесс
    loop Каждые 2 секунды
        Watcher->>DB: SELECT last_update FROM system_status
        DB-->>Watcher: timestamp
    end

    %% 3. Внешнее изменение
    External->>DB: INSERT INTO parts (...)
    activate DB
    DB->>DB: Trigger AFTER INSERT
    DB->>DB: UPDATE system_status SET last_update = NOW()
    deactivate DB

    %% 4. Обнаружение изменения
    Watcher->>DB: SELECT last_update FROM system_status
    DB-->>Watcher: NEW timestamp!
    Watcher->>Bus: notify("data_changed")
    activate Bus
    Bus->>SSE_Ctrl: queue.put("data_changed")
    deactivate Bus

    %% 5. Отправка в браузер
    SSE_Ctrl->>Browser: data: {"type": "data_changed"}
    deactivate SSE_Ctrl
    
    %% 6. Обновление UI
    Note over Browser: JS EventSource ловит сообщение
    Browser->>Browser: window.location.reload()
    Browser->>User: Страница обновилась (новая деталь в таблице)
```
</details>