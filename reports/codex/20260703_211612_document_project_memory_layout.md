# Отчет Codex: Document preferred project memory layout

## 1. Название задачи

Foundation v0.8 - document preferred project memory layout.

## 2. Дата и время

2026-07-03 21:16:12 Europe/Budapest.

## 3. Созданные файлы

- `docs/PROJECT_MEMORY_LAYOUT.md` - документация preferred project memory layout для approved canon и legacy memory.
- `reports/codex/20260703_211612_document_project_memory_layout.md` - текущий отчет по задаче.

## 4. Измененные файлы

- `README.md` - добавлена короткая ссылка на `docs/PROJECT_MEMORY_LAYOUT.md` в разделе Memory System.
- `docs/TASK_QUEUE.md` - добавлен выполненный manual/technical foundation item `Document preferred project memory layout`.

## 5. Что было реализовано

Добавлена документация preferred project memory layout.

Документ объясняет:

- preferred layout `projects/<project>/memory/...`;
- поддерживаемый legacy layout `projects/<project>/world`, `characters`, `prompts`, `episodes`;
- что approved creative canon должен храниться в `projects/<project>/memory/...`;
- что legacy folders остаются совместимыми, но не являются preferred location для нового canon;
- категории `world`, `characters`, `prompts`, `episodes`, `pending`;
- различие между locked canon, expandable canon и pending notes;
- короткий пример на The Origin System.

## 6. Как это работает

Это документационное изменение.

Production pipeline, MemoryLoader, агенты, external integrations и approved canon files не изменялись.

`docs/PROJECT_MEMORY_LAYOUT.md` фиксирует соглашение для будущих human/Codex задач: новый утвержденный canon должен попадать в `projects/<project>/memory/...`, а старые директории остаются только совместимым legacy source.

## 7. Проверки и тесты

Выполнены легкие проверки:

- подтверждено существование `docs/PROJECT_MEMORY_LAYOUT.md`;
- подтверждено, что файл читается как UTF-8;
- проверено наличие обязательных фрагментов про preferred layout;
- проверено, что `__pycache__` не появился;
- проверено, что новые production artifacts не создавались.

Результат проверки:

```text
project_memory_layout_doc_ok
```

Smoke-тесты pipeline не запускались, потому что задача была documentation only и код не изменялся.

## 8. Подтверждение по lore

Новый lore не придумывался.

Approved canon files не переписывались и не расширялись.

Документ использует только структурные правила layout и короткие пути-примеры к уже существующим canon-файлам The Origin System.

## 9. Слабые места

- Документ описывает preferred layout, но не мигрирует старые legacy memory-файлы.
- `memory/episodes/` и `memory/pending/` описаны как preferred folders, но пока не подключались отдельной задачей к runtime loading.
- README содержит только короткую ссылку, без подробного объяснения memory layout, чтобы не раздувать главный файл.

## 10. Рекомендуемый следующий шаг

Следующий безопасный шаг - отдельной задачей решить, нужно ли подключать `projects/<project>/memory/episodes/` и `projects/<project>/memory/pending/` к runtime memory loading, или пока оставить их только как documented authoring layout.

## 11. Требуется ли человеческое ревью

Да, ревью желательно. Это документация для будущего workflow памяти, поэтому важно подтвердить, что preferred layout совпадает с ожиданиями проекта.
