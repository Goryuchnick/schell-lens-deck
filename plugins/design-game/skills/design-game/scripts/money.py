"""Окупаемость игры для раздела «Деньги» стадии 7. Считает скрипт, а не модель: в арифметике модель ошибается.

    python -X utf8 scripts/money.py --cost 300000 --unit-income 450
    python -X utf8 scripts/money.py --cost 300000 --arpu-month 90 --months 8 --cac 400

  --cost         сколько стоит сделать и выпустить игру
  --unit-income  приход с одной единицы после комиссий: продажи, лида, целевого действия
  --arpu-month   средний приход с игрока в месяц; --months — сколько месяцев он в среднем играет
  --cac          сколько стоит привлечь одного игрока

Все входы — оценки, пока их не подтвердили данные: в таблицу результат идёт с пометкой «расчёт».
"""
import argparse
import math
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cost', type=float, required=True)
    ap.add_argument('--unit-income', type=float)
    ap.add_argument('--arpu-month', type=float)
    ap.add_argument('--months', type=float)
    ap.add_argument('--cac', type=float)
    a = ap.parse_args()
    given = {k: v for k, v in vars(a).items() if v is not None}
    if bad := [k for k, v in given.items() if v <= 0]:
        sys.exit(f'значения должны быть больше нуля: {", ".join(bad)}')
    ltv_inputs = all(x is not None for x in (a.arpu_month, a.months, a.cac))
    if a.unit_income is None and not ltv_inputs:
        sys.exit('нужен --unit-income или вместе --arpu-month, --months и --cac')
    if a.unit_income is not None:
        print(f'Единиц до окупаемости: {math.ceil(a.cost / a.unit_income)}')
    if ltv_inputs:
        ltv = a.arpu_month * a.months
        print(f'Приход с игрока за всё время: {ltv:g}; стоимость привлечения: {a.cac:g}; отношение: {ltv / a.cac:.2f}')
        if ltv > a.cac:
            print(f'Игроков до окупаемости: {math.ceil(a.cost / (ltv - a.cac))}')
        else:
            print('Не окупается: привлечь игрока дороже, чем он принесёт')


if __name__ == '__main__':
    main()
