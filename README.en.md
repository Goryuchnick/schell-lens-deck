[Русский](README.md) | **English**

# design-game — game design through Jesse Schell's lenses

A skill for Claude Code and OpenAI Codex that takes a game from a raw idea to a finished design document through stages 0–7 of Jesse Schell's method (*The Art of Game Design: A Book of Lenses*). It works for a five-minute game and for a large project alike.

> **Language note.** The skill currently speaks Russian: the lens deck, stage guides, templates and agent roles are written in Russian. An English base is planned as a separate step.

The agent acts as a sparring partner, scribe and auditor; the human makes the calls. To keep the model from improvising where it matters, deterministic steps are scripts: they pick the lenses for a stage, check a stage file before its gate, collect the owner's answers, print the gate card and assemble the project Bible.

## What's inside

- **Lens deck** — the 113 lenses of the book retold in our own words, lens 93½ *Presence* from the third edition, and two lenses of our own marked "not Schell": *Honest Claims* for advergames and educational games, and *Child Safety in Social Play*.
- **Stages 0–7**: heart of the experience → concept and tetrad → mechanics → balance → experience and interface → story and world → playtesting → release. Each stage has its own steps, template and agent role.
- **The keeper** re-audits the whole game after every stage: does it still serve the controlling idea, does it pass the eight filters, do stages contradict each other.
- **Audience gate**: before the player agent runs a probe, a human describes who is going to play. Player interviews are built for each audience separately.
- **Probes** — throwaway tests of one risky question: a table, paper, a web probe built right in the session, or a game engine via MCP.

The result is a game folder with stage files, logs of decisions, risks and lenses, and `BIBLE.md` — one document you can hand to an outsider.

## Install

Requires Python 3.9+ and git.

**Claude Code** — as a plugin, two commands:

```bash
claude plugin marketplace add Goryuchnick/schell-lens-deck
claude plugin install design-game@schell-lens-deck
```

Inside a session the same is done with `/plugin marketplace add Goryuchnick/schell-lens-deck` and `/plugin install design-game@schell-lens-deck`. If you have no SSH key on GitHub and the clone fails, add the marketplace by its full address: `claude plugin marketplace add https://github.com/Goryuchnick/schell-lens-deck.git`.

**Codex** — clone and run the installer:

```bash
git clone https://github.com/Goryuchnick/schell-lens-deck.git
cd schell-lens-deck
python install.py --codex
```

On Windows use `py install.py --codex`. The installer puts the skill into `~/.agents/skills/design-game/` and converts the agent roles into `~/.codex/agents/*.toml`. Role models are set with `--model` and `--strong-model`; without them a role uses the session model. Update with `--force`; install into one project with `--project <folder>`.

**Claude Code without the plugin** — `python install.py --claude`: the skill goes to `~/.claude/skills/`, roles to `~/.claude/agents/`.

Web probes need Playwright MCP, engine probes need that engine's MCP. Paper and table probes need nothing. In Codex, MCP servers are set up in `~/.codex/config.toml`, and role restrictions rest on the role text: Codex roles have no `tools` field.

### Ask your agent to install it

Paste one message to your agent.

Claude Code:

```text
Install the design-game skill: run in the terminal
claude plugin marketplace add https://github.com/Goryuchnick/schell-lens-deck.git
claude plugin install design-game@schell-lens-deck
then tell me to restart the session.
```

Codex:

```text
Install the design-game skill: clone https://github.com/Goryuchnick/schell-lens-deck into a temporary folder and run python install.py --codex there (on Windows: py install.py --codex). Check that ~/.agents/skills/design-game/SKILL.md and ~/.codex/agents/gd-keeper.toml exist, then tell me to restart Codex.
```

## Getting started

Say "let's design a game" in Russian — «спроектируем игру» — plus one sentence about the idea. In Codex call `$design-game`; in Claude Code the skill triggers by meaning.

1. The skill asks the brief in one message, each question with a recommendation: scale, game tags, whether there is a client, working mode, where to keep the game folder.
2. Then stage by stage. After each one you get a gate card: what was decided, the keeper's verdict, the top risk, questions for you with recommendations.
3. Answer in chat by question ID ("Q-02.3: yes") or with a comment right in the stage file:

   ```markdown
   > [!owner] 2026-11-20
   > Make the starting room darker and its exit easier to spot. Q-04.2: yes.
   ```

The default mode is `co-design`: you make the decisions. In `assisted` the agent drives a stage up to its gate, in `auto` all the way, but anything that goes out on your behalf it only prepares — you send it.

You can stop and come back: "let's continue the game" in the same folder makes the skill read the state from the Bible and resume from the first open stage.

## Where the lenses come from

The method and the lenses are Jesse Schell's. The deck was checked against the Russian edition (Alpina Publisher, 2019), a translation of the second edition where lenses are called "prisms". Each lens carries its number and its Russian-edition title so you can find it in the book. English titles were checked against the table of lenses of the third edition (CRC Press, 2019); numbering 1–113 is the same there, only 93½ is new.

All lens texts are retold in our own words, not quoted: the questions carry the author's ideas, not his wording or examples. The deck does not replace the book. If the skill helps you, buy the book — it has the explanations, stories and examples this deck leaves out.

## License

[MIT](LICENSE).
