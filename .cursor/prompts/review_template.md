# Дизайн-ревью: Feedback Modal
*(пример заполнения; реальные значения подставляются по факту)*

_Дата ревью: 09-05-2026 13:50  ·  Реализация: 1440x900 px (screenshot.png)  ·  Макет: 1440x900 px (figma · node 12:340)  ·  Тема: light_

## Краткое резюме
Вердикт: **Нужны правки**
Score: **74 / 100**
Формула: `score = max(0, 100 − критичные×10 − значимые×5 − незначительные×2)  →  100 − 1×10 − 2×5 − 3×2 = 74`
Ошибки: Критичные – 1, Значимые – 2, Незначительные – 3

**Top-3 правки по ROI** (Impact × 1/Effort, не по убыванию severity):
1. Поднять контраст body-текста с #B0B0B0 до #4A4A4A → Color/A2
2. Уменьшить border-radius primary-CTA с 12 px до 8 px → Components/A1
3. Увеличить gap между элементами формы с 12 px до 16 px → Spacing/A4

## Что сделано хорошо
- Шапка модалки пиксель-в-пиксель совпадает с макетом (logo, close-icon, padding 24 px)
- Цвета primary/surface совпадают с токенами `Brand/Primary-500` и `Surface/Base`
- Modal-overlay корректный: dimmer 60%, blur 8 px

## Ключевые расхождения

### Color

#### A2. Низкий контраст body-текста
- Уровень: Критичная
- Impact: High   ·   Effort: S
- Что должно быть: body text #4A4A4A на #FFFFFF, контраст 7.4:1
- Что по факту: #B0B0B0 на #FFFFFF, контраст 2.4:1
- Что исправить: заменить hex основного текста с #B0B0B0 на #4A4A4A
- Правило ДС: Colors.text.body = #4A4A4A

### Components

#### A1. Border-radius primary-CTA
- Уровень: Значимая
- Impact: Med   ·   Effort: S
- Что должно быть: Buttons.radius = 8 px (по чек-листу ДС)
- Что по факту: 12 px
- Что исправить: уменьшить border-radius primary-CTA с 12 px до 8 px
- Правило ДС: Buttons.radius = 8

### Spacing

#### A4. Зазор между полями формы
- Уровень: Значимая
- Impact: Med   ·   Effort: S
- Что должно быть: gap между полями формы 16 px (по сетке 4-grid)
- Что по факту: 12 px
- Что исправить: увеличить vertical gap в form-stack с 12 px до 16 px
- Правило ДС: Spacing.form-stack = 16

#### A5. Padding модалки сверху
- Уровень: Незначительная
- Impact: Low   ·   Effort: S
- Что должно быть: padding-top модалки 32 px
- Что по факту: 28 px
- Что исправить: увеличить padding-top модалки на 4 px
- Правило ДС: Spacing.modal.padding-top = 32

### Typography

#### A3. Размер заголовка модалки
- Уровень: Незначительная
- Impact: Low   ·   Effort: S
- Что должно быть: Inter 20/28, weight 600
- Что по факту: Inter 18/24, weight 600
- Что исправить: увеличить font-size заголовка с 18 px до 20 px и line-height с 24 px до 28 px
- Правило ДС: Typography.h2 = 20/28

### Other

#### A6. Footer-ссылки расположены ниже
- Уровень: Незначительная
- Impact: Low   ·   Effort: M
- Что должно быть: footer-ссылки прижаты к низу модалки на 24 px от bottom
- Что по факту: ссылки расположены на 32 px от bottom
- Что исправить: уменьшить отступ footer-ссылок от низа модалки с 32 px до 24 px

## Accessibility quick-check
- Контраст основного текста: 2.4:1 (❌ AA — нужен ≥ 4.5:1) → см. A2
- Контраст вспомогательного текста / caption: 4.6:1 (✅ AA)
- Touch target интерактивных элементов: primary-CTA 44x44 px (✅), close-icon 32x32 px (❌)
- Visible focus state: неизвестно — нужны hover/focus-стейты в исходнике
- Текст на изображениях / низкий контраст плашек: не выявлено

## Соответствие дизайн-системе

- Использованный чек-лист:
  - Buttons: radius 8, padding 12/24, primary #2D5BFF
  - Typography: Inter 12 / 14 / 16 / 20 / 24 / 32
  - Colors: primary #2D5BFF, surface #FFFFFF, text body #4A4A4A
  - Spacing: 4-grid (4 / 8 / 12 / 16 / 24 / 32)
  - Radius / shadows: radius 8, shadow elev-2 (0 4 16 rgba(0,0,0,.08))
- Нарушения:
  - A1 — Buttons.radius (правило 8, по факту 12)
  - A2 — Colors.text.body (правило #4A4A4A, по факту #B0B0B0)
  - A3 — Typography.h2 (правило 20/28, по факту 18/24)
  - A4 — Spacing.form-stack (правило 16, по факту 12)
  - A5 — Spacing.modal.padding-top (правило 32, по факту 28)

## Визуальные пометки
Файл: `DESIGN REVIEW REPORT/Feedback-Modal-annotated_09-05-2026-13-50.png`
- A1 — components
- A2 — color
- A3 — typography
- A4 — spacing
- A5 — spacing
- A6 — other

## Артефакты
- PNG c пометками: `DESIGN REVIEW REPORT/Feedback-Modal-annotated_09-05-2026-13-50.png`
- Исходный скриншот реализации: `DESIGN REVIEW REPORT/Feedback-Modal-source-actual_09-05-2026-13-50.png`
- Исходный макет дизайна: `DESIGN REVIEW REPORT/Feedback-Modal-source-design_09-05-2026-13-50.png`
- Отчёт md/pdf: `DESIGN REVIEW REPORT/Feedback-Modal_09-05-2026-13-50`
- Кэш дизайн-системы: `DESIGN REVIEW REPORT/design-system-jupiter_09-05-2026-13-30.md`
