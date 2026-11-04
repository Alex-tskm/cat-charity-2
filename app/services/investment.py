# app/services/investment.py
"""Универсальная функция распределения инвестиций."""
from datetime import datetime


def invest(
    target,      # новый объект: проект ИЛИ пожертвование
    sources,     # противоположные объекты с неиспользованными остатками
) -> None:
    """Распределяет средства между target и списком sources.

    Если target — новый проект, то sources — свободные пожертвования.
    Если target — новое пожертвование, то sources — открытые проекты.
    Изменения сохраняются в сессии, но commit() здесь НЕ вызывается:
    его делает вызывающий код — так вся операция проходит одной транзакцией.
    """
    for source in sources:
        # Свободный остаток у донора/проекта-источника.
        free_source = source.full_amount - (source.invested_amount or 0)
        # Сколько ещё нужно target.
        free_target = target.full_amount - (target.invested_amount or 0)

        if free_source <= 0 or free_target <= 0:
            continue

        # Переводим, сколько возможно.
        to_invest = min(free_source, free_target)
        source.invested_amount = (source.invested_amount or 0) + to_invest
        target.invested_amount = (target.invested_amount or 0) + to_invest

        # Источник полностью распределён — закрываем его.
        if source.invested_amount == source.full_amount:
            source.fully_invested = True
            source.close_date = datetime.now()

        # Target собрал/распределил всё — закрываем его и прекращаем цикл.
        if target.invested_amount == target.full_amount:
            target.fully_invested = True
            target.close_date = datetime.now()
            break
