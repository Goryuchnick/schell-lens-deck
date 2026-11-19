"""Установка скилла design-game без маркетплейса плагинов.

    python install.py --codex                  скилл в ~/.agents/skills/, роли в ~/.codex/agents/ (TOML)
    python install.py --claude                 скилл в ~/.claude/skills/, роли в ~/.claude/agents/
    python install.py --codex --project <папка>  то же, но внутрь проекта: .agents/ и .codex/ или .claude/

В Claude Code проще плагином — две команды, и скилл с ролями обновляется сам:
    claude plugin marketplace add Goryuchnick/schell-lens-deck
    claude plugin install design-game@schell-lens-deck

Установленную версию скрипт заменяет только с --force. В Codex модели ролей не задаются, пока не переданы
--model (обычные роли) и --strong-model (gd-keeper, gd-concept, gd-balance): без них роль берёт модель сессии.
Нужен Python 3.9 или новее.
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE / 'plugins' / 'design-game'
SKILL = PLUGIN / 'skills' / 'design-game'
AGENTS = sorted((PLUGIN / 'agents').glob('gd-*.md'))


def split_role(path):
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', path.read_text(encoding='utf-8'), re.S)
    if not m:
        sys.exit(f'{path.name}: нет frontmatter')
    meta = dict(line.split(':', 1) for line in m.group(1).splitlines() if ':' in line)
    return {k.strip(): v.strip() for k, v in meta.items()}, m.group(2).strip()


def toml_role(meta, body, model):
    if "'''" in body:
        sys.exit(f'{meta["name"]}: в тексте роли есть три апострофа подряд — TOML их не примет')
    quote = lambda s: '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'
    lines = [f'name = {quote(meta["name"])}', f'description = {quote(meta["description"])}']
    if model:
        lines.append(f'model = {quote(model)}')
    return '\n'.join(lines + [f"developer_instructions = '''\n{body}\n'''", ''])


def clear(target, force):
    if target.exists():
        if not force:
            sys.exit(f'{target} уже есть — для обновления запусти с --force')
        shutil.rmtree(target) if target.is_dir() else target.unlink()


def main():
    ap = argparse.ArgumentParser(description='Установка скилла design-game')
    tool = ap.add_mutually_exclusive_group(required=True)
    tool.add_argument('--codex', action='store_true')
    tool.add_argument('--claude', action='store_true')
    ap.add_argument('--project', help='папка проекта вместо домашней папки пользователя')
    ap.add_argument('--force', action='store_true', help='заменить уже установленную версию')
    ap.add_argument('--model', help='Codex: модель обычных ролей')
    ap.add_argument('--strong-model', help='Codex: модель для gd-keeper, gd-concept, gd-balance')
    a = ap.parse_args()
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')

    base = Path(a.project).resolve() if a.project else Path.home()
    skills_dir = base / ('.agents' if a.codex else '.claude') / 'skills'
    agents_dir = base / ('.codex' if a.codex else '.claude') / 'agents'
    skill_target = skills_dir / 'design-game'
    roles = [(role, *split_role(role)) for role in AGENTS]
    targets = [skill_target] + [agents_dir / (f'{m["name"]}.toml' if a.codex else r.name) for r, m, _ in roles]
    if not a.force and (busy := [t for t in targets if t.exists()]):
        sys.exit(f'уже установлено ({len(busy)} из {len(targets)}), например {busy[0]} — для обновления запусти с --force')
    clear(skill_target, a.force)
    skill_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SKILL, skill_target, ignore=shutil.ignore_patterns('__pycache__'))

    agents_dir.mkdir(parents=True, exist_ok=True)
    for role, meta, body in roles:
        if a.codex:
            target = agents_dir / f'{meta["name"]}.toml'
            clear(target, a.force)
            model = a.strong_model if meta.get('model') == 'opus' else a.model
            target.write_text(toml_role(meta, body, model), encoding='utf-8')
        else:
            target = agents_dir / role.name
            clear(target, a.force)
            shutil.copy2(role, target)

    print(f'Скилл: {skill_target}')
    print(f'Роли ({len(AGENTS)}): {agents_dir}')
    print('Codex: перезапусти и позови «$design-game».' if a.codex else
          'Claude Code: перезапусти сессию и скажи «спроектируем игру».')


if __name__ == '__main__':
    main()
