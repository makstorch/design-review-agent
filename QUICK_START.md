# Quick Start

**Подготовь локальную папку проекта (любой вариант):**

1) `git -C "design-review-agent" pull || git clone https://github.com/makstorch/design-review-agent.git && cd "design-review-agent"`  
2) или скачай архив (`.zip`), если не работаешь с git, и распакуй `design-review-agent`.

**Не Cursor?** Открой [`DESIGN_REVIEW_AGENT.md`](DESIGN_REVIEW_AGENT.md), вставь в инструкции проекта или прикрепи к чату и напиши: «Запусти процесс дизайн-ревью».

1. Напиши в чат: `/design-review` или `/design-review-start`
2. Агент сам проверит Python-окружение (`preflight`)
3. Если окружение не готово, подтверди авто-установку/восстановление в чате
4. Выбери режим сравнения: `1`, `2`, `3` или `4`
5. Передай нужные данные для выбранного режима
6. Получи отчет с визуальными пометками

Режимы:
1) Скриншот из браузера vs картинка дизайна
2) Скриншот из браузера vs ссылка на Figma
3) Ссылка на веб-страницу vs картинка дизайна
4) Ссылка на веб-страницу vs ссылка на Figma


Файлы сохраняются в `DESIGN REVIEW REPORT/` с именами `review-…` и `annotated-…` (см. README).

Очистить папку: `/design-review-clean` (остаётся только `.gitkeep`).
