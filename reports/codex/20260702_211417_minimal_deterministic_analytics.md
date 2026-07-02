# Отчет Codex: minimal deterministic Analytics

## 1. Название задачи

Implement minimal deterministic Analytics.

## 2. Дата и время

2026-07-02 21:14:17 Europe/Budapest.

## 3. Созданные файлы

- `agents/analytics/agent.py` — первая исполняемая реализация Analytics.
- `tests/smoke_analytics.py` — smoke-тест полного прохода пайплайна до Analytics.
- `reports/codex/20260702_211417_minimal_deterministic_analytics.md` — текущий отчет по выполненной задаче.

## 4. Измененные файлы

- `tests/smoke_story_architect.py` — ожидание финальной остановки обновлено до `publisher`, потому что пайплайн теперь проходит Analytics.
- `tests/smoke_script_writer.py` — ожидание финальной остановки обновлено до `publisher`.
- `tests/smoke_prompt_engineer.py` — ожидание финальной остановки обновлено до `publisher`.
- `tests/smoke_image_director.py` — ожидание финальной остановки обновлено до `publisher`.
- `tests/smoke_voice_director.py` — ожидание финальной остановки обновлено до `publisher`.
- `tests/smoke_video_editor.py` — ожидание финальной остановки обновлено до `publisher`.
- `docs/TASK_QUEUE.md` — задача Analytics отмечена выполненной, текущее состояние пайплайна дополнено `episode_report.json`, следующим активным пунктом оставлен Publisher.

## 5. Что реализовано

Реализован минимальный детерминированный Analytics без внешних API, без подключения платформенной аналитики и без сетевых интеграций.

Агент читает `production_task.json`, `episode_plan.json`, `episode_script.md`, `scene_prompts.json`, `images/image_manifest.json`, `voice/voice_manifest.json` и `video/video_manifest.json`. На их основе он создает локальный `episode_report.json` со сводкой по стадиям, артефактам, количеству сцен, статусам planned-only ассетов, стоимости внешних API и базовыми validation notes.

Отчет явно фиксирует, что реальные изображения, аудио и видео не были сгенерированы: это по-прежнему deterministic local pipeline.

## 6. Как это работает

Studio Director не знает об Analytics напрямую. Выполнение идет через существующую архитектуру:

- `core/pipeline/stages.py` уже содержит стадию `analytics`.
- `PipelineManager` берет текущую стадию из `ProductionTask`.
- `FileSystemAgentRegistry` ищет `agents/analytics/agent.py`.
- Модуль агента предоставляет фабрику `create_agent()`.
- Возвращенный объект реализует метод `execute(task, context)` и совместим с интерфейсом `AgentExecutor`.

Архитектура Studio Director, PipelineManager и AgentRegistry не изменялась.

## 7. Где сохраняются analytics-артефакты

Analytics сохраняет результат строго через `ProductionTask.output_directory`:

```text
projects/<Project>/production/tasks/<episode>/<task_id>/episode_report.json
```

Отдельная директория `analytics/` не создавалась, потому что `FIRST_PIPELINE.md` и текущая стадия ожидают `episode_report.json` как основной output Analytics.

## 8. Как обновляется production_task.json

После успешного выполнения Analytics существующий PipelineManager и Studio Director обновляют `production_task.json`:

- добавляют `analytics` в `completed_stages`;
- удаляют `analytics` из `pending_stages`;
- устанавливают `current_stage` в `publisher`;
- устанавливают статус `Waiting for Publisher implementation.`;
- сохраняют результат агента в `metadata.stage_results.analytics`.

Метаданные результата включают путь к `episode_report.json`, количество сцен, `pipeline_status` и локальный статус `analytics_status`.

## 9. Что происходит, когда Publisher отсутствует

После Analytics пайплайн переходит к стадии `publisher`. Так как `agents/publisher/agent.py` не реализован, `FileSystemAgentRegistry` возвращает безопасный missing-agent executor.

Пайплайн не падает, а завершает текущий запуск со статусом:

```text
Waiting for Publisher implementation.
```

Это соответствует правилу разработки по одному production department за запуск.

## 10. Выполненные проверки и тесты

Были выполнены проверки:

- синтаксис Python-файлов через AST-парсинг: успешно;
- graceful failure Analytics при отсутствии обязательных входных файлов: успешно;
- `tests/smoke_analytics.py`: успешно;
- `tests/smoke_story_architect.py`: успешно;
- `tests/smoke_script_writer.py`: успешно;
- `tests/smoke_prompt_engineer.py`: успешно;
- `tests/smoke_image_director.py`: успешно;
- `tests/smoke_voice_director.py`: успешно;
- `tests/smoke_video_editor.py`: успешно.

Дополнительно проверено:

- temporary production artifacts удаляются после smoke-тестов;
- запуск выполнялся с `PYTHONDONTWRITEBYTECODE=1`, чтобы не оставлять `__pycache__`;
- внешние API не подключались;
- `agents/publisher/agent.py` не реализован в рамках этой задачи.

## 11. Слабые места

- Analytics пока считает только локальную deterministic-сводку, а не реальные метрики аудитории или платформы.
- Нет JSON Schema-валидации входных контрактов.
- Отчет не содержит checksum-реестр артефактов.
- Нет измерения реального времени выполнения стадий.
- Нет resume-механизма и нет накопительной аналитики между эпизодами.

## 12. Рекомендуемый следующий шаг

Следующий пункт очереди — реализовать минимальный детерминированный Publisher. Он должен читать `episode_report.json` и production artifacts, создавать финальную структуру эпизода без загрузки на внешние платформы и завершать локальный deterministic pipeline.

## 13. Требуется ли человеческое ревью

Да, человеческое ревью желательно. Изменение расширяет фактический end-to-end smoke-пайплайн и меняет ожидаемую точку остановки всех существующих smoke-тестов. Особенно стоит проверить, достаточно ли информативен формат `episode_report.json` для будущего Publisher и последующей JSON Schema-валидации.
