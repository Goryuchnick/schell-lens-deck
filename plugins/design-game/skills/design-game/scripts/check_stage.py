"""Проверка файла стадии перед гейтом.

    python -X utf8 scripts/check_stage.py <папка игры> --stage N [--before-keeper]
    python -X utf8 scripts/check_stage.py <папка игры> --stage 0 --audience

Что проверяет:
- шапку: статус из списка; управляющая идея совпадает со стержнем; строка «Линзы стадии» совпадает
  с текущим выводом pick_lenses.py (сменился паспорт или идея — шапку надо обновить);
- обязательные разделы из шаблона стадии; разделы с пометкой «по тегу» или «по полю» — только если они есть
  в паспорте игры («+» — и, «|» — или, запятая — любой из вариантов);
- таблицу вопросов владельцу: номера Q-NN.k этой стадии и рекомендация у каждого;
- журнал линз: строка на каждую линзу набора стадии и статус знания из четырёх;
- необработанные комментарии [!owner];
- незаполненные {{заглушки}} — у роли перед сдачей (--before-keeper) и у стадий в GATE, OK, ЖДЁТ ВЛАДЕЛЬЦА;
- сверку хранителя в едином формате — для GATE, OK и ЖДЁТ ВЛАДЕЛЬЦА без --before-keeper;
- на стадии 0 ещё стержень (нет заглушек вне выключенных паспортом разделов) и анкету аудитории.

--before-keeper — проверка роли стадии перед её ответом «готово»: сверку хранителя не требует.
--audience — только анкета аудитории: у каждой «### Группа» поля 1–12 без заглушек, у «не знаю» — вопрос Q-00.k.
Перед запуском агента-игрока она должна дать код 0.
Код 0 — готово, 1 — есть проблемы (список в выводе), 2 — ошибка паспорта.
"""
import argparse
import re
import sys
from pathlib import Path

from pick_lenses import SKILL, select

STATUSES = ('TODO', 'DRAFT', 'GATE', 'OK', 'BLOCK', 'SKIP', 'ЖДЁТ ВЛАДЕЛЬЦА')
KEEPER = ('GATE', 'OK', 'ЖДЁТ ВЛАДЕЛЬЦА')
KNOWLEDGE = ('факт', 'вкус владельца', 'гипотеза', 'проверено')
MARK = re.compile(r'\s*<!--\s*(по тегу|по полю|необязательно)\s*:?\s*([^>]*?)\s*-->')
AUDIENCE_FIELDS = 12


def outside_code(md):
    out, code = [], False
    for line in md.splitlines():
        if line.strip().startswith('```'):
            code = not code
        elif not code:
            out.append(line)
    return out


def headings(md):
    return [line[3:] for line in outside_code(md) if line.startswith('## ')]


def sections(md):
    """Разделы «## …» без блоков кода: (заголовок, строки тела)."""
    out = []
    for line in outside_code(md):
        if line.startswith('## '):
            out.append((line[3:], []))
        elif out:
            out[-1][1].append(line)
    return out


def wanted(values, have):
    """Условие пометки: варианты через запятую — любой; внутри варианта «+» — и, «|» — или.
    «kids + multiplayer | community» — дети и при этом сеть или сообщество."""
    return any(all(set(p.strip() for p in part.split('|')) & set(have) for part in alt.split('+'))
               for alt in values)


def enabled(heading, s):
    """Нужен ли раздел при этом паспорте."""
    m = MARK.search(heading)
    if not m:
        return True
    kind, values = m.group(1), [v.strip() for v in m.group(2).split(',') if v.strip()]
    if kind == 'необязательно':
        return False
    return wanted(values, s['tags'] if kind == 'по тегу' else s['fields'])


def idea_of(md):
    m = re.search(r'^## Управляющая идея[^\n]*\n(.*?)(?=^## |\Z)', md, re.M | re.S)
    for line in (m.group(1).splitlines() if m else []):
        b = re.match(r'^\*\*(.+?)\*\*\s*$', line.strip())
        if b and not line.lstrip().startswith('>') and '{{' not in b.group(1):
            return b.group(1).strip()
    return None


def audience_problems(game):
    path = game / '00-heart' / 'AUDIENCE.md'
    if not path.exists():
        return ['нет 00-heart/AUDIENCE.md — гейт аудитории не пройден']
    md = path.read_text(encoding='utf-8')
    groups = re.findall(r'^### Группа[^\n]*\n(.*?)(?=^### Группа|^## |\Z)', md, re.M | re.S)
    if not groups:
        return ['в анкете аудитории нет ни одной «### Группа»']
    problems, unknown = [], False
    for n, body in enumerate(groups, 1):
        for k in range(1, AUDIENCE_FIELDS + 1):
            row = re.search(rf'^\|\s*{k}\s*\|(.*)$', body, re.M)
            if not row:
                problems.append(f'анкета, группа {n}: нет поля {k}')
            elif '{{' in row.group(1):
                problems.append(f'анкета, группа {n}: поле {k} не заполнено')
            elif 'не знаю' in row.group(1).lower():
                unknown = True
    heart = game / '00-heart' / 'HEART.md'
    if unknown and not (heart.exists() and re.search(r'^\| Q-00\.\d+', heart.read_text(encoding='utf-8'), re.M)):
        problems.append('в анкете есть «не знаю», а в 00-heart/HEART.md нет вопроса Q-00.k об этом')
    return problems


def check(game, stage, before_keeper=False):
    """Список проблем файла стадии и сведения о нём: статус, файл, набор линз."""
    game = Path(game)
    s = select(game, stage)
    nn = f'{int(stage):02d}'
    rel = s['stage']['file']
    info = {'select': s, 'nn': nn, 'file': rel, 'status': None}
    if not (game / rel).exists():
        return [f'нет файла стадии {rel}'], info
    md = (game / rel).read_text(encoding='utf-8')
    ci = (game / '00-heart' / 'CONTROLLING-IDEA.md').read_text(encoding='utf-8')
    problems = []

    m = re.search(r'Статус:\s*(' + '|'.join(STATUSES) + ')', md)
    info['status'] = status = m.group(1) if m else None
    if not status:
        problems.append('в шапке нет статуса: ' + ', '.join(STATUSES))
    head_idea = re.search(r'^> Управляющая идея:\s*\*\*(.+?)\*\*', md, re.M)
    idea = idea_of(ci)
    if not head_idea or '{{' in head_idea.group(1):
        problems.append('в шапке нет управляющей идеи')
    elif idea and head_idea.group(1).strip() != idea:
        problems.append('управляющая идея в шапке не совпадает со стержнем — обновить шапку')
    lens_line = re.search(r'^> Линзы стадии:\s*(.+)$', md, re.M)
    expected = ' · '.join(f'{i} {s["lenses"][i]["name"]}' for i in dict.fromkeys(i for _, ids in s['groups'] for i in ids))
    if not lens_line or '{{' in lens_line.group(1):
        problems.append('в шапке нет строки «Линзы стадии» — вписать первую строку вывода pick_lenses.py')
    elif lens_line.group(1).strip() != expected:
        problems.append('строка «Линзы стадии» устарела — вписать заново первую строку вывода pick_lenses.py')
    if status == 'SKIP':
        summary = re.search(r'^## Резюме\s*\n(.+?)(?=^## |\Z)', md, re.M | re.S)
        if not summary or not summary.group(1).strip() or '{{' in summary.group(1):
            problems.append('стадия пропущена, но в «Резюме» нет причины пропуска')
        return problems, info

    have = {MARK.sub('', h).strip() for h in headings(md)}
    template = SKILL / 'templates' / 'stages' / f'{nn}-{Path(rel).stem}.md'
    for h in headings(template.read_text(encoding='utf-8')):
        if enabled(h, s) and MARK.sub('', h).strip() not in have:
            problems.append(f'нет раздела «## {MARK.sub("", h).strip()}»')

    for line in md.splitlines():
        if line.startswith('| Q-'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if not cells[0].startswith(f'Q-{nn}.'):
                problems.append(f'вопрос {cells[0]}: номер не этой стадии, нужен Q-{nn}.k')
            if len(cells) < 5 or not cells[2] or '{{' in cells[2]:
                problems.append(f'вопрос {cells[0]}: нет рекомендации')
    if n := len(re.findall(r'^> \[!owner\]', md, re.M)):
        problems.append(f'необработанных [!owner]: {n} — ответить «> [!agent]» и сменить тег на [!owner-ok]')
    if (before_keeper or status in KEEPER) and any('{{' in line for line in outside_code(md)):
        problems.append('остались незаполненные {{заглушки}}')

    if stage == '0':
        for h, body in sections(ci):
            if enabled(h, s) and any('{{' in line for line in body):
                problems.append(f'стержень: раздел «{MARK.sub("", h).strip()}» не заполнен')
        problems += audience_problems(game)

    log = game / 'logs' / 'LENS-LOG.md'
    logmd = log.read_text(encoding='utf-8') if log.exists() else ''
    for i in dict.fromkeys(i for _, ids in s['groups'] for i in ids):
        if not re.search(rf'^\|\s*{re.escape(i)}\s[^|]*\|[^|]*\|[^|]*\|\s*{nn}\s*\|', logmd, re.M):
            problems.append(f'в logs/LENS-LOG.md нет строки линзы {i} «{s["lenses"][i]["name"]}» на стадии {nn}')
    for line in logmd.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if line.startswith('|') and len(cells) >= 7 and cells[3] == nn and '{{' not in line and cells[6] not in KNOWLEDGE:
            problems.append(f'журнал линз, {cells[0]}: знание «{cells[6]}» — нужно одно из {KNOWLEDGE}')

    if status in KEEPER and not before_keeper:
        cons = game / 'logs' / 'CONSISTENCY.md'
        blocks = re.findall(rf'^## Сверка после стадии {nn}\b.*?(?=^## Сверка после стадии |\Z)',
                            cons.read_text(encoding='utf-8') if cons.exists() else '', re.M | re.S)
        if not blocks:
            problems.append('нет сверки хранителя для этой стадии — сначала gd-keeper')
        elif not re.search(r'^\*\*Вердикт:\*\*\s*(OK|DRIFT|BLOCK|ЖДЁТ ВЛАДЕЛЬЦА)\s*$', blocks[-1], re.M):
            problems.append('вердикт хранителя не в формате «**Вердикт:** OK | DRIFT | BLOCK | ЖДЁТ ВЛАДЕЛЬЦА»')
    return problems, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('game')
    ap.add_argument('--stage', required=True, choices=[str(i) for i in range(8)])
    ap.add_argument('--before-keeper', action='store_true')
    ap.add_argument('--audience', action='store_true')
    a = ap.parse_args()
    if a.audience:
        problems = audience_problems(Path(a.game))
        print('\n'.join(f'- {p}' for p in problems) if problems else 'OK: анкета аудитории заполнена')
        sys.exit(1 if problems else 0)
    problems, info = check(a.game, a.stage, a.before_keeper)
    if problems:
        print(f'Стадия {info["nn"]} ({info["file"]}, статус {info["status"]}) не готова:')
        for p in problems:
            print(f'- {p}')
        sys.exit(1)
    print(f'OK: стадия {info["nn"]} ({info["file"]}, статус {info["status"]}) готова')


if __name__ == '__main__':
    main()
