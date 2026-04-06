---
name: design-review
description: Runs guided UI design review in Cursor with four comparison modes, saves reports under DESIGN REVIEW REPORT/, and supports /design-review-clean to remove generated artifacts. Use when user asks for design QA, visual mismatch checks, layout-to-design comparison, or clearing review output folders
---

# Design Review Skill

Canonical behavior (Russian, all environments): see [DESIGN_REVIEW_AGENT.md](../../../DESIGN_REVIEW_AGENT.md) at repo root

## Slash command

Use `/design-review` to start a guided review flow

## Workflow

1. Show mode picker:
   - `1` Screenshot from browser vs design image
   - `2` Screenshot from browser vs Figma link
   - `3` Web page URL vs design image
   - `4` Web page URL vs Figma link
2. Ask only for missing required inputs for selected mode
3. Run comparison and return a compact report
4. Save artifacts into flat folder `DESIGN REVIEW REPORT/`:
   - `review-YYYYMMDD-HHMM.md`
   - `annotated-YYYYMMDD-HHMM.png`
5. Always include saved relative file paths in the final response

## Report format

Return exactly these blocks:

1. `Summary`
   - page or screen name
   - match score (0-100)
   - counts: critical/major/minor
2. `Key mismatches` (max 8, sorted by severity)
   - component
   - expected
   - actual
   - severity
   - recommendation
3. `Visual annotations`
   - annotated image or coordinate list (A1, A2, ...)
   - mismatch type per label: layout/spacing/typography/color/text
4. `Final verdict`
   - ready or needs fixes
   - top 3 fixes first

## Tolerances

- spacing: +/-2px
- font size: +/-1px
- component size: +/-3px
- minor color variance allowed
- ignore insignificant 1px rendering noise

## Clean output

When user runs `/design-review-clean` or asks to clear `DESIGN REVIEW REPORT`:

1. Delete all files in `DESIGN REVIEW REPORT/` except root `.gitkeep`
2. Do not delete other repo folders
3. Summarize what was removed. Full rules: [DESIGN_REVIEW_AGENT.md](../../../DESIGN_REVIEW_AGENT.md)
