# Design Review Agent
Агент для проверки соответствия верстки дизайну

| Среда | Как подключить |
|--------|----------------|
| **Любая** | Каноничные правила лежат в [`DESIGN_REVIEW_AGENT.md`](DESIGN_REVIEW_AGENT.md) — скопируй текст в system / project instructions или прикрепи файл к первому сообщению. |
| **Cursor** | Автоматически: `.cursor/rules/design-review-agent.mdc` + Skill `.cursor/skills/design-review/`. Команды `/design-review`, `/design-review-start`. |
| **Claude** (Projects / веб) | Вставь содержимое `DESIGN_REVIEW_AGENT.md` в инструкции проекта или начни чат с: «Следуй инструкциям из прикреплённого DESIGN_REVIEW_AGENT.md». |
| **Codex / ChatGPT** | Custom instructions или первое сообщение + вложение `DESIGN_REVIEW_AGENT.md`; затем режим `1–4` и входные данные. |

Универсальная фраза для старта в любом чате: **«Запусти дизайн-ревью по DESIGN_REVIEW_AGENT.md, режим N»** (подставь N или попроси меню)

## Команды

- `/design-review` — slash-команда Skill для запуска сценария дизайн-ревью
- `/design-review-start` — запуск и выбор режима сравнения
- `/design-review-help` — справка по режимам и входным данным
- `/design-review-run` — запустить проверку, если входные данные уже готовы
- `/design-review-report` — вывести отчет в компактном формате
- `/design-review-clean` — удалить все файлы в `DESIGN REVIEW REPORT/`, кроме `.gitkeep`

Поддерживается legacy-команда `start design review`, но рекомендуется использовать префикс `/design-review-`

## Режимы сравнения

1. Скриншот из браузера vs картинка дизайна
2. Скриншот из браузера vs ссылка на Figma
3. Ссылка на веб-страницу vs картинка дизайна
4. Ссылка на веб-страницу vs ссылка на Figma

## Как использовать

1. Открой проект в Cursor
2. Напиши `/design-review` (или `/design-review-start`)
3. Выбери режим: `1`, `2`, `3` или `4`
4. Передай обязательные входные данные для выбранного режима
5. Получи отчет с визуальными пометками неточностей

## Что в отчете

- Сводка: score + critical/major/minor
- Ключевые расхождения: до 8 самых важных несоответствий
- Визуальные пометки: зоны расхождений
- Итог: ready или needs fixes


## Папка результатов

Все артефакты лежат **в одной папке** `DESIGN REVIEW REPORT/` (без вложенных `reports/` и `annotated/`):

- `review-YYYYMMDD-HHMM.md` — текстовый отчёт
- `annotated-YYYYMMDD-HHMM.png` — картинка с пометками

При коллизии имён добавляй суффикс `-01`, `-02` и т.д.

Очистка: `/design-review-clean` или фраза в любом чате с каноном: «Очисти DESIGN REVIEW REPORT по DESIGN_REVIEW_AGENT.md»
