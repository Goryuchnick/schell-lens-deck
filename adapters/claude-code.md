# Адаптер — Claude Code (нативный)

Это домашняя среда скилла. Здесь всё работает из коробки.

## Раскладка

| Что | Где |
|---|---|
| Оркестратор (скилл) | `.claude/skills/design-game/SKILL.md` (глобальный) |
| Субагенты | `gamedesign/.claude/agents/gd-*.md` |
| Линзы / карты | `gamedesign/lenses/{lenses,stage-map,schell-prototyping,models}.md` |
| Шаблоны | `gamedesign/templates/*.md` |
| Артефакты игры | `<game-path>/` (спрашивается в брифе) |

## Модели

Фронтматтер субагентов уже проставлен под Claude Code (`model: opus | sonnet | haiku`) по тирам из `lenses/models.md`:

- `reasoning-heavy` → `opus`: `gd-keeper`, `gd-concept`, `gd-balance`.
- `balanced-creative` → `sonnet`: `gd-mechanics`, `gd-experience`, `gd-narrative`, `gd-playtest`, `gd-release`, `gd-prototyper`.

## Вызов

`/design-game` (или попроси «спроектируем игру по Шеллу»). Оркестратор спросит бриф и поведёт по стадиям.

## Обнаружение субагентов

Claude Code находит субагенты в `.claude/agents/` проекта, когда работаешь в его контексте. Чтобы `gd-*` были доступны по имени из любого места — один из вариантов:

1. работать из `gamedesign/` (или открыть его как рабочую папку);
2. скопировать `gamedesign/.claude/agents/gd-*.md` в глобальный `.claude/agents/`;
3. **fallback (всегда работает):** оркестратор читает `gamedesign/.claude/agents/gd-X.md` и передаёт тело как роль обычному агенту с моделью по `models.md`. Этот путь зашит в `SKILL.md`.

## Прото-зонды (gd-prototyper)

Для **веб-зондов** (стадия 6, вопрос про ощущение/тайминг) нужен **Playwright MCP** — чтобы собранный билд открыть и снять состояние/скриншот прямо в чате. Включи его под этого агента (в `.mcp.json` уже есть `fetch`; добавь `playwright`, если не подключён). Без браузерного автомата `gd-prototyper` соберёт билд и отдаст его на ручной запуск.

Безкодовые зонды (бумага / таблица-симуляция / ASCII) Playwright не требуют.
