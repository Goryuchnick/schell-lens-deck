# WIKI — куда смотреть в какой ситуации

Пути — от папки скилла. Скрипты: `python -X utf8 <папка скилла>/scripts/<скрипт>.py`.

| Ситуация | Что читать | Что запустить |
|---|---|---|
| Новая игра | `SKILL.md` «Шаг 0», `stages/00-heart.md` | `init_game.py <папка> --name … --scale …` |
| Продолжаем игру | `SKILL.md` «Шаг 0» — таблица состояния печатается в вывод | `init_game.py <папка>` без имени и масштаба, `inbox.py` |
| Какие линзы на стадии | — | `pick_lenses.py <папка> --stage N` |
| Линзы для сверки на гейте | — | `pick_lenses.py <папка> --stage N --gate` |
| «Скучно», «не пойму, что делать» | `SKILL.md` «Застряли» | `pick_lenses.py <папка> --stage N --symptom "…"` |
| Вопросы-линзы владельцу | `method/owner.md` | `pick_lenses.py <папка> --stage N --owner stage0\|gate\|stall\|fatigue\|critique\|closing` |
| Владелец ответил в чате или в файле | `method/owner.md` | `inbox.py <папка>` |
| Режим автономии, что можно без владельца | `method/owner.md` | — |
| Стадия готова к гейту? | шаги стадии `stages/NN-*.md` | `check_stage.py <папка> --stage N` |
| Карточка гейта и решение по ней | `method/cycle.md` | `gate.py <папка> --stage N --mode …`, затем `--accept` или `--return M` |
| Вердикт DRIFT, BLOCK, «ждёт владельца» | `method/cycle.md` | — |
| Вернуться на прошлую стадию | `method/cycle.md` «Возврат на стадию» | `check_stage.py`, `gate.py` |
| Нужен зонд, какую форму выбрать | `method/probe-capabilities.md`, шаги стадии | роли `gd-prototyper` → `gd-builder` |
| Риски игры | `logs/RISKS.md` игры, шаблон `templates/RISKS.md` | — |
| Кто будет играть, гейт аудитории | `templates/AUDIENCE.md`, `stages/00-heart.md` | — |
| Агент-игрок на зонде | вход — четыре вещи из `stages/06-playtest.md`; роль `gd-player` зовут по имени | `check_stage.py <папка> --stage 0 --audience` — код 0 |
| Плейтест, интервью, согласие на запись | `stages/06-playtest.md`, `templates/INTERVIEW-BASE.md`, `templates/PLAYTEST-CONSENT.md` | — |
| Заказчик, рекламная или обучающая игра | `method/layers.md`, разделы стержня с пометками | — |
| Дети и общение в игре | `method/layers.md`, линза N2 | — |
| Деньги и окупаемость | `stages/07-release.md`, шаблон стадии 7 | `money.py` |
| Питч | `templates/PITCH.md` | — |
| Хендофф в сборку | `templates/BUILD-HANDOFF.md` | — |
| Игра уже собрана, дизайн поверх | `method/cycle.md` «Игра уже собрана» | — |
| Что ставить человеку: факт или гипотеза | `method/knowledge.md` | — |
| Где лежит какой файл игры | `method/game-folder.md` | — |
| Масштаб `mini` | шаблоны стадий — пометки про `mini`, `stages/stages.json` | — |
