# Отчет Codex: JSON Schema validation layer

## 1. Название задачи

Add JSON Schema validation layer.

## 2. Дата и время

2026-07-02 21:44:09 Europe/Budapest.

## 3. Созданные файлы

- `core/validation/__init__.py` — публичные exports validation layer.
- `core/validation/json_schema.py` — минимальный локальный JSON Schema validator без внешних зависимостей.
- `core/validation/schemas.py` — runtime-схемы JSON-контрактов первого deterministic pipeline.
- `core/validation/artifacts.py` — привязка pipeline stages к JSON-артефактам и схемам.
- `tests/smoke_validation_layer.py` — smoke-тест прямой проверки validator и artifact validator.
- `reports/codex/20260702_214409_json_schema_validation_layer.md` — текущий отчет по выполненной задаче.

## 4. Измененные файлы

- `core/director/studio_director.py` — добавлена post-stage валидация JSON-артефактов перед отметкой стадии как завершенной.
- `tests/smoke_publisher.py` — добавлены проверки, что validation metadata сохраняется в `production_task.json`.
- `docs/TASK_QUEUE.md` — задача JSON Schema validation layer отмечена выполненной, следующим активным пунктом оставлен `Resume pipeline from existing production_task.json`.

## 5. Что реализовано

Добавлен локальный validation layer для JSON-контрактов первого deterministic pipeline.

Валидатор поддерживает достаточный для текущего проекта subset JSON Schema:

- `type`;
- `required`;
- `properties`;
- `items`;
- `enum`;
- `const`;
- `minItems`;
- `additionalProperties: false`.

Схемы добавлены для:

- `episode_plan.json`;
- `scene_prompts.json`;
- `images/image_manifest.json`;
- `voice/voice_manifest.json`;
- `video/video_manifest.json`;
- `episode_report.json`;
- `final/metadata.json`.

`episode_script.md` пока не валидируется JSON Schema, потому что это Markdown-контракт. Для него validation result помечается как `skipped`.

## 6. Как это работает

После успешного выполнения агента Studio Director вызывает `DefaultArtifactValidator.validate_stage(...)`.

Если для стадии есть JSON-контракт:

- артефакт загружается с диска;
- проверяется по runtime-схеме;
- результат сохраняется в `metadata.stage_results.<stage>.metadata.validation`;
- стадия завершается только если validation result успешен.

Если JSON-артефакт отсутствует, поврежден или не проходит схему, Studio Director превращает результат стадии в:

```text
status = validation_failed
```

и останавливает pipeline без падения процесса.

Если для стадии нет JSON Schema-контракта, как у `script_writer`, validation result сохраняется как `skipped`.

## 7. Проверяемые артефакты

Validation layer проверяет следующие stage outputs:

- `story_architect` -> `episode_plan.json`;
- `prompt_engineer` -> `scene_prompts.json`;
- `image_director` -> `images/image_manifest.json`;
- `voice_director` -> `voice/voice_manifest.json`;
- `video_editor` -> `video/video_manifest.json`;
- `analytics` -> `episode_report.json`;
- `publisher` -> `final/metadata.json`.

## 8. Как обновляется production_task.json

Каждый `stage_results` теперь содержит блок:

```json
"validation": {
  "success": true,
  "schema_name": "...",
  "artifact_path": "...",
  "skipped": false,
  "issues": []
}
```

Для `script_writer` сохраняется `skipped: true`, потому что его текущий output — Markdown.

## 9. Что не было реализовано

Не реализовывались будущие задачи:

- resume pipeline;
- улучшение memory usage;
- real AI provider adapters;
- внешние API;
- реальная генерация медиа;
- публикация на платформы.

Также не подключалась внешняя библиотека `jsonschema`, чтобы не добавлять зависимость и не требовать сетевой установки.

## 10. Выполненные проверки и тесты

Были выполнены проверки:

- синтаксис Python-файлов через AST-парсинг: успешно;
- `tests/smoke_validation_layer.py`: успешно;
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
- внешние API не подключались.

## 11. Слабые места

- Валидатор покрывает только subset JSON Schema, а не полный стандарт.
- Runtime-схемы пока находятся в Python-коде, а не в отдельных `.schema.json` файлах.
- Markdown-контракт `episode_script.md` пока не имеет отдельного структурного валидатора.
- Схемы намеренно минимальны и проверяют базовую совместимость, а не все бизнес-правила.
- Нет автоматической синхронизации между `docs/schemas/*.md` и runtime-схемами.

## 12. Рекомендуемый следующий шаг

Следующий пункт очереди — `Resume pipeline from existing production_task.json`. Перед его реализацией полезно сохранить текущий validation layer как обязательную проверку при resume, чтобы восстановленный pipeline не продолжал работу с поврежденными артефактами.

## 13. Требуется ли человеческое ревью

Да, человеческое ревью желательно. Изменение влияет на центральный orchestration path: теперь JSON-артефакты проходят validation gate перед переходом к следующей стадии. Особенно стоит проверить, достаточно ли строгие текущие runtime-схемы и стоит ли на следующем этапе вынести их в отдельные `.schema.json` файлы.
