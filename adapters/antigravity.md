# Адаптер — Google Antigravity (2.0)

Antigravity использует другую раскладку, чем Claude Code/Cursor: общий контекст в `GEMINI.md`, поведение субагентов в `.agents/agents.md`, переиспользуемые способности в `.agents/skills.md`. Перенос — транскрипция, не drop-in.

## Что делать

1. **Общий контекст → `GEMINI.md`.** Положи туда инвариант: управляющая идея — стержень; линза Unification после каждой стадии; engine-agnostic ядро; прото = одноразовый зонд. Сошлись на `gamedesign/lenses/stage-map.md`.
2. **Субагенты → `.agents/agents.md`.** Перенеси 9 ролей `gd-*` (тела из `gamedesign/.claude/agents/`). Antigravity описывает поведение субагентов в одном файле — оформи каждую роль секцией с её мандатом, линзами и контрактом `OK|BLOCK`.
3. **Скилл → `.agents/skills.md`.** Объяви `design-game` как способность: бриф → стадии 0–7 → gd-keeper между ними. Логика — из `SKILL.md` и `stage-map.md`.
4. **Модель.** По тирам `lenses/models.md`:
   - `reasoning-heavy` → Gemini 3 Pro или Claude Opus 4.6 — `gd-keeper`, `gd-concept`, `gd-balance`;
   - `balanced-creative` → Gemini 3 Pro или Claude Sonnet 4.6 — остальные;
   - `mechanical` → Gemini 3 Flash или GPT-OSS — механические шаги.
   > Claude в Antigravity требует свой Anthropic API-ключ в настройках (биллинг идёт через Google).

## Веб-зонды

Browser-автомат — через инструменты агента Antigravity (его агент-сёрфейс умеет управлять браузером) либо MCP-эквивалент Playwright. Иначе `gd-prototyper` отдаёт билд на ручной запуск.

## Статус

Этот адаптер — **документированный маппинг**, не протестирован в самом Antigravity (другая среда). Раскладка файлов Antigravity 2.0 может меняться — сверяйся с актуальной докой перед переносом.
