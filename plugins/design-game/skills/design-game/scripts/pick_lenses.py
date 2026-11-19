"""Подбор линз стадии: точный набор и текст только отобранных линз.

    python -X utf8 scripts/pick_lenses.py <папка игры> --stage N [--gate] [--symptom "реплика"] [--owner МОМЕНТ]

Читает паспорт игры из `00-heart/CONTROLLING-IDEA.md` (раздел «## Паспорт игры», блок строк «ключ: значение»),
правила — из `stages/stages.json`, текст линз — из `lenses/lenses.json` (пути от папки скилла).

  --gate             добавить сквозной набор гейта
  --symptom "…"      добавить до трёх линз, чьи diagnoses совпали с репликой («скучно», «не пойму, что делать»)
  --owner МОМЕНТ     вопросы владельцу на момент: stage0, gate, stall, fatigue, critique, closing

Первая строка вывода — готовая строка «Линзы стадии: …» для шапки файла стадии.
Ошибка паспорта (нет раздела, неизвестный масштаб или тег) — код 2: подбор не угадывается.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SCALES = ['mini', 'small', 'medium', 'large']
OWNER_MOMENTS = ['stage0', 'gate', 'stall', 'fatigue', 'critique', 'closing']


def fail(msg):
    print(f'ОШИБКА: {msg}', file=sys.stderr)
    sys.exit(2)


def passport(game):
    path = game / '00-heart' / 'CONTROLLING-IDEA.md'
    if not path.exists():
        fail(f'нет {path} — сначала стадия 0')
    m = re.search(r'^## Паспорт игры\s*\n+```[a-z]*\n(.*?)\n```', path.read_text(encoding='utf-8'), re.M | re.S)
    if not m:
        fail('в CONTROLLING-IDEA.md нет раздела «## Паспорт игры» с блоком «ключ: значение»')
    data = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            data[k.strip().lower()] = v.strip()
    return data


def words(text):
    return {w[:5] for w in re.findall(r'[а-яёa-z]{4,}', text.lower().replace('ё', 'е'))}


def load():
    rules = json.loads((SKILL / 'stages' / 'stages.json').read_text(encoding='utf-8'))
    lenses = {x['id']: x for x in json.loads((SKILL / 'lenses' / 'lenses.json').read_text(encoding='utf-8'))}
    return rules, lenses


def select(game, st, gate=False, symptom=None, owner=None):
    """Набор линз стадии: группы (заголовок, id), вшитые в шаблон, паспорт. Общий для подбора и проверки стадии."""
    rules, lenses = load()
    p = passport(Path(game))

    scale = p.get('масштаб', '')
    if scale not in SCALES:
        fail(f'масштаб «{scale}» — нужен один из {SCALES}')
    tags = [t.strip() for t in p.get('теги', '').split(',') if t.strip() and t.strip() not in ('нет', '-', '—')]
    if unknown := [t for t in tags if t not in rules['tags']]:
        fail(f'неизвестные теги {unknown} — допустимы {sorted(rules["tags"])}')
    fields = [f for f in rules['fields'] if p.get(f, 'нет').lower() == 'да']

    stage = rules['stages'][st]
    core, template = stage['core'], stage['template']
    taken = set(core) | set(template)
    groups = [('Ядро стадии', core)]

    def applicable(ids):
        return [i for i in ids if i not in taken and int(st) in lenses[i]['stages']]

    extra = []
    for t in tags:
        extra += rules['tags'][t]
    for c in rules['combos']:
        if all(t in tags for t in c['all']) and any(t in tags for t in c['any']):
            extra += c['lenses']
    for f in fields:
        extra += rules['fields'][f]
    if SCALES.index(scale) >= SCALES.index(rules['scale']['from']):
        extra += rules['scale']['lenses']
    # не больше passport_cap линз по паспорту: порядок в списках тегов — приоритет, остальное доступно по симптому
    chosen = applicable(list(dict.fromkeys(extra)))[:rules['passport_cap']]
    taken.update(chosen)
    groups.append(('По паспорту: теги, поля, масштаб', chosen))

    if gate:
        groups.append(('Сквозные на гейте', [i for i in rules['gate'] if i not in taken]))
        taken.update(rules['gate'])
    if symptom:
        sw = words(symptom)
        scored = []
        for i, x in lenses.items():
            hits = sum(1 for d in x['diagnoses'] if (dw := words(d)) and len(dw & sw) * 2 >= len(dw))
            if hits and i not in taken:
                scored.append((-hits, i))
        groups.append((f'По симптому «{symptom}»', [i for _, i in sorted(scored)[:3]]))
    if owner:
        groups.append((f'Вопросы владельцу ({owner}): задать и записать ответ дословно',
                       rules['owner']['when'][owner]['lenses']))
    return {'rules': rules, 'lenses': lenses, 'stage': stage, 'groups': groups, 'template': template,
            'scale': scale, 'tags': tags, 'fields': fields}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('game')
    ap.add_argument('--stage', required=True, choices=[str(i) for i in range(8)])
    ap.add_argument('--gate', action='store_true')
    ap.add_argument('--symptom')
    ap.add_argument('--owner', choices=OWNER_MOMENTS)
    a = ap.parse_args()
    s = select(a.game, a.stage, a.gate, a.symptom, a.owner)
    lenses, groups, template = s['lenses'], s['groups'], s['template']

    owner = set(s['rules']['owner']['lenses'])
    shown = [i for _, ids in groups for i in ids]
    print('Линзы стадии: ' + ' · '.join(f'{i} {lenses[i]["name"]}' for i in dict.fromkeys(shown)))
    print(f'\nСтадия {a.stage} «{s["stage"]["name"]}» · масштаб {s["scale"]} · теги: {", ".join(s["tags"]) or "нет"}'
          f' · поля: {", ".join(s["fields"]) or "нет"}')
    for title, ids in groups:
        if not ids:
            continue
        print(f'\n## {title}')
        for i in ids:
            x = lenses[i]
            ref = f'рус. изд.: «{x["ru_edition"]}»; ' if x['ru_edition'] else ''
            mark = ' · вопрос владельцу' if i in owner else ''
            print(f'\n### {i} · {x["name"]} — {ref}{x["en"]} · {x["source"]}{mark}\n')
            print(x['purpose'] + '\n')
            for q in x['questions']:
                print(f'- {q}')
    if template:
        print('\n## Вшиты в шаблон стадии — их вопросы стали разделами файла')
        print(' · '.join(f'{i} {lenses[i]["name"]}' for i in template))


if __name__ == '__main__':
    main()
