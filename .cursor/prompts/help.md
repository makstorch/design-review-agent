# Design Review Help

Команды:
- /design-review-start
- /design-review-help
- /design-review-run
- /design-review-report
- /design-review-clean

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


Сохранение результатов (всё в одной папке):
- отчет: `DESIGN REVIEW REPORT/review-YYYYMMDD-HHMM.md`
- графика: `DESIGN REVIEW REPORT/annotated-YYYYMMDD-HHMM.png`

Очистка (`/design-review-clean`):
- удаляется всё в `DESIGN REVIEW REPORT/`, кроме `.gitkeep`
