# Design Review Help

Команды:
- /design-review-start
- /design-review-help
- /design-review-run
- /design-review-report
- /design-review-clean
- /design-review-update

Режимы сравнения:
1) Скриншот из браузера vs картинка дизайна
   Вход: скриншот из браузера + картинка дизайна

2) Скриншот из браузера vs ссылка на Figma
   Вход: скриншот из браузера + ссылка на FIGMA

3) Ссылка на веб-страницу vs картинка дизайна
   Вход: URL + картинка дизайна

4) Ссылка на веб-страницу vs ссылка на Figma
   Вход: URL + ссылка на FIGMA

Отчет:
- score
- critical/major/minor
- ключевые расхождения
- визуальные пометки
- итоговый вердикт


Сохранение результатов (всё в одной папке, **один timestamp**):
- отчет: `DESIGN REVIEW REPORT/review-YYYYMMDD-HHMM.md`
- графика (обязательно): `DESIGN REVIEW REPORT/annotated-YYYYMMDD-HHMM.png` — через `scripts/annotate_review.py` или генератор изображений среды

PDF для команды:
- `python3 scripts/review_to_pdf.py "DESIGN REVIEW REPORT/review-YYYYMMDD-HHMM.md"` → `review-*.pdf`
- зависимости: `scripts/requirements-pdf.txt`

Очистка (`/design-review-clean`):
- удаляется всё в `DESIGN REVIEW REPORT/`, кроме `.gitkeep`


Формат служебных сообщений:
- старт: «🥷 Design Review Agent v1.0 by makstorch»
- перед запуском: «✅ Принял URL и макет»
- завершение: «✅ Процесс дизайн-ревью завершен»
- после завершения: список команд для следующего запуска, без вопросов «если хочешь…»


Если данных недостаточно для режима:
- агент пишет, каких полей не хватает, и НЕ запускает пайплайн до полного ввода.

Обновление агента:
- /design-review-update
- Команда одной строкой: `git -C "design-review-agent" pull || git clone https://github.com/makstorch/design-review-agent`
- После обновления: `Developer: Reload Window`

