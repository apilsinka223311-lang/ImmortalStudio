# Отчет Codex: minimal deterministic Image Director

## 1. Название задачи

Implement minimal deterministic Image Director.

## 2. Дата и время

2026-07-02 14:28:35 Europe/Budapest.

## 3. Созданные файлы

- `agents/image_director/agent.py` — первая исполняемая реализация Image Director.
- `tests/smoke_image_director.py` — smoke-тест полного прохода пайплайна до Image Director.
- `reports/codex/20260702_142835_minimal_deterministic_image_director.md` — текущий отчет по выполненной задаче.

## 4. Измененные файлы

- `tests/smoke_story_architect.py` — ожидание финальной остановки обновлено до `voice_director`, потому что теперь пайплайн проходит дальше Image Director.
- `tests/smoke_script_writer.py` — ожидание финальной остановки обновлено до `voice_director`.
- `tests/smoke_prompt_engineer.py` — ожидание финальной остановки обновлено до `voice_director`.
- `docs/TASK_QUEUE.md` — задача Image Director отмечена выполненной, текущее состояние пайплайна дополнено `images/image_manifest.json`, следующим активным пунктом оставлен Voice Director.

## 5. Что реализовано

Реализован минимальный детерминированный Image Director без внешних API и без генерации изображений.

Агент читает `scene_prompts.json`, создает директорию `images/`, формирует по одному JSON-плану изображения на каждую сцену и создает общий `images/image_manifest.json`. PNG-файлы намеренно не создаются, чтобы система не притворялась, что реальные изображения уже сгенерированы.

Каждый план сцены содержит `scene_id`, `scene_title`, `source_prompt`, `negative_prompt`, `planned_output_file`, `image_status`, `image_style`, `continuity_notes`, `generation_notes` и `metadata`. Значение `image_status` равно `planned_not_generated`.

## 6. Как Image Director обнаруживается и выполняется

Studio Director не знает о Image Director напрямую. Выполнение идет через существующую архитектуру:

- `core/pipeline/stages.py` содержит стадию `image_director`.
- `PipelineManager` берет текущую стадию из `ProductionTask`.
- `FileSystemAgentRegistry` ищет `agents/image_director/agent.py`.
- Модуль агента предоставляет фабрику `create_agent()`.
- Возвращенный объект реализует метод `execute(task, context)` и совместим с интерфейсом `AgentExecutor`.

Такой подход сохраняет расширяемость: будущие агенты можно подключать по той же схеме без прямого изменения Studio Director.

## 7. Где сохраняются image-артефакты

Все артефакты сохраняются строго через `ProductionTask.output_directory`:

```text
projects/<Project>/production/tasks/<episode>/<task_id>/images/
```

Внутри создаются:

- `images/image_manifest.json`;
- `images/scene_001.json`;
- `images/scene_002.json`;
- `images/scene_003.json`;
- другие `scene_*.json`, если входной `scene_prompts.json` содержит больше сцен.

Файлы `.png` не создаются.

## 8. Как обновляется production_task.json

После успешного выполнения Image Director существующий PipelineManager и Studio Director обновляют `production_task.json`:

- добавляют `image_director` в `completed_stages`;
- удаляют `image_director` из `pending_stages`;
- устанавливают `current_stage` в `voice_director`;
- устанавливают статус `Waiting for Voice Director implementation.`;
- сохраняют результат агента в `metadata.stage_results.image_director`.

Метаданные результата включают путь к `scene_prompts.json`, путь к `image_manifest.json`, количество сцен и статус `planned_not_generated`.

## 9. Что происходит, когда Voice Director отсутствует

После Image Director пайплайн переходит к стадии `voice_director`. Так как `agents/voice_director/agent.py` не реализован, `FileSystemAgentRegistry` возвращает безопасный missing-agent executor. Пайплайн не падает, а завершает текущий запуск со статусом:

```text
Waiting for Voice Director implementation.
```

Это соответствует текущей стратегии: каждая новая стадия добавляется отдельным вертикальным срезом.

## 10. Выполненные проверки и тесты

Были выполнены smoke-тесты:

- `tests/smoke_story_architect.py`;
- `tests/smoke_script_writer.py`;
- `tests/smoke_prompt_engineer.py`;
- `tests/smoke_image_director.py`.

Дополнительно проверены:

- синтаксис Python-файлов через AST-парсинг;
- graceful failure Image Director при отсутствии `scene_prompts.json`;
- отсутствие `__pycache__`;
- отсутствие временных production-артефактов после smoke-тестов;
- отсутствие `agents/voice_director/agent.py`;
- отсутствие созданных fake PNG-файлов.

## 11. Слабые места

- Image Director пока создает только планы, а не реальные изображения.
- Нет JSON Schema-валидации входного `scene_prompts.json`; агент ожидает корректный контракт от Prompt Engineer.
- Нет отдельной доменной модели для image plan и manifest за пределами локального dataclass.
- Нет resume-механизма для продолжения уже созданной production task.
- Smoke-тесты остаются скриптовыми, а не интегрированы в полноценный test runner.

## 12. Рекомендуемый следующий шаг

Следующий пункт очереди — реализовать минимальный детерминированный Voice Director. Он должен читать `episode_script.md` и/или `scene_prompts.json`, создавать структурированные voice-планы без генерации аудио и останавливать пайплайн на следующем отсутствующем агенте.

## 13. Требуется ли человеческое ревью

Да, человеческое ревью желательно. Изменение затрагивает поведение всего smoke-пайплайна: теперь ранние тесты проходят дальше и ожидают остановку на Voice Director. Особенно стоит проверить, достаточно ли удобен формат `images/image_manifest.json` для будущего реального Image Director.
