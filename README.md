# Design Review Agent v1.0

Готовый инструмент для проведения дизайн-ревью верстки: сравнивает реализацию с макетом/референсом, подсвечивает зоны расхождений и сохраняет отчет в `DESIGN REVIEW REPORT/`.

## Команды для Cursor

- `/design-review` — быстрый запуск сценария ревью
- `/design-review-start` — старт и выбор режима
- `/design-review-help` — краткая справка
- `/design-review-run` — запуск, если вход уже передан
- `/design-review-report` — показать текущий формат отчета
- `/design-review-clean` — очистить `DESIGN REVIEW REPORT/` (кроме `.gitkeep`)
- `/design-review-update` — показать команду обновления

Поддерживается legacy-команда: `start design review`.

## Запуск

- **Cursor**: используй slash-команды выше.
- **Claude / Codex / ChatGPT**:
  1. прикрепи файл `DESIGN_REVIEW_AGENT.md` в чат;
  2. отправь готовый промпт:

```text
Следуй инструкциям из прикрепленного файла DESIGN_REVIEW_AGENT.md.
Запусти дизайн-ревью, режим 1-4 уточни у меня.
```

## Режимы сравнения и результат

### Режимы сравнения
1. Скриншот из браузера vs картинка дизайна
2. Скриншот из браузера vs ссылка на Figma
3. Ссылка на веб-страницу vs картинка дизайна
4. Ссылка на веб-страницу vs ссылка на Figma

### Что на выходе
- краткое резюме с процентом соответствия
- список несоответствий по блокам
- PNG с отмеченными зонами ошибок
- отчет в `md` и `pdf`

### Папка результатов
Все артефакты сохраняются в `DESIGN REVIEW REPORT/`:
- `review-YYYYMMDD-HHMM.md`
- `annotated-YYYYMMDD-HHMM.png`
- `review-YYYYMMDD-HHMM.pdf`

## Обновление

Команда одной строкой:
`git -C "design-review-agent" pull || git clone https://github.com/makstorch/design-review-agent`
