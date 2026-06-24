**English** | [Русский](README.ru.md)

# design-game

**design-game** is a multi-stage game design pipeline built on Jesse Schell's lenses ("The Art of Game Design: A Book of Lenses"). It guides AI coding agents (Claude Code / Cursor / Antigravity) from a raw idea to release through Stages 0–7, keeping the controlling idea as the spine and checking consistency after every stage. Scale-agnostic: works for a 5-minute mini-game and an AAA concept alike.

---

## What it is

- **Orchestrator** (`skill/design-game/SKILL.md`) — entry point; runs the brief interview, dispatches stage agents, holds review loops.
- **Sub-agents** (`.claude/agents/gd-*.md`) — each owns one stage; reads `CONTROLLING-IDEA.md` as the spine; returns `OK | BLOCK`.
- **Lens library** (`lenses/`) — ~100 lenses with focus questions, stage mapping, and proto-probe discipline.
- **Templates** (`templates/`) — game artefacts (GDD, LENS-LOG, CONTROLLING-IDEA, CONSISTENCY, PITCH, PROTOTYPE-PROBE, JSON logs).
- **Adapters** (`adapters/`) — setup instructions for Claude Code, Cursor, and Antigravity.

---

## Key principles

- **Controlling idea is the spine.** Formulated first (Stage 0), lives in the header of every artefact. Any element that does not reinforce it is a cut candidate (Unification lens).
- **Living lens log (LENS-LOG).** Answers to focus questions accumulate throughout; some may stay `open` for a long time. That is more honest than answering everything at once.
- **Rule of the Loop — gd-keeper after every stage.** After closing any stage, `gd-keeper` re-audits all previous stages for drift from the controlling idea and internal contradictions → `CONSISTENCY.md`. Serious drift → `BLOCK` → loop back to the user.
- **Engine-agnostic proto-probes, disposable by Schell's discipline.** Each probe has exactly one risky question; be ready to throw it away. Form ladder: simulation table → paper/ASCII → web (TS + Phaser/Canvas). Web is chosen because Claude Code can build and run it via Playwright right in the chat — closing the loop.
- **Autonomy dial** — three modes, chosen at start, switchable at any point: `co-design` (agent proposes, human decides every fork) / `assisted` (agent drafts, human approves at gates) / `auto` (agent drives, every independent decision logged in `decision-log`). The agent is sparring partner and scribe; **the designer calls the shots**.
- **Lens selection by two axes — not by scale alone.** Each stage's set = stage core + `foundational` candidates (Essential Experience, The Toy, Flow, Curiosity) + **pull by game categories and risks** (tags: advergame, multiplayer, narrative, economy, kids, …). Scale affects depth, but does not cut a relevant lens.
- **Advergame honesty layer.** For promotional and educational games: any number shown publicly must have a source or be marked "illustrative". `gd-balance` does not silently invent claims; `gd-keeper` catches them as `DRIFT (Responsibility / Honest Claim)`.
- **Log architecture: reasoning = .md, data = JSON.** `GDD.md` / `LENS-LOG.md` / `CONSISTENCY.md` are the argument for the designer. `probe.json` / `lens-log.json` / `errors.json` are measurements and statuses for machine checks. Not duplicates — separated by nature.

---

## Stages 0–7

| # | Stage | Goal / artefact | Key lenses | Agent |
|---|---|---|---|---|
| **0** | Heart of the experience | Controlling idea in 1 sentence + desired experience + for whom + scale → `CONTROLLING-IDEA.md` | Essential Experience, Emotion, The Player, Fun, Curiosity, Surprise | orchestrator (interview) |
| **1** | Concept | Elemental Tetrad (Mechanics / Story / Aesthetics / Technology), player portrait, theme → GDD section + one-pager | Holographic Design, Unification, Resonance, Elemental Tetrad, Flow, Motivation | **gd-concept** |
| **2** | Core & mechanics | Core loop; space/objects/actions/rules; goals; meaningful choices → GDD section (+ probe) | The Toy, Mechanics, Goals, Meaningful Choices, Triangularity, Skill, Chance | **gd-mechanics** (+ gd-prototyper / gd-builder) |
| **3** | Balance | 12 balance types, economy, difficulty curves → GDD section (+ simulation table) | Fairness, Challenge, Reward, Simplicity/Complexity, Elegance, Economy, Honest Claim | **gd-balance** (+ gd-prototyper / gd-builder) |
| **4** | Experience & interface | Interest curve, aesthetics, interface, feedback, "juiciness", indirect control → GDD section | Interest Curve, Beauty, The Interface, Feedback, Juiciness, Indirect Control | **gd-experience** |
| **5** | Narrative & world *(skippable for mini)* | Story, world, avatar, characters, story-machine → GDD section | The Story, The World, The Avatar, Character, Story Machine, The Obstacle | **gd-narrative** |
| **6** | Playtesting & iteration | Test plan, iteration loop, risk map → PLAYTEST section (+ playable build) | The Playtest, The Loop, The Team | **gd-playtest** (+ gd-prototyper / gd-builder) |
| **7** | Release & business | Pitch, community, monetisation, responsibility, tech/deploy plan → `PITCH.md` + GDD section | The Pitch, The Profit, Transformation, Responsibility, Community | **gd-release** |

After every stage — **gd-keeper** (back-audit of all previous stages). Stage 5 is skippable for scale `mini`/`small` without narrative. Stage 7 is mandatory for `advergame/serious`.

---

## Installation

Full instructions with tool-specific notes are in `adapters/`:

| Tool | Adapter |
|---|---|
| Claude Code | [`adapters/claude-code.md`](adapters/claude-code.md) |
| Cursor 2.4+ | [`adapters/cursor.md`](adapters/cursor.md) |
| Antigravity 2.0 | [`adapters/antigravity.md`](adapters/antigravity.md) |

### Quick install for Claude Code

> **Important:** The local folder name must be `gamedesign` — the skill's internal paths (`gamedesign/lenses/...`, `gamedesign/.claude/agents/...`) resolve relative to the workspace root and rely on this exact name. The GitHub repo name (`schell-lens-deck`) and the local folder name (`gamedesign`) differ intentionally — clone with an explicit folder name as shown below.

```bash
# 1. Clone INTO a folder named gamedesign (the name matters — the skill references it):
git clone https://github.com/Goryuchnick/schell-lens-deck.git gamedesign

# 2. Install the skill orchestrator into .claude/skills/ (global or project-level):
cp -r gamedesign/skill/design-game ~/.claude/skills/design-game
#    (or into your project's .claude/skills/)

# 3. Sub-agents are already at gamedesign/.claude/agents/ — the orchestrator finds them automatically.
#    Optionally copy to ~/.claude/agents/ for global access from any project.

# 4. Review / adjust models in gamedesign/lenses/models.md:
#    - reasoning-heavy → opus:   gd-keeper, gd-concept, gd-balance
#    - balanced-creative → sonnet: all other agents
#    - mechanical → haiku: mechanical steps

# 5. For web probes (stage with feel/timing questions) you need Playwright MCP —
#    add it to your project's .mcp.json if not already connected.
#    Code-free probes (simulation table / ASCII) do not require Playwright.
```

> **Note:** `skill/design-game/SKILL.md` in the repo is a copy kept for standalone cloning. The canonical working skill for Claude Code is expected at `.claude/skills/design-game/SKILL.md` (global or project config) — copy it there during installation.

### Cursor 2.4+

Cursor 2.4+ reads `.claude/agents/` (`.cursor/agents/` takes priority on name collisions), so the sub-agents transfer almost unchanged — only replace the `model` field values per [`lenses/models.md`](lenses/models.md) (`opus` → `claude-opus-4.x`, `sonnet` → `inherit`, `haiku` → `fast`). Details → [`adapters/cursor.md`](adapters/cursor.md).

### Antigravity 2.0

Transcription, not a drop-in: invariant → `GEMINI.md`, roles → `.agents/agents.md`, skill → `.agents/skills.md`. Models by tier from [`lenses/models.md`](lenses/models.md). Details → [`adapters/antigravity.md`](adapters/antigravity.md).

---

## Quick start

1. Invoke `/design-game` (or say "let's design a game by Schell's lenses").
2. The orchestrator asks brief questions one by one:
   - idea in one sentence;
   - scale (`mini` / `small` / `medium` / `large`);
   - mode (`docs-only` or `docs + proto-probes`);
   - game type (`entertainment` or `advergame/serious`);
   - autonomy mode (`co-design` / `assisted` / `auto`);
   - where to put artefacts (`<game-path>`).
3. Walk through Stages 0–7 — each ends with a gate: a summary and a chance to steer.
4. Output: assembled `GDD.md` + `PITCH.md` + `LENS-LOG.md` + (optionally) `prototypes/`.

---

## Repository structure

```
gamedesign/
  README.md                      ← this file
  README.ru.md                   ← Russian version
  LICENSE                        ← MIT
  .gitignore
  CLAUDE.md                      ← project rules for Claude Code

  lenses/
    lenses.md                    ← library of ~100 lenses (RU/EN name + focus questions + tags)
    stage-map.md                 ← stage → lenses + scale rules + risk-gate
    schell-prototyping.md        ← proto-probe discipline (form ladder, rules)
    models.md                    ← model tier → concrete model per tool
    lens-index.json              ← machine index of lenses (diagnoses, categories, tier)

  templates/
    CONTROLLING-IDEA.md          ← spine template
    LENS-LOG.md                  ← living lens log template
    GDD.md                       ← master game design document template
    CONSISTENCY.md               ← gd-keeper audit template
    PITCH.md                     ← pitch template
    PROTOTYPE-PROBE.md           ← probe story template
    probe.json                   ← probe JSON log template
    lens-log.json                ← thin lens index template
    errors.json                  ← project pitfalls log template

  adapters/
    claude-code.md               ← setup for Claude Code
    cursor.md                    ← setup for Cursor 2.4+
    antigravity.md               ← setup for Antigravity 2.0

  docs/
    SPEC.md                      ← skill specification (source of truth)
    LESSONS.md                   ← maintainer log: system gaps and fixed behaviours

  .claude/agents/
    gd-keeper.md                 ← controlling-idea guardian + cross-stage audit
    gd-concept.md                ← idea refinement + tetrad + one-pager
    gd-mechanics.md              ← core loop + mechanics + choices
    gd-balance.md                ← balance + economy + difficulty curves
    gd-experience.md             ← interest curve + interface + juiciness
    gd-narrative.md              ← story + world + characters
    gd-playtest.md               ← test plan + iteration loop
    gd-release.md                ← pitch + monetisation + responsibility + deploy
    gd-prototyper.md             ← disposable probe design (reasoning)
    gd-builder.md                ← probe code + Playwright + probe.json

  skill/
    design-game/
      SKILL.md                   ← orchestrator copy for standalone cloning
```

> Individual game artefacts (`games/<slug>/`) are not published — they stay local with the designer. Runtime logs (`errors.json`, `probe.json`, `lens-log.json` inside game folders) are excluded from git as well.

---

## Attribution

Based on the methodology of Jesse Schell, *The Art of Game Design: A Book of Lenses* (3rd ed.). The focus questions for lenses in `lenses/lenses.md` are a paraphrase, not verbatim text from the card deck. If you want to work with the original cards, we recommend buying the deck from the author.

---

## License

[MIT](LICENSE) — Copyright (c) 2026 Alexander Pronin.
