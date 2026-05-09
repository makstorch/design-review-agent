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


Сохранение результатов (всё в одной папке, **один timestamp**, имена по теме экрана):
- формат timestamp в именах: `DD-MM-YYYY-HH-MM` (всё через дефис; `_` отделяет slug от даты)
- отчёт: `DESIGN REVIEW REPORT/<Slug>_DD-MM-YYYY-HH-MM.md`
- графика (обязательно): `DESIGN REVIEW REPORT/<Slug>-annotated_DD-MM-YYYY-HH-MM.png`
- копии оригиналов (без перекодирования): `<Slug>-source-actual_*`, `<Slug>-source-design_*`
- если тема не определена — fallback: `review_*.md`, `annotated_*.png`, `source-*_*`

PDF для команды:
- `.venv/bin/python scripts/review_to_pdf.py "DESIGN REVIEW REPORT/<Slug>_DD-MM-YYYY-HH-MM.md"` → `<Slug>_*.pdf`
- зависимости: `scripts/requirements-pdf.txt`

Опциональный шаг после выбора режима — **дизайн-система**:
- В новой сессии агент сначала ищет в `DESIGN REVIEW REPORT/` файлы `design-system-<planet>_DD-MM-YYYY-HH-MM.md`. Если они есть, берёт самый свежий и предлагает выбор: `1` использовать его, `2` приложить новую (картинка/Figma), `3` без ДС. В чате агент называет её по «кодовому имени», например: «Нашёл сохранённую ДС *Jupiter* от 09-05-2026 13:36».
- Если кэша нет — пользователь может приложить картинку style-guide / ссылку на Figma library / пропустить (`Пропустить`, `-`).
- При новом извлечении агент сразу пинит короткий чек-лист (Buttons, Typography, Colors, Spacing, Components) в чат, присваивает ДС случайное имя из 13 планет (Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Ceres, Eris, Haumea, Makemake — и старается выбрать имя, которого ещё нет в папке) и сохраняет файл `design-system-<planet>_DD-MM-YYYY-HH-MM.md` для будущих сессий. Старые ds-файлы остаются как история.
- Чек-лист попадает в блок «Соответствие дизайн-системе» отчёта, а в пунктах «Несоответствия» появляется поле `Правило ДС: …`. Можно прокинуть готовый чек-лист в скрипт через `--design-system-notes "<...>"`.

Очистка (`/design-review-clean`):
- если в папке есть `design-system-*.md`, агент сначала предупредит и спросит подтверждение (`да` / `нет` / `сохранить ДС`)
- удаляется всё в `DESIGN REVIEW REPORT/`, кроме `.gitkeep` (и кроме `design-system-*.md` при ответе «сохранить ДС»)

Python-окружение:
- агент запускает скрипты только через `.venv/bin/python` (никогда `python3` напрямую)
- если `.venv` отсутствует или зависимости не стоят — агент предложит `./install.command` одним сообщением, без raw-стэктрейсов

Формат служебных сообщений:
- старт: «🥷 Design Review Agent v2.8 by makstorch»
- перед запуском: «✅ Принял URL и макет»
- завершение: «✅ Процесс дизайн-ревью завершен»
- после завершения: список команд для следующего запуска, без вопросов «если хочешь…»


Если данных недостаточно для режима:
- агент пишет, каких полей не хватает, и НЕ запускает пайплайн до полного ввода.

Обновление агента:
- /design-review-update
- Команда одной строкой: `git -C "design-review-agent" pull || git clone https://github.com/makstorch/design-review-agent`
- После обновления: `Developer: Reload Window`

