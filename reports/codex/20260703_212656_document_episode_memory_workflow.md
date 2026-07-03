# Отчет Codex: Document episode memory workflow

## 1. Название задачи

Foundation v0.9 - document episode memory workflow.

## 2. Дата и время

2026-07-03 21:26:56 Europe/Budapest.

## 3. Созданные файлы

- `docs/EPISODE_MEMORY_WORKFLOW.md` - документация будущего workflow чтения памяти, принятия эпизодов и предложений memory updates.
- `reports/codex/20260703_212656_document_episode_memory_workflow.md` - текущий отчет по задаче.

## 4. Измененные файлы

- `docs/TASK_QUEUE.md` - добавлен выполненный manual/technical foundation item `Document episode memory workflow`.

## 5. Что было реализовано

Добавлен документ `docs/EPISODE_MEMORY_WORKFLOW.md`.

Он описывает, как будущие story/episode agents должны:

- читать `memory/world`, `memory/characters`, `memory/prompts`, `memory/episodes`, `memory/pending`;
- сохранять locked canon;
- расширять expandable canon только без противоречий;
- отправлять uncertain facts в pending notes;
- записывать accepted episode summaries в `memory/episodes/episode_<number>_summary.md`;
- разделять proposed memory updates на accepted updates, pending review и rejected / do not use;
- не переписывать silently ключевые locked canon files;
- использовать будущего Lore Keeper / Memory Curator только как reviewable automation, а не как скрытый переписыватель канона.

## 6. Как это работает

Это documentation-only изменение.

Код production pipeline, MemoryLoader, агенты, external integrations и approved canon files не изменялись.

Документ задает будущий workflow для человеческих и агентных задач, но не реализует нового агента и не добавляет runtime behavior.

## 7. Проверки и тесты

Выполнены легкие проверки:

- подтверждено существование `docs/EPISODE_MEMORY_WORKFLOW.md`;
- подтверждено, что файл читается как UTF-8;
- проверено наличие обязательных фрагментов про `episode_<number>_summary.md` и `Future Implementation Notes`;
- проверено, что `__pycache__` не появился;
- проверено, что production artifacts не создавались.

Результат проверки:

```text
episode_memory_workflow_doc_ok
```

Smoke-тесты pipeline не запускались, потому что задача была строго documentation only и код не менялся.

## 8. Подтверждение по lore

Новый lore не придумывался.

Approved canon files не переписывались и не расширялись.

Пример The Origin System использует только факты, прямо указанные в задании: Episode 1 содержит public humiliation, system awakening и первый retreat Lin Jian.

## 9. Слабые места

- Workflow пока не автоматизирован.
- `memory/episodes/` и `memory/pending/` описаны как будущий preferred workflow, но отдельный Lore Keeper / Memory Curator agent не создан.
- Нет формального JSON/Markdown schema для episode summary и pending notes; пока это документационный шаблон.

## 10. Рекомендуемый следующий шаг

Следующий безопасный шаг - отдельной задачей создать schema/documentation contract для `memory/episodes/*_summary.md` и `memory/pending/*.md`, не реализуя агента и не изменяя pipeline.

## 11. Требуется ли человеческое ревью

Да, ревью желательно. Документ определяет будущую дисциплину работы с каноном и должен совпадать с ожиданиями проекта.
