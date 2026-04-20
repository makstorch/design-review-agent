# Design Review Agent v2.0

Готовый инструмент для проведения дизайн-ревью верстки: сравнивает реализацию с макетом/референсом, подсвечивает зоны расхождений и сохраняет отчет в `DESIGN REVIEW REPORT/`.

## Запуск

Сначала подготовь папку проекта одним из двух способов:

1. **Есть доступ к git (рекомендуется):**  
   `git -C "design-review-agent" pull || git clone https://github.com/makstorch/design-review-agent.git && cd "design-review-agent"`
2. **Если с git не работаешь:** скачай репозиторий архивом (`.zip`), распакуй и используй локальную папку `design-review-agent`.

Для работы агента нужна Python-среда. При запуске `/design-review-start` агент сам делает preflight-проверку окружения и, если нужно, предлагает автоматическую установку/восстановление — достаточно подтверждать действия в чате.

Если хочешь установить все вручную заранее (macOS):

1. `install.command` — первичная установка Python 3.12 + `.venv` + зависимостей
2. `check-env.command` — проверка готовности (`OK`)
3. `repair.command` — восстановление окружения после ошибок/обновлений

Для Cursor используй slash-команды ниже.  
Для Claude / Codex / ChatGPT:
  1. прикрепи файл `DESIGN_REVIEW_AGENT.md` в чат;
  2. отправь готовый промпт:

```text
Следуй инструкциям из прикрепленного файла DESIGN_REVIEW_AGENT.md.
Запусти процесс дизайн-ревью.
```

## Команды для Cursor

- `/design-review` — быстрый запуск сценария ревью
- `/design-review-start` — старт и выбор режима
- `/design-review-help` — краткая справка
- `/design-review-run` — запуск, если вход уже передан
- `/design-review-report` — показать текущий формат отчета
- `/design-review-clean` — очистить `DESIGN REVIEW REPORT/` (кроме `.gitkeep`)
- `/design-review-update` — показать команду обновления

Поддерживается legacy-команда: `start design review`.

## Режимы сравнения

1. Скриншот из браузера vs картинка дизайна
2. Скриншот из браузера vs ссылка на Figma
3. Ссылка на веб-страницу vs картинка дизайна
4. Ссылка на веб-страницу vs ссылка на Figma

После выбора режима и передачи нужных артефактов вы получите:
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
`git -C "design-review-agent" pull || git clone https://github.com/makstorch/design-review-agent.git`
