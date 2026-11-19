"""Карточка гейта стадии и решение по ней — одинаково в любом режиме автономии.

    python -X utf8 scripts/gate.py <папка игры> --stage N --mode co-design|assisted|auto
    python -X utf8 scripts/gate.py <папка игры> --stage N --mode … --accept
    python -X utf8 scripts/gate.py <папка игры> --stage N --mode … --return M

Без флагов — карточка. Сначала проверка стадии (check_stage.py): не прошла — проблемы и код 1, карточки нет.
Карточка — только у стадии в GATE, OK, ЖДЁТ ВЛАДЕЛЬЦА или SKIP: GATE ставит оркестратор после сверки хранителя.
Общая часть карточки — резюме, вердикт хранителя и фильтры, верхний риск, вопрос правила цикла, вопросы владельцу
с рекомендациями, строка страсти, следующий шаг; дальше — раздел «## Для карточки гейта», который пишет роль.

--accept — владелец принял стадию (в том числе при DRIFT с переносом вопросов): статус OK и строка в журнале решений.
--return M — возврат: стадия M и эта стадия получают DRAFT, строка в журнале решений.
"""
import argparse
import datetime as dt
import re
import sys
from pathlib import Path

from check_stage import check

RANK = {'высокая': 0, 'средняя': 1, 'низкая': 2}
CLOSED = ('закрыт', 'снят', 'принят владельцем')


def section(md, title):
    m = re.search(rf'^##+ {re.escape(title)}[^\n]*\n(.*?)(?=^##+ |\Z)', md, re.M | re.S)
    return m.group(1).strip() if m else ''


def set_status(path, status):
    md = path.read_text(encoding='utf-8')
    md = re.sub(r'(Статус:\s*)(TODO|DRAFT|GATE|OK|BLOCK|SKIP|ЖДЁТ ВЛАДЕЛЬЦА)', rf'\g<1>{status}', md, count=1)
    md = re.sub(r'(Обновлено:\s*)(\S+)', rf'\g<1>{dt.date.today().isoformat()}', md, count=1)
    path.write_text(md, encoding='utf-8')


def log_decision(game, nn, decision, consequence):
    log = game / 'logs' / 'DECISIONS.md'
    row = f'| {dt.date.today().isoformat()} | {nn} | gate | — | «{decision}» | {consequence} | владелец | да |\n'
    text = log.read_text(encoding='utf-8') if log.exists() else ''
    log.write_text(text + ('' if text.endswith('\n') else '\n') + row, encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('game')
    ap.add_argument('--stage', required=True, choices=[str(i) for i in range(8)])
    ap.add_argument('--mode', required=True, choices=['co-design', 'assisted', 'auto'])
    act = ap.add_mutually_exclusive_group()
    act.add_argument('--accept', action='store_true')
    act.add_argument('--return', dest='back', choices=[str(i) for i in range(8)])
    a = ap.parse_args()
    game = Path(a.game)
    if a.back is not None:  # решение о возврате — не карточка, проверка стадии ему не нужна
        from pick_lenses import load
        stages = load()[0]['stages']
        nn, target = f'{int(a.stage):02d}', stages[a.back]['file']
        for rel in {stages[a.stage]['file'], target}:
            set_status(game / rel, 'DRAFT')
        log_decision(game, nn, f'возврат на стадию {int(a.back):02d}', f'{target} → DRAFT')
        print(f'Возврат: стадии {int(a.back):02d} и {nn} в DRAFT, строка в logs/DECISIONS.md.')
        return
    problems, info = check(game, a.stage)
    if problems:
        print(f'Гейт стадии {info["nn"]} не готов:')
        print('\n'.join(f'- {p}' for p in problems))
        sys.exit(1)
    if info['status'] not in ('GATE', 'OK', 'ЖДЁТ ВЛАДЕЛЬЦА', 'SKIP'):
        print(f'Гейт стадии {info["nn"]} не готов: статус {info["status"]} — после сверки хранителя поставь в шапке '
              'GATE или ЖДЁТ ВЛАДЕЛЬЦА; при BLOCK — DRAFT и блок «Возврат» из сверки владельцу')
        sys.exit(1)

    s, nn = info['select'], info['nn']
    stages = s['rules']['stages']
    path = game / info['file']
    if a.accept:
        set_status(path, 'OK')
        log_decision(game, nn, 'стадия принята на гейте', f'{info["file"]} → OK')
        print(f'Стадия {nn} принята: статус OK, строка в logs/DECISIONS.md. Пересобери Библию.')
        return

    md = path.read_text(encoding='utf-8')
    nxt = next(((k, v) for k, v in stages.items() if int(k) > int(a.stage)
                and 'Статус: SKIP' not in ((game / v['file']).read_text(encoding='utf-8')
                                           if (game / v['file']).exists() else '')), None)
    tail = ' В режиме auto иду сразу, вопросы выше решаю как [!auto].' if a.mode == 'auto' else ''
    after = f'Дальше: стадия {int(nxt[0]):02d} «{nxt[1]["name"]}», ведёт {nxt[1]["agent"]}.{tail}' if nxt else \
        'Дальше: закрытие — вопросы владельцу 112 «Ворон» и 111 «Ответственность», хендофф в сборку по желанию.'
    summary = [ln for ln in section(md, 'Резюме').splitlines() if ln.strip() and not ln.lstrip().startswith('>')][:3]
    if info['status'] == 'SKIP':
        print(f'### Стадия {nn} «{s["stage"]["name"]}» пропущена · режим {a.mode}')
        print('Причина: ' + (' '.join(summary) or '—'))
        print(after)
        return

    cons = (game / 'logs' / 'CONSISTENCY.md').read_text(encoding='utf-8')
    block = re.findall(rf'^## Сверка после стадии {nn}\b.*?(?=^## Сверка после стадии |\Z)', cons, re.M | re.S)[-1]
    verdict = re.search(r'^\*\*Вердикт:\*\*\s*(.+)$', block, re.M).group(1).strip()
    filters = re.findall(r'^\| (\d) [^|]*\|\s*([^|]+?)\s*\|', section(block, 'Восемь фильтров'), re.M)
    back = ([ln for ln in section(block, 'Возврат').splitlines() if ln.strip()] or ['—'])[0].lstrip('- ')
    risks = (game / 'logs' / 'RISKS.md').read_text(encoding='utf-8') if (game / 'logs' / 'RISKS.md').exists() else ''
    rows = []
    for ln in risks.splitlines():
        c = [x.strip() for x in ln.strip().strip('|').split('|')]
        if ln.startswith('| R-') and '{{' not in ln and len(c) >= 7 and c[6] not in CLOSED:
            rows.append((RANK.get(c[3], 3), RANK.get(c[4], 3), f'{c[0]} {c[1]} — цена {c[3]}, неопределённость {c[4]}'))
    questions = []
    for line in md.splitlines():
        if line.startswith(f'| Q-{nn}.') and '{{' not in line and ('⏳' in line or '| open |' in line):
            c = [x.strip() for x in line.strip().strip('|').split('|')]
            questions.append(f'- {c[0]} {c[1]} — рекомендация: {c[2]}')
    comments = sum(len(re.findall(r'^> \[!owner\]', f.read_text(encoding='utf-8'), re.M))
                   for f in game.rglob('*.md') if f.name != 'BIBLE.md')
    extra = [ln for ln in section(md, 'Для карточки гейта').splitlines() if ln.strip() and not ln.lstrip().startswith('>')]

    print(f'### Гейт стадии {nn} «{s["stage"]["name"]}» · режим {a.mode}')
    print(f'Файл: {info["file"]}')
    print('Резюме: ' + (' '.join(summary) or '—'))
    print(f'Хранитель: {verdict}. Возврат: {back}')
    print('Фильтры: ' + (' · '.join(f'{n} {st}' for n, st in filters) or 'таблица не заполнена'))
    print('Верхний риск: ' + (sorted(rows)[0][2] if rows else 'открытых рисков нет'))
    print('Правило цикла: какая проблема у игры теперь и какой риск самый крупный — идём дальше или возвращаемся?')
    print('Вопросы (ответ в чате «Q-NN.k: …» или в файле под вопросом «> [!owner]»):')
    print('\n'.join(questions) or '- открытых нет')
    print(f'Комментарии владельца без ответа: {comments or "нет"}')
    print('Страсть (линза 18): горит ли ещё эта игра? — ответ владельца одной строкой')
    if extra:
        print('\n'.join(extra))
    print(after)


if __name__ == '__main__':
    main()
