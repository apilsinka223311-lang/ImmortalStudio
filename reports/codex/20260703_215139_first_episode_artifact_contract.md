# Отчет Codex: First episode artifact contract

## 1. Название задачи

Foundation v1.1 - add first episode artifact contract.

## 2. Дата и время

2026-07-03 21:51:39 Europe/Budapest.

## 3. Созданные файлы

- `docs/contracts/FIRST_CANON_EPISODE_CONTRACT.md` - контракт минимальных canon beats и artifact expectations для The Origin System Episode 1.
- `tests/smoke_first_episode_contract.py` - smoke-тест, валидирующий generated artifacts against the Episode 1 contract.
- `reports/codex/20260703_215139_first_episode_artifact_contract.md` - текущий отчет по задаче.

## 4. Измененные файлы

- `docs/TASK_QUEUE.md` - добавлен выполненный manual/technical foundation item `Add first episode artifact contract`.

## 5. Что было реализовано

Добавлен небольшой явный contract для первого canon-driven episode sample.

Контракт фиксирует required Episode 1 beats:

- Lin Mo awakens during public humiliation;
- scene connected to Azure Sword Clan;
- Lin Jian humiliates Lin Mo as a cripple/disgrace;
- The Origin System initializes;
- spiritual channels are artificially severed;
- Foundation fragment is detected;
- Lin Jian's weak point is analyzed;
- Lin Mo counters for the first time;
- system shop must not appear;
- Lin Mo must not become overpowered.

Также описаны expectations для:

- `production_task.json -> metadata.memory_context`;
- `episode_plan.json`;
- `scene_prompts.json`;
- `final/metadata.json`.

## 6. Как работает smoke-тест

`tests/smoke_first_episode_contract.py` запускает существующий deterministic local pipeline для `ImmortalAcademy` с Episode 1 request и проверяет:

- required beats present in `episode_plan.json` or generated prompt artifacts;
- approved canon references are present in `memory_context`;
- final metadata exists after Publisher;
- forbidden positive system-shop phrases are absent;
- forbidden overpowered Lin Mo phrases are absent;
- temporary production task artifacts are removed after the test.

Проверка намеренно остается foundation-level: она не требует полноценного story-aware generation engine и не заставляет агентов писать красивую прозу. Она защищает минимальные canon references и forbidden changes.

## 7. Проверки и тесты

Выполнены проверки:

- Python syntax check через AST: успешно, проверено 46 файлов;
- `tests/smoke_first_episode_contract.py`: успешно;
- `tests/smoke_first_canon_episode_sample.py`: успешно;
- `tests/smoke_approved_memory_canon_loading.py`: успешно;
- `tests/smoke_validation_layer.py`: успешно;
- `tests/smoke_resume_pipeline.py`: успешно.

Дополнительно проверено:

- temporary production artifacts очищаются smoke-тестами;
- `__pycache__` не должен оставаться, так как проверки запускались с `PYTHONDONTWRITEBYTECODE=1`.

## 8. Подтверждения по ограничениям

Внешние API не использовались.

Future Tasks не реализовывались.

Production pipeline не редизайнился.

MemoryLoader не редизайнился.

Lore Keeper agent не создавался.

Episode Writer agent не создавался.

Approved canon files не переписывались.

Новый lore не придумывался.

Lin Mo не делался overpowered.

System shop не добавлялся.

## 9. Слабые места

- Контракт проверяет Foundation-level generated artifacts через deterministic text checks, а не через полноценную структурную story schema.
- Текущие агенты все еще используют input idea и memory references как главный источник canon specificity.
- Negative checks специально ограничены явными forbidden phrases, чтобы не конфликтовать с разрешенной locked rule phrase `The Origin System has no shop`.

## 10. Рекомендуемый следующий шаг

Следующий безопасный шаг - вынести общую test helper-логику для canon sample/contract smoke-тестов, если таких контрактов станет больше. Пока дублирование небольшое и оставлено явным для простоты ревью.

## 11. Требуется ли человеческое ревью

Да, ревью желательно. Контракт становится regression guard для будущих изменений Story Architect и Prompt Engineer, поэтому важно подтвердить, что required beats и forbidden checks соответствуют ожиданиям проекта.
