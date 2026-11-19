"""Входящие владельца: необработанные комментарии [!owner] во всех файлах игры и открытые вопросы стадий.

    python -X utf8 scripts/inbox.py <папка игры>

Запускается перед каждым агентом и каждым гейтом. Каждый ответ оркестратор переносит дословно в таблицу
вопросов стадии и строкой в logs/DECISIONS.md, а под комментарием пишет «> [!agent]» и меняет тег на [!owner-ok].
"""
import re
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_dir():
        sys.exit('нужна папка игры: inbox.py <папка игры>')
    root = Path(sys.argv[1])
    comments, questions = [], []
    for f in sorted(root.rglob('*.md')):
        if f.name == 'BIBLE.md':
            continue
        lines = f.read_text(encoding='utf-8').splitlines()
        rel = f.relative_to(root).as_posix()
        for n, line in enumerate(lines):
            if line.startswith('> [!owner]'):
                body = []
                for nxt in lines[n + 1:]:
                    if not nxt.startswith('>'):
                        break
                    body.append(nxt.lstrip('> ').strip())
                comments.append(f'- {rel}:{n + 1} {line[10:].strip()} — {" ".join(body)}')
            elif line.startswith('| Q-') and '{{' not in line and ('⏳' in line or '| open |' in line):
                cells = [c.strip() for c in line.strip().strip('|').split('|')]
                rec = f' — рекомендация: {cells[2]}' if len(cells) > 2 and cells[2] else ''
                questions.append(f'- {cells[0]} ({rel}): {cells[1] if len(cells) > 1 else ""}{rec}')
    print(f'Комментарии [!owner] без ответа: {len(comments)}')
    print('\n'.join(comments) or '- нет')
    print(f'\nОткрытые вопросы владельцу: {len(questions)}')
    print('\n'.join(questions) or '- нет')


if __name__ == '__main__':
    main()
