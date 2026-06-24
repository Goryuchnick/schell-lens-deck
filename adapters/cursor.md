# Адаптер — Cursor (2.4+)

Cursor 2.4+ имеет субагенты как **Markdown + YAML-фронтматтер** и для совместимости **читает `.claude/agents/`** (`.cursor/` приоритетнее при коллизии имён). Поэтому перенос почти бесплатный.

## Что делать

1. **Субагенты.** Либо оставь `gamedesign/.claude/agents/gd-*.md` (Cursor подхватит из `.claude/agents/`), либо скопируй в `.cursor/agents/`. Тела ролей tool-agnostic — менять не нужно.
2. **Модель.** Расходится только словарь поля `model`. Замени по `lenses/models.md`:
   - `opus` → `claude-opus-4.x` (или конкретный id) — для `gd-keeper`, `gd-concept`, `gd-balance`;
   - `sonnet` → `inherit` или `claude-sonnet-4.x` — для остальных;
   - `haiku` → `fast` — для механических шагов.
3. **Скилл-оркестратор.** `SKILL.md` кладётся как Cursor-skill (Cursor 2.4 поддерживает SKILL.md-манифесты). Логика стадий и risk-gate берётся из `gamedesign/lenses/stage-map.md` как есть.
4. **Фон/последовательность.** Стадии — последовательно (foreground), чтобы не было гонок по `GDD.md`. `is_background: true` уместен только для долгого веб-зонда.

## Веб-зонды

Браузерный автомат Playwright MCP в Claude Code → в Cursor используется его встроенный браузер/превью либо MCP-эквивалент. Если недоступен — `gd-prototyper` отдаёт билд на ручной запуск.

## Что НЕ переносится 1:1

- Поле `model` (словарь различается — см. выше).
- Механизм обнаружения скилла (Cursor skills marketplace vs `.claude/skills/`).
