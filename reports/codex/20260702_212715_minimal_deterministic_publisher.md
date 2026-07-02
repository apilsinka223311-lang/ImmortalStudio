# Отчет Codex: minimal deterministic Publisher

## 1. Название задачи

Implement minimal deterministic Publisher.

## 2. Дата и время

2026-07-02 21:27:15 Europe/Budapest.

## 3. Созданные файлы

- `agents/publisher/agent.py` — первая исполняемая реализация Publisher.
- `tests/smoke_publisher.py` — smoke-тест полного deterministic pipeline до завершения.
- `reports/codex/20260702_212715_minimal_deterministic_publisher.md` — текущий отчет по выполненной задаче.

## 4. Измененные файлы

- `tests/smoke_story_architect.py` — ожидание финального состояния обновлено до `completed`.
- `tests/smoke_script_writer.py` — ожидание финального состояния обновлено до `completed`.
- `tests/smoke_prompt_engineer.py` — ожидание финального состояния обновлено до `completed`.
- `tests/smoke_image_director.py` — ожидание финального состояния обновлено до `completed`.
- `tests/smoke_voice_director.py` — ожидание финального состояния обновлено до `completed`.
- `tests/smoke_video_editor.py` — ожидание финального состояния обновлено до `completed`.
- `tests/smoke_analytics.py` — ожидание финального состояния обновлено до `completed`.
- `docs/TASK_QUEUE.md` — задача Publisher отмечена выполненной, текущее состояние пайплайна дополнено `final/metadata.json`, следующим активным пунктом оставлен JSON Schema validation layer.

## 5. Что реализовано

Реализован минимальный детерминированный Publisher без внешних API, без загрузки на платформы и без создания fake media-файлов.

Агент читает `production_task.json`, `episode_plan.json`, `episode_script.md`, `scene_prompts.json`, `episode_report.json`, `images/image_manifest.json`, `voice/voice_manifest.json` и `video/video_manifest.json`.

После успешной проверки входов Publisher создает локальный пакет внутри текущей production task:

```text
final/
```

В пакет копируются исходные контракты и planning-директории `images/`, `voice/`, `video/`. Затем создаются `final/metadata.json` и `final/package_manifest.json`.

Publisher не создает `.mp4`, `.mov`, `.wav`, `.mp3` и не выполняет upload.

## 6. Как это работает

Studio Director не знает о Publisher напрямую. Выполнение идет через существующую архитектуру:

- `core/pipeline/stages.py` уже содержит последнюю стадию `publisher`.
- `PipelineManager` берет текущую стадию из `ProductionTask`.
- `FileSystemAgentRegistry` ищет `agents/publisher/agent.py`.
- Модуль агента предоставляет фабрику `create_agent()`.
- Возвращенный объект реализует метод `execute(task, context)` и совместим с интерфейсом `AgentExecutor`.

После успешного Publisher `PipelineManager.next_stage_after("publisher")` возвращает `None`, поэтому Studio Director переводит production task в `current_stage = completed` и `status = completed`.

## 7. Где сохраняются publisher-артефакты

Все publisher-артефакты сохраняются строго через `ProductionTask.output_directory`:

```text
projects/<Project>/production/tasks/<episode>/<task_id>/final/
```

Основные файлы:

- `final/metadata.json`;
- `final/package_manifest.json`;
- `final/episode_plan.json`;
- `final/episode_script.md`;
- `final/scene_prompts.json`;
- `final/episode_report.json`;
- `final/images/`;
- `final/voice/`;
- `final/video/`;
- `final/subtitles/`.

## 8. Как обновляется production_task.json

После успешного выполнения Publisher существующий PipelineManager и Studio Director обновляют `production_task.json`:

- добавляют `publisher` в `completed_stages`;
- удаляют `publisher` из `pending_stages`;
- устанавливают `current_stage` в `completed`;
- устанавливают статус `completed`;
- сохраняют результат агента в `metadata.stage_results.publisher`.

Метаданные результата включают путь к local package, `metadata.json`, `package_manifest.json`, статус `not_uploaded` и `local_package_created`.

## 9. Что происходит после Publisher

Publisher является последней стадией текущего `FIRST_PIPELINE_STAGES`. Поэтому отсутствующий downstream-agent не нужен: после успешного Publisher pipeline завершается штатно.

Внешняя публикация пока не выполняется. `metadata.json` фиксирует `upload_status = not_uploaded`, а `pipeline_status = draft`, потому что реального MP4 еще нет.

## 10. Выполненные проверки и тесты

Были выполнены проверки:

- синтаксис Python-файлов через AST-парсинг: успешно;
- graceful failure Publisher при отсутствии обязательных входных файлов: успешно;
- `tests/smoke_publisher.py`: успешно;
- `tests/smoke_story_architect.py`: успешно;
- `tests/smoke_script_writer.py`: успешно;
- `tests/smoke_prompt_engineer.py`: успешно;
- `tests/smoke_image_director.py`: успешно;
- `tests/smoke_voice_director.py`: успешно;
- `tests/smoke_video_editor.py`: успешно;
- `tests/smoke_analytics.py`: успешно.

Дополнительно проверено:

- temporary production artifacts удаляются после smoke-тестов;
- запуск выполнялся с `PYTHONDONTWRITEBYTECODE=1`, чтобы не оставлять `__pycache__`;
- fake `.mp4` и `.mov` не создаются;
- внешние API не подключались.

## 11. Слабые места

- Publisher пока создает только локальный пакет внутри task directory, а не переносит эпизод в постоянную final-библиотеку проекта.
- `metadata.json` пока отражает planned-only pipeline, а не полноценный завершенный медиаэпизод.
- Нет checksum-реестра для copied artifacts.
- Нет JSON Schema-валидации `metadata.json`.
- Нет upload adapters и platform-specific publishing metadata.

## 12. Рекомендуемый следующий шаг

Следующий пункт очереди — `Add JSON Schema validation layer`. Его стоит реализовать до подключения реальных генераторов, чтобы все agent contracts проверялись автоматически до перехода к следующей стадии.

## 13. Требуется ли человеческое ревью

Да, человеческое ревью желательно. Изменение впервые доводит deterministic local pipeline до состояния `completed`, поэтому важно проверить, подходит ли структура `final/metadata.json` и локального пакета для дальнейшего слоя JSON Schema validation и будущего реального Publisher.
