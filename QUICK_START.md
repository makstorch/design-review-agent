# Quick Start

**Подготовить локальную папку проекта:**
`git -C "design-review-agent" pull || git clone https://github.com/makstorch/design-review-agent.git && cd "design-review-agent"`

**Если у сервиса нет доступа к работе с git:** сначала скачай репозиторий в архиве (`.zip`) или подготовь папку `design-review-agent`, затем передай эти файлы в сервис.

**Не Cursor?** Открой [`DESIGN_REVIEW_AGENT.md`](DESIGN_REVIEW_AGENT.md), вставь в инструкции проекта или прикрепи к чату и напиши: «Запусти процесс дизайн-ревью».

1. Напиши в чат: `/design-review` или `/design-review-start`
2. Выбери режим сравнения: `1`, `2`, `3` или `4`
3. Передай нужные данные для выбранного режима
4. Получи отчет с визуальными пометками

Режимы:
1) Скриншот из браузера vs картинка дизайна
2) Скриншот из браузера vs ссылка на Figma
3) Ссылка на веб-страницу vs картинка дизайна
4) Ссылка на веб-страницу vs ссылка на Figma


Файлы сохраняются в `DESIGN REVIEW REPORT/` с именами `review-…` и `annotated-…` (см. README).

Очистить папку: `/design-review-clean` (остаётся только `.gitkeep`).
