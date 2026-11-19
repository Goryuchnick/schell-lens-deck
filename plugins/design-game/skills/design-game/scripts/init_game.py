"""Создаёт папку игры из шаблонов скилла и собирает Библию.

    python -X utf8 scripts/init_game.py <папка игры> --name "Название" --scale mini|small|medium|large
    python -X utf8 scripts/init_game.py <папка игры>     повторно: «продолжим игру»

Существующие файлы не перезаписывает, поэтому повторный запуск безопасен: досоздаёт недостающее.
Имя и масштаб нужны только для новой игры. В копию игры не идут строки-подсказки шаблонов («> …»,
кроме шапки стадии и выносок «> [!…]») и отдельные комментарии «<!-- … -->»: подсказки писатель читает
в шаблоне скилла, а в файлах игры они только занимали бы место.
"""
import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
TPL = SKILL / 'templates'
KEEP = ('> Управляющая идея:', '> Стадия:', '> Линзы стадии:', '> [!')

DIRS = ['00-heart/research', '00-heart/probes', '01-concept/probes', '02-mechanics/probes', '03-balance/sims',
        '03-balance/probes', '04-experience/probes', '05-narrative', '06-playtest/probes', '06-playtest/sessions',
        '07-release', 'logs']
COPY = {
    'CONTROLLING-IDEA.md': '00-heart/CONTROLLING-IDEA.md',
    'AUDIENCE.md': '00-heart/AUDIENCE.md',
    'stages/00-HEART.md': '00-heart/HEART.md',
    'stages/01-CONCEPT.md': '01-concept/CONCEPT.md',
    'stages/02-MECHANICS.md': '02-mechanics/MECHANICS.md',
    'stages/03-BALANCE.md': '03-balance/BALANCE.md',
    'stages/04-EXPERIENCE.md': '04-experience/EXPERIENCE.md',
    'stages/05-NARRATIVE.md': '05-narrative/NARRATIVE.md',
    'stages/06-PLAYTEST.md': '06-playtest/PLAYTEST.md',
    'stages/07-RELEASE.md': '07-release/RELEASE.md',
    'RISKS.md': 'logs/RISKS.md',
    'LENS-LOG.md': 'logs/LENS-LOG.md',
    'CONSISTENCY.md': 'logs/CONSISTENCY.md',
    'DECISIONS.md': 'logs/DECISIONS.md',
}


def strip_hints(text):
    out, code, comment = [], False, False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith('```'):
            code = not code
        if code or s.startswith('```'):
            out.append(line)
        elif comment:
            comment = '-->' not in s
        elif s.startswith('<!--'):
            comment = '-->' not in s
        elif s.startswith('>') and not s.startswith(KEEP):
            continue
        elif not (s == '' and out and out[-1].strip() == ''):
            out.append(line)
    return '\n'.join(out).strip() + '\n'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('game')
    ap.add_argument('--name')
    ap.add_argument('--scale', choices=['mini', 'small', 'medium', 'large'])
    a = ap.parse_args()

    root = Path(a.game).resolve()
    new = not (root / '00-heart' / 'CONTROLLING-IDEA.md').exists()
    if new and not (a.name and a.scale):
        sys.exit('новая игра: нужны --name и --scale')
    for d in DIRS:
        (root / d).mkdir(parents=True, exist_ok=True)
    subst = {'{{Название игры}}': a.name or root.name, '{{ГГГГ-ММ-ДД}}': dt.date.today().isoformat(),
             'масштаб: mini | small | medium | large': f'масштаб: {a.scale}' if a.scale else 'масштаб: mini | small | medium | large'}

    created, skipped = [], []
    for src, dst in COPY.items():
        target = root / dst
        if target.exists():
            skipped.append(dst)
            continue
        text = strip_hints((TPL / src).read_text(encoding='utf-8'))
        for k, v in subst.items():
            text = text.replace(k, v)
        target.write_text(text, encoding='utf-8')
        created.append(dst)
    if not (root / 'logs' / 'errors.json').exists():
        (root / 'logs' / 'errors.json').write_text('[]\n', encoding='utf-8')
        created.append('logs/errors.json')

    print('создано:', *(created or ['ничего — всё уже было']), sep='\n  ')
    if skipped:
        print(f'уже были, не тронуты: {len(skipped)}')
    sys.stdout.flush()
    return subprocess.call([sys.executable, '-X', 'utf8', str(SKILL / 'scripts' / 'build_bible.py'), str(root)])


if __name__ == '__main__':
    sys.exit(main())
