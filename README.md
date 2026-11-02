# Лабораторная работа №1 (Домен и Observer)

Здесь описаны доменные сущности, паттерн Observer и менеджер, работающие с сущностью `Part`.

## 1. Ядро: Домен и живые проекции (Observer)

На этой диаграмме видно, как `Part` (Subject) уведомляет `LiveProjection` (Observer) об изменениях, а `Refresher` управляет их жизненным циклом.

```mermaid
classDiagram
    class Part {
        -list _observers
        -_article / _name / _price
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


