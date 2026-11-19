"""Собирает BIBLE.md игры из файлов стадий и логов и печатает таблицу состояния.

    python -X utf8 scripts/build_bible.py <папка игры>

Библию руками не правят: источники истины — файлы стадий и логи, после правок Библия пересобирается.
Список стадий — из `stages/stages.json` скилла, вердикт хранителя — по единому формату из `logs/CONSISTENCY.md`:
«## Сверка после стадии NN — …» и следом строка «**Вердикт:** OK | DRIFT | BLOCK | ЖДЁТ ВЛАДЕЛЬЦА».
Открытые линзы — строки `logs/LENS-LOG.md` со статусом open. Таблица состояния печатается и в вывод:
по ней оркестратор продолжает игру, не читая Библию целиком.
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
STATUS = r'(TODO|DRAFT|GATE|OK|BLOCK|SKIP|ЖДЁТ ВЛАДЕЛЬЦА)'
VERDICT = re.compile(r'^## Сверка после стадии (\d+)[^\n]*\n+\*\*Вердикт:\*\*\s*(OK|DRIFT|BLOCK|ЖДЁТ ВЛАДЕЛЬЦА)', re.M)
APPENDIX = [('Анкета аудитории', '00-heart/AUDIENCE.md'), ('Реестр рисков', 'logs/RISKS.md'),
            ('Питч', '07-release/PITCH.md'), ('Хендофф в сборку', '07-release/BUILD-HANDOFF.md'),
            ('Журнал линз', 'logs/LENS-LOG.md'), ('Сверки хранителя', 'logs/CONSISTENCY.md'),
            ('Журнал решений', 'logs/DECISIONS.md')]


def read(p):
    return p.read_text(encoding='utf-8') if p.exists() else ''


def first(pattern, text, default='—'):
    m = re.search(pattern, text, re.M)
    return m.group(1).strip() if m else default


def idea_of(ci):
    """Первая жирная строка раздела «Управляющая идея», подсказки «> …» пропускаются."""
    m = re.search(r'^## Управляющая идея[^\n]*\n(.*?)(?=^## |\Z)', ci, re.M | re.S)
    for line in (m.group(1).splitlines() if m else []):
        b = re.match(r'^\*\*(.+?)\*\*\s*$', line.strip())
        if b and not line.lstrip().startswith('>') and '{{' not in b.group(1):
            return b.group(1).strip()
    return '—'


def demote(md, levels=2):
    """Понижает заголовки, не трогая блоки кода: файл стадии встаёт под обёртку «## NN Название»."""
    out, code = [], False
    for line in md.splitlines():
        if line.strip().startswith('```'):
            code = not code
        m = None if code else re.match(r'^(#{1,6}) ', line)
        out.append('#' * min(len(m.group(1)) + levels, 6) + line[len(m.group(1)):] if m else line)
    return '\n'.join(out)


def main():
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_dir():
        sys.exit('нужна папка игры: build_bible.py <папка игры>')
    root = Path(sys.argv[1]).resolve()
    stages = json.loads((SKILL / 'stages' / 'stages.json').read_text(encoding='utf-8'))['stages']

    ci = read(root / '00-heart' / 'CONTROLLING-IDEA.md')
    title = first(r'^# .*? — (.+)$', ci, root.name)
    idea = idea_of(ci)
    passport = {k: first(rf'^{k}:\s*(.+)$', ci) for k in ('масштаб', 'теги', 'режим', 'прото', 'заказчик')}

    rows, toc, bodies, total_q, total_c = [], [], [], 0, 0
    for num, s in stages.items():
        rel, nn = s['file'], f'{int(num):02d}'
        md = read(root / rel)
        q = sum(1 for line in md.splitlines()
                if line.startswith('| Q-') and '{{' not in line and ('⏳' in line or '| open |' in line))
        c = len(re.findall(r'^> \[!owner\]', md, re.M))
        total_q, total_c = total_q + q, total_c + c
        status = first(r'Статус:\s*' + STATUS, md) if md else '—'
        updated = first(r'Обновлено:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})', md) if md else '—'
        rows.append(f"| {nn} | [{s['name']}]({rel}) | {status} | {updated} | {q} | {c} |")
        anchor = f"{nn}-{s['name'].lower().replace(' ', '-')}"
        toc.append(f"- [{nn} {s['name']}](#{anchor})")
        body = demote(md) if md and status not in ('TODO', '—') else '_Стадия не начата._'
        bodies.append(f"\n---\n\n## {nn} {s['name']}\n\n<!-- источник: {rel} -->\n\n{body}\n")

    verdicts = VERDICT.findall(read(root / 'logs' / 'CONSISTENCY.md'))
    last = f'стадия {verdicts[-1][0]}: {verdicts[-1][1]}' if verdicts else 'сверок ещё нет'
    open_lenses = []
    for line in read(root / 'logs' / 'LENS-LOG.md').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if line.startswith('|') and len(cells) >= 6 and cells[5] == 'open' and '{{' not in line:
            open_lenses.append(f'- {cells[0]} (стадия {cells[3]}): {cells[1]}')
    probes = []
    for pp in sorted(root.glob('*/probes/probe-*/PROTOTYPE-PROBE.md')):
        pmd = read(pp)
        question = first(r'^\*\*Вопрос[^:]*:\*\*\s*(.+)$', pmd, 'вопрос не размечен')
        verdict = first(r'^\*\*Вердикт[^:]*:\*\*\s*(.+)$', pmd)
        probes.append(f'- [{pp.parent.name}]({pp.relative_to(root).as_posix()}) — {question} → {verdict}')

    table = ['| Стадия | Файл | Статус | Обновлено | Открытых вопросов | Комментариев владельца |',
             '|---|---|---|---|---|---|', *rows,
             f'\nОткрытых вопросов владельцу: **{total_q}** · необработанных `[!owner]`: **{total_c}** · '
             f'последний вердикт хранителя: **{last}** · открытых линз: **{len(open_lenses)}**']
    out = [f'# Библия проекта — {title}\n',
           f'> Собрано `build_bible.py` {dt.date.today().isoformat()}. Руками не править: источники — файлы стадий и логи.\n',
           '## Стержень\n', f'**{idea}**\n',
           '- ' + ' · '.join(f'{k}: {v}' for k, v in passport.items()) + '\n',
           '## Состояние\n', *table, '',
           'Открытые линзы:\n' + ('\n'.join(open_lenses) or '- нет') + '\n',
           '## Оглавление\n', '- [Управляющая идея полностью](#управляющая-идея-полностью)', *toc,
           '- [Приложения](#приложения)\n',
           '---\n\n## Управляющая идея полностью\n\n<!-- источник: 00-heart/CONTROLLING-IDEA.md -->\n',
           demote(ci) if ci else '_`00-heart/CONTROLLING-IDEA.md` ещё нет._', *bodies,
           '\n---\n\n## Приложения\n', '### Зонды\n' + ('\n'.join(probes) or '- зондов пока нет') + '\n',
           '### Документы\n',
           *[f"- [{n}]({r}){'' if (root / r).exists() else ' _(ещё нет)_'}" for n, r in APPENDIX], '']
    (root / 'BIBLE.md').write_text('\n'.join(out), encoding='utf-8')
    print(f'Библия: {root / "BIBLE.md"}\nСтержень: {idea}\n')
    print('\n'.join(table))


if __name__ == '__main__':
    main()
