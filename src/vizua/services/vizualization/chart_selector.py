def select_top_candidates(ranked_candidates: list[dict], top_n: int) -> list[dict]:
    """
    Выбирает лучшие кандидаты, соблюдая баланс между релевантностью и разнообразием.
    """
    selected_candidates = []
    
    # Динамические лимиты: чем больше графиков просит пользователь, тем больше повторов мы допускаем
    type_limit = max(2, (top_n // 4) + 1)
    col_usage_limit = max(2, (top_n // 5) + 1)
    
    chart_type_counts = {"boxplot": 0, "histogram": 0, "bar": 0, "scatter": 0}
    # Объединяем X и Y в один счетчик использования колонки
    column_usage = {}
    used_pairs = set()

    def get_column_count(col):
        if col is None:
            return 0
        return column_usage.get(col, 0)

    # Первый проход: Строгое соблюдение лимитов
    for candidate in ranked_candidates:
        if len(selected_candidates) >= top_n:
            break

        c_type = candidate["chart_type"]
        x = candidate["x"]
        y = candidate["y"]
        
        # Проверяем лимит на тип графика
        if chart_type_counts[c_type] >= type_limit:
            continue

        # Проверяем уникальность пары (X, Y)
        pair = tuple(sorted((x, y))) if c_type == "scatter" else (x, y)
        if pair in used_pairs:
            continue

        # Проверяем лимит на использование колонок (X и Y суммарно)
        if get_column_count(x) >= col_usage_limit or get_column_count(y) >= col_usage_limit:
            continue

        # Если все проверки прошли — добавляем
        selected_candidates.append(candidate)
        used_pairs.add(pair)
        chart_type_counts[c_type] += 1
        column_usage[x] = column_usage.get(x, 0) + 1
        if y:
            column_usage[y] = column_usage.get(y, 0) + 1

    # Второй проход: Добор оставшихся (ослабляем лимиты, но сохраняем уникальность пар)
    if len(selected_candidates) < top_n:
        for candidate in ranked_candidates:
            if len(selected_candidates) >= top_n:
                break

            c_type = candidate["chart_type"]
            x = candidate["x"]
            y = candidate["y"]
            pair = tuple(sorted((x, y))) if c_type == "scatter" else (x, y)

            if pair in used_pairs:
                continue
            
            # Разрешаем превышать лимит типа, но стараемся не частить с колонками
            if get_column_count(x) >= col_usage_limit + 1 or get_column_count(y) >= col_usage_limit + 1:
                continue

            selected_candidates.append(candidate)
            used_pairs.add(pair)
            column_usage[x] = column_usage.get(x, 0) + 1
            if y:
                column_usage[y] = column_usage.get(y, 0) + 1

    # Финальный проход: Если все еще не набрали top_n (крайний случай)
    if len(selected_candidates) < top_n:
        for candidate in ranked_candidates:
            if len(selected_candidates) >= top_n:
                break
            
            c_type = candidate["chart_type"]
            x = candidate["x"]
            y = candidate["y"]
            pair = tuple(sorted((x, y))) if c_type == "scatter" else (x, y)
            
            if pair not in used_pairs:
                selected_candidates.append(candidate)
                used_pairs.add(pair)

    return selected_candidates
