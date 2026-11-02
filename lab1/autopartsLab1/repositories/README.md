# Лабораторная работа №2 (Репозитории)

Здесь описаны паттерны работы с файлами, базой данных и декораторы.

## 1. Ветка работы с файлами (Паттерны Стратегия и Реестр)

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
