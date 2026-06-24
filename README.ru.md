[English](README.md) | **Русский**

# design-game

**design-game** — мульти-стадийный пайплайн гейм-дизайна по линзам Джесси Шелла («The Art of Game Design: A Book of Lenses»). Ведёт ИИ-кодинг-агентов (Claude Code / Cursor / Antigravity) **от идеи до релиза** по стадиям 0–7, держит управляющую идею как стержень и сверяет связность после каждой стадии. Масштаб-агностичен: работает и для миниигры на 5 минут, и для AAA-концепта.

---

## Что это

- **Оркестратор** (`skill/design-game/SKILL.md`) — точка входа; ведёт бриф, диспатчит стадийных агентов, держит петли ревью.
- **Субагенты** (`.claude/agents/gd-*.md`) — каждый отвечает за одну стадию; читают `CONTROLLING-IDEA.md` как стержень; возвращают `OK | BLOCK`.
- **Библиотека линз** (`lenses/`) — ~100 линз с фокус-вопросами, стадийным маппингом и дисциплиной прото-зондов.
- **Шаблоны** (`templates/`) — артефакты игры (GDD, LENS-LOG, CONTROLLING-IDEA, CONSISTENCY, PITCH, PROTOTYPE-PROBE, JSON-логи).
- **Адаптеры** (`adapters/`) — инструкции по установке под Claude Code, Cursor, Antigravity.

---

## Ключевые принципы

- **Управляющая идея — стержень.** Формулируется первой (Стадия 0), живёт в шапке каждого артефакта. Любой элемент, не усиливающий её, — кандидат на вырез (линза Unification).
- **Живой журнал линз (LENS-LOG).** Ответы на фокус-вопросы накапливаются по ходу, могут долго висеть `open`. Это честнее, чем отвечать на всё сразу.
- **Rule of the Loop — gd-keeper после каждой стадии.** После закрытия любой стадии `gd-keeper` переаудитирует все предыдущие на дрейф от управляющей идеи и внутренние противоречия → `CONSISTENCY.md`. Серьёзный дрейф → `BLOCK` → петля к пользователю.
- **Engine-agnostic прото-зонды, одноразовые по дисциплине Шелла.** У каждого зонда ровно один рискованный вопрос; готов выбросить. Лестница форм: таблица-симуляция → бумага/ASCII → веб (TS + Phaser/Canvas). Веб берётся потому, что его Claude Code может собрать и запустить через Playwright прямо в чате — петля замыкается.
- **Руль автономии** — три режима, выбираются на старте, переключаются в любой точке: `co-design` (агент предлагает, человек решает каждую развилку) / `assisted` (агент драфтит, человек аппрувит на гейтах) / `auto` (агент гонит, каждое самостоятельное решение в `decision-log`). Агент = спарринг-партнёр + писарь; **ставки делает дизайнер**.
- **Подбор линз по двум осям — не по чистому scale.** Набор стадии = ядро стадии + `foundational`-кандидаты (Essential Experience, The Toy, Flow, Curiosity) + **pull по категориям и рискам игры** (теги: advergame, multiplayer, narrative, economy, kids, …). Scale влияет на глубину, но не обрезает релевантную линзу.
- **Advergame-слой правдивости.** Для рекламных и обучающих игр: число-наружу = источник или пометка «иллюстративное». `gd-balance` не выдумывает обещания молча, `gd-keeper` ловит их как `DRIFT (Responsibility / Honest Claim)`.
- **Лог-архитектура: рассуждение = .md, данные = JSON.** `GDD.md` / `LENS-LOG.md` / `CONSISTENCY.md` — аргумент для дизайнера. `probe.json` / `lens-log.json` / `errors.json` — замеры и статусы для машинных проверок. Не дубль — разделение по природе.

---

## Стадии 0–7

| # | Стадия | Цель / артефакт | Ключевые линзы | Агент |
|---|---|---|---|---|
| **0** | Сердце опыта | Управляющая идея в 1 предложение + желаемый опыт + для кого + scale → `CONTROLLING-IDEA.md` | Essential Experience, Emotion, The Player, Fun, Curiosity, Surprise | оркестратор (интервью) |
| **1** | Концепт | Тетрада (Механика / История / Эстетика / Технология), портрет игрока, тема → раздел GDD + one-pager | Holographic Design, Unification, Resonance, Elemental Tetrad, Flow, Motivation | **gd-concept** |
| **2** | Ядро и механики | Core loop; пространство/объекты/действия/правила; цели; значимые выборы → раздел GDD (+ зонд) | The Toy, Mechanics, Goals, Meaningful Choices, Triangularity, Skill, Chance | **gd-mechanics** (+ gd-prototyper / gd-builder) |
| **3** | Баланс | 12 типов баланса, экономика, кривые сложности → раздел GDD (+ таблица-симуляция) | Fairness, Challenge, Reward, Simplicity/Complexity, Elegance, Economy, Honest Claim | **gd-balance** (+ gd-prototyper / gd-builder) |
| **4** | Опыт и интерфейс | Кривая интереса, эстетика, интерфейс, фидбэк, «сочность», непрямое управление → раздел GDD | Interest Curve, Beauty, The Interface, Feedback, Juiciness, Indirect Control | **gd-experience** |
| **5** | Нарратив и мир *(skippable для mini)* | История, мир, аватар, персонажи, story-machine → раздел GDD | The Story, The World, The Avatar, Character, Story Machine, The Obstacle | **gd-narrative** |
| **6** | Плейтест и итерации | План тестов, петля итераций, карта рисков → секция PLAYTEST (+ играбельный билд) | The Playtest, The Loop, The Team | **gd-playtest** (+ gd-prototyper / gd-builder) |
| **7** | Релиз и бизнес | Питч, комьюнити, монетизация, ответственность, тех/деплой-план → `PITCH.md` + раздел GDD | The Pitch, The Profit, Transformation, Responsibility, Community | **gd-release** |

После каждой стадии — **gd-keeper** (обратная сверка всех предыдущих стадий). Стадия 5 skippable для масштаба `mini`/`small` без нарратива. Стадия 7 обязательна для `advergame/serious`.

---

## Установка

Полные инструкции с нюансами каждого тула — в `adapters/`:

| Тул | Адаптер |
|---|---|
| Claude Code | [`adapters/claude-code.md`](adapters/claude-code.md) |
| Cursor 2.4+ | [`adapters/cursor.md`](adapters/cursor.md) |
| Antigravity 2.0 | [`adapters/antigravity.md`](adapters/antigravity.md) |

### Быстрая установка под Claude Code

> **Важно:** Имя локальной папки должно быть `gamedesign` — на него ссылаются внутренние пути скилла (`gamedesign/lenses/...`, `gamedesign/.claude/agents/...` от корня воркспейса). Имя репо на GitHub (`schell-lens-deck`) и имя локальной папки (`gamedesign`) различаются намеренно — клонируй с явным именем папки, как в команде ниже.

```bash
# 1. Клонируй В ПАПКУ gamedesign (имя важно — на него ссылается скилл):
git clone https://github.com/Goryuchnick/schell-lens-deck.git gamedesign

# 2. Поставь скилл-оркестратор в .claude/skills/ (глобально или в проект):
cp -r gamedesign/skill/design-game ~/.claude/skills/design-game
#    (или в .claude/skills/ твоего проекта)

# 3. Субагенты уже в gamedesign/.claude/agents/ — оркестратор находит их сам.
#    Опционально скопировать в ~/.claude/agents/ для глобального доступа из любого проекта.

# 4. Проверь/скорректируй модели в gamedesign/lenses/models.md:
#    - reasoning-heavy → opus:    gd-keeper, gd-concept, gd-balance
#    - balanced-creative → sonnet: остальные агенты
#    - mechanical → haiku:         механические шаги

# 5. Для веб-зондов (стадия с вопросом про ощущение/тайминг) нужен Playwright MCP —
#    добавь в .mcp.json проекта, если не подключён.
#    Безкодовые зонды (таблица/ASCII) Playwright не требуют.
```

> **Примечание:** `skill/design-game/SKILL.md` в репо — копия для самодостаточности клона. Канонический рабочий скилл Claude Code ожидается в `.claude/skills/design-game/SKILL.md` (глобальный или проектный конфиг) — туда его и копируй при установке.

### Cursor 2.4+

Cursor 2.4+ читает `.claude/agents/` (`.cursor/agents/` приоритетнее при коллизии имён), поэтому субагенты переносятся почти без изменений — только замени словарь поля `model` по [`lenses/models.md`](lenses/models.md) (`opus` → `claude-opus-4.x`, `sonnet` → `inherit`, `haiku` → `fast`). Подробнее → [`adapters/cursor.md`](adapters/cursor.md).

### Antigravity 2.0

Транскрипция, не drop-in: инвариант → `GEMINI.md`, роли → `.agents/agents.md`, скилл → `.agents/skills.md`. Модели по тирам из [`lenses/models.md`](lenses/models.md). Подробнее → [`adapters/antigravity.md`](adapters/antigravity.md).

---

## Быстрый старт

1. Вызови `/design-game` (или напиши «спроектируем игру по Шеллу»).
2. Оркестратор задаст вопросы брифа (по одному):
   - идея в одном предложении;
   - масштаб (`mini` / `small` / `medium` / `large`);
   - режим (`docs-only` или `docs + прото-зонды`);
   - тип игры (`entertainment` или `advergame/serious`);
   - режим автономии (`co-design` / `assisted` / `auto`);
   - куда класть артефакты (`<game-path>`).
3. Пройди стадии 0–7 — каждая заканчивается гейтом с резюме и возможностью направить курс.
4. На выходе: собранный `GDD.md` + `PITCH.md` + `LENS-LOG.md` + (опц.) `prototypes/`.

---

## Структура репозитория

```
gamedesign/
  README.md                      ← английская версия (основная)
  README.ru.md                   ← этот файл
  LICENSE                        ← MIT
  .gitignore
  CLAUDE.md                      ← правила проекта для Claude Code

  lenses/
    lenses.md                    ← библиотека ~100 линз (имя RU/EN + фокус-вопросы + теги)
    stage-map.md                 ← стадия → линзы + scale-правила + risk-gate
    schell-prototyping.md        ← дисциплина прото-зонда (лестница форм, правила)
    models.md                    ← тир модели → конкретная модель по тулу
    lens-index.json              ← машинный индекс линз (diagnoses, categories, tier)

  templates/
    CONTROLLING-IDEA.md          ← шаблон стержня
    LENS-LOG.md                  ← шаблон живого журнала линз
    GDD.md                       ← шаблон мастер-диздока
    CONSISTENCY.md               ← шаблон аудитов gd-keeper
    PITCH.md                     ← шаблон питча
    PROTOTYPE-PROBE.md           ← шаблон истории зонда
    probe.json                   ← шаблон JSON-лога зонда
    lens-log.json                ← шаблон тонкого индекса линз
    errors.json                  ← шаблон лога граблей проекта

  adapters/
    claude-code.md               ← установка под Claude Code
    cursor.md                    ← установка под Cursor 2.4+
    antigravity.md               ← установка под Antigravity 2.0

  docs/
    SPEC.md                      ← спецификация скилла (источник истины)
    LESSONS.md                   ← maintainer-лог: дыры системы, исправленные поведения

  .claude/agents/
    gd-keeper.md                 ← хранитель управляющей идеи + кросс-стадийный аудит
    gd-concept.md                ← огранка идеи + тетрада + one-pager
    gd-mechanics.md              ← core loop + механики + выборы
    gd-balance.md                ← баланс + экономика + кривые сложности
    gd-experience.md             ← кривая интереса + интерфейс + «сочность»
    gd-narrative.md              ← история + мир + персонажи
    gd-playtest.md               ← план тестов + петля итераций
    gd-release.md                ← питч + монетизация + ответственность + деплой
    gd-prototyper.md             ← дизайн одноразового зонда (reasoning)
    gd-builder.md                ← код зонда + Playwright + probe.json

  skill/
    design-game/
      SKILL.md                   ← копия оркестратора для самодостаточности клона
```

> Артефакты конкретных игр (`games/<slug>/`) в публикацию не входят — они остаются локально у дизайнера. Runtime-логи (`errors.json`, `probe.json`, `lens-log.json` в папках игр) тоже исключены из git.

---

## Атрибуция

Основано на методологии Jesse Schell, *The Art of Game Design: A Book of Lenses* (3rd ed.). Фокус-вопросы линз в `lenses/lenses.md` — парафраз, не дословный текст карт колоды. Если хочешь работать с оригинальными карточками — рекомендуем купить колоду у автора.

---

## Лицензия

[MIT](LICENSE) — Copyright (c) 2026 Alexander Pronin.
