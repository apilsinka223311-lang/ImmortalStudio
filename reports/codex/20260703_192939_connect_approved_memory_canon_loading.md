# Отчет Codex: Connect approved creative memory canon to runtime memory loading

## 1. Название задачи

Foundation v0.7 - connect approved creative memory canon to runtime memory loading.

## 2. Дата и время

2026-07-03 19:29:39 Europe/Budapest.

## 3. Созданные файлы

- `tests/smoke_approved_memory_canon_loading.py` - smoke-тест, проверяющий, что утвержденный canon из `projects/ImmortalAcademy/memory/...` попадает в runtime `memory_context`, `episode_plan.json` и `scene_prompts.json`.
- `reports/codex/20260703_192939_connect_approved_memory_canon_loading.md` - текущий отчет по задаче.

## 4. Измененные файлы

- `core/services/memory_loader.py` - добавлена минимальная поддержка approved canon folders `memory/world`, `memory/characters` и `memory/prompts` рядом с прежними project memory folders.
- `docs/TASK_QUEUE.md` - добавлена выполненная manual/technical foundation task `Connect approved creative memory canon to runtime memory loading`.

## 5. Что было реализовано

Runtime memory loading теперь читает утвержденные canon-файлы из:

- `projects/ImmortalAcademy/memory/world/`;
- `projects/ImmortalAcademy/memory/characters/`;
- `projects/ImmortalAcademy/memory/prompts/`.

Старое поведение сохранено:

- `projects/<project>/world/` продолжает загружаться;
- `projects/<project>/characters/` продолжает загружаться;
- `projects/<project>/prompts/` продолжает загружаться;
- `projects/<project>/episodes/` продолжает загружаться как previous episodes;
- существующие поля `memory_summary` не удалялись.

Approved canon добавляется как дополнительный источник памяти с путями вида:

```text
memory/world/world_overview.md
memory/characters/lin_mo.md
memory/prompts/story_rules.md
```

Это позволяет агентам видеть, откуда именно пришел canon excerpt.

## 6. Как это работает

В `MemoryLoader.load(...)` прежние legacy sections теперь загружаются через небольшой helper `_load_memory_section(...)`.

Для каждой секции helper:

1. Загружает старую директорию проекта, например `world/`.
2. Дополнительно загружает approved canon из `memory/<section>/`.
3. Объединяет оба источника в тот же `ProjectMemory.world`, `ProjectMemory.characters` или `ProjectMemory.prompts`.

`ProjectMemory.context(...)` продолжает отдавать компактные excerpts, но стандартная длина excerpt увеличена до 640 символов. Это нужно, чтобы ключевые locked rules, например `The Origin System has no shop`, попадали в runtime context и не обрезались слишком рано.

Пустые файлы обрабатываются безопасно: они учитываются в summary, но не попадают в excerpts, потому что excerpt создается только из непустого текста.

Production pipeline, агенты, внешние интеграции и approved canon text не изменялись.

## 7. Проверки и тесты

Выполнены проверки:

- Python syntax check через AST: успешно, проверено 44 файла;
- `tests/smoke_approved_memory_canon_loading.py`: успешно;
- `tests/smoke_memory_usage.py`: успешно;
- `tests/smoke_validation_layer.py`: успешно;
- `tests/smoke_resume_pipeline.py`: успешно.

Новый smoke-тест подтвердил:

- approved world canon попадает в `memory_context`;
- world canon содержит `The Origin System` и `Fallen Star Realm`;
- character canon содержит `Lin Mo`;
- prompt/story rules содержат правило `The Origin System has no shop`;
- `memory_context` сохраняется в `production_task.json`;
- Story Architect получает canon references в `episode_plan.json`;
- Prompt Engineer получает canon references в `scene_prompts.json`;
- временные production artifacts удаляются после теста;
- `__pycache__` не остается.

## 8. Подтверждение по lore

Новый lore не придумывался.

Утвержденные canon-файлы не переписывались и не расширялись. Изменение только подключает уже существующие approved memory files к runtime memory loading.

## 9. Слабые места

- Runtime memory context все еще использует простые excerpt-выдержки, без поиска релевантности по текущей идее эпизода.
- Approved canon и legacy memory объединяются в одни секции `world`, `characters`, `prompts`; отдельного поля `approved_canon` пока нет.
- Лимит `max_files_per_section=3` остается прежним. Для текущего набора canon этого достаточно, но при росте memory может понадобиться явное ранжирование или отдельные приоритеты.

## 10. Рекомендуемый следующий шаг

Следующий безопасный шаг - наполнить или синхронизировать старые legacy memory folders только если они все еще нужны. Если canonical source теперь `projects/<project>/memory/...`, стоит отдельной задачей задокументировать это как preferred memory layout, не меняя production pipeline.

## 11. Требуется ли человеческое ревью

Да, ревью желательно. Изменение небольшое, но оно влияет на runtime context, который получают Story Architect и Prompt Engineer.
