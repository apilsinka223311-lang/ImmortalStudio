# Отчет Codex: minimal deterministic Voice Director

## 1. Название задачи

Implement minimal deterministic Voice Director.

## 2. Дата и время

2026-07-02 14:38:18 Europe/Budapest.

## 3. Созданные файлы

- `agents/voice_director/agent.py` — первая исполняемая реализация Voice Director.
- `tests/smoke_voice_director.py` — smoke-тест полного прохода пайплайна до Voice Director.
- `reports/codex/20260702_143818_minimal_deterministic_voice_director.md` — текущий отчет по выполненной задаче.

## 4. Измененные файлы

- `tests/smoke_story_architect.py` — ожидание финальной остановки обновлено до `video_editor`, потому что пайплайн теперь проходит Voice Director.
- `tests/smoke_script_writer.py` — ожидание финальной остановки обновлено до `video_editor`.
- `tests/smoke_prompt_engineer.py` — ожидание финальной остановки обновлено до `video_editor`.
- `tests/smoke_image_director.py` — ожидание финальной остановки обновлено до `video_editor`.
- `docs/TASK_QUEUE.md` — задача Voice Director отмечена выполненной, текущее состояние пайплайна дополнено `voice/voice_manifest.json`, следующим активным пунктом оставлен Video Editor.

## 5. Что реализовано

Реализован минимальный детерминированный Voice Director без внешних API, без ElevenLabs, без OpenAI и без генерации аудио.

Агент читает `episode_script.md`, `scene_prompts.json` и `images/image_manifest.json`, создает директорию `voice/`, формирует по одному JSON-плану озвучки на каждую сцену и создает общий `voice/voice_manifest.json`.

Файлы `.wav` и `.mp3` намеренно не создаются. В планах хранится только будущий путь `planned_output_file`, а `audio_status` явно равен `planned_not_generated`.

Каждый план сцены содержит `scene_id`, `scene_title`, `source_voice_prompt`, `narration_plan`, `dialogue_plan`, `voice_style`, `pacing`, `emotion`, `planned_output_file`, `audio_status`, `continuity_notes`, `generation_notes` и `metadata`.

## 6. Как Voice Director обнаруживается и выполняется

Studio Director не знает о Voice Director напрямую. Выполнение идет через существующую архитектуру:

- `core/pipeline/stages.py` уже содержит стадию `voice_director`.
- `PipelineManager` берет текущую стадию из `ProductionTask`.
- `FileSystemAgentRegistry` ищет `agents/voice_director/agent.py`.
- Модуль агента предоставляет фабрику `create_agent()`.
- Возвращенный объект реализует метод `execute(task, context)` и совместим с интерфейсом `AgentExecutor`.

Такой подход сохраняет расширяемость: будущие агенты по-прежнему подключаются через файловый реестр, без прямого изменения Studio Director.

## 7. Где сохраняются voice-артефакты

Все voice-артефакты сохраняются строго через `ProductionTask.output_directory`:

```text
projects/<Project>/production/tasks/<episode>/<task_id>/voice/
```

Внутри создаются:

- `voice/voice_manifest.json`;
- `voice/scene_001.json`;
- `voice/scene_002.json`;
- `voice/scene_003.json`;
- другие `scene_*.json`, если входной `scene_prompts.json` содержит больше сцен.

Файлы `.wav` и `.mp3` не создаются.

## 8. Как обновляется production_task.json

После успешного выполнения Voice Director существующий PipelineManager и Studio Director обновляют `production_task.json`:

- добавляют `voice_director` в `completed_stages`;
- удаляют `voice_director` из `pending_stages`;
- устанавливают `current_stage` в `video_editor`;
- устанавливают статус `Waiting for Video Editor implementation.`;
- сохраняют результат агента в `metadata.stage_results.voice_director`.

Метаданные результата включают пути к `episode_script.md`, `scene_prompts.json`, `images/image_manifest.json`, `voice/voice_manifest.json`, количество сцен и статус `planned_not_generated`.

## 9. Что происходит, когда Video Editor отсутствует

После Voice Director пайплайн переходит к стадии `video_editor`. Так как `agents/video_editor/agent.py` не реализован, `FileSystemAgentRegistry` возвращает безопасный missing-agent executor.

Пайплайн не падает, а завершает текущий запуск со статусом:

```text
Waiting for Video Editor implementation.
```

Это сохраняет текущую стратегию разработки: каждый новый production department добавляется отдельным вертикальным срезом.

## 10. Выполненные проверки и тесты

Были выполнены проверки:

- синтаксис Python-файлов через AST-парсинг: успешно;
- graceful failure Voice Director при отсутствии обязательных входных файлов: успешно;
- `tests/smoke_voice_director.py`: успешно;
- `tests/smoke_story_architect.py`: успешно;
- `tests/smoke_script_writer.py`: успешно;
- `tests/smoke_prompt_engineer.py`: успешно;
- `tests/smoke_image_director.py`: успешно.

Дополнительно проверено:

- temporary production artifacts удаляются после smoke-тестов;
- `__pycache__` не остается при запуске с `PYTHONDONTWRITEBYTECODE=1`;
- `.wav` и `.mp3` файлы не создаются;
- `agents/video_editor/agent.py` не реализован в рамках этой задачи.

## 11. Слабые места

- Voice Director пока создает только планы, а не реальные аудиофайлы.
- Разбор `episode_script.md` минимальный: агент берет контекст сцены как текстовый фрагмент, а не как полноценную структурированную модель.
- Нет JSON Schema-валидации входных `scene_prompts.json` и `image_manifest.json`.
- Нет отдельной доменной модели для voice manifest за пределами локального dataclass.
- Нет resume-механизма для продолжения уже созданной production task.

## 12. Рекомендуемый следующий шаг

Следующий пункт очереди — реализовать минимальный детерминированный Video Editor. Он должен читать image-планы и voice-планы, создавать структурированный video assembly plan без генерации MP4 и останавливать пайплайн на следующем отсутствующем агенте.

## 13. Требуется ли человеческое ревью

Да, человеческое ревью желательно. Изменение расширяет фактический end-to-end smoke-пайплайн и меняет ожидаемую точку остановки всех существующих smoke-тестов. Особенно стоит проверить, достаточно ли удобен формат `voice/voice_manifest.json` для будущего реального Voice Director и Video Editor.
