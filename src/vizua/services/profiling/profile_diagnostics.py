def profile_diagnostics(results: dict) -> list[str]:
    lines = []

    # Извлекаем данные из вложенной структуры
    basic = results.get("basic", {})
    missing = results.get("missing", {})
    unique = results.get("unique", {})
    advanced = results.get("advanced", {})

    rows = basic.get("rows", 0)
    duplicated_rows = missing.get("duplicated_rows", 0)
    missing_by_column = missing.get("missing_by_column", {})
    unique_by_column = unique.get("unique_by_column", {})
    dtypes = basic.get("dtypes", {})

    if duplicated_rows == 0:
        lines.append("Дубликатов строк не обнаружено")
    else:
        lines.append(f"Обнаружено {duplicated_rows} дублированных строк")

    for column_name, missing_count in missing_by_column.items():
        if missing_count > 0:
            lines.append(f"Колонка {column_name} имеет {missing_count} пропусков")

    for column_name, unique_count in unique_by_column.items():
        column_is_id = False
        column_name_lower = column_name.replace(" ", "_").lower()

        if (
            column_name_lower == "id"
            or column_name_lower.endswith("_id")
            or column_name_lower.startswith("id_")
            or "uuid" in column_name_lower
        ):
            column_is_id = True

        if rows > 0:
            uniqueness_ratio = unique_count / rows
            if uniqueness_ratio > 0.95 and column_is_id:
                lines.append(
                    f'Колонка "{column_name}" похожа на идентификатор: почти все значения уникальны'
                )
            elif uniqueness_ratio > 0.95 or column_is_id:
                lines.append(
                    f'Колонка "{column_name}" похожа на уникальный технический признак / почти все значения уникальны'
                )

        dtype = dtypes.get(column_name, "")
        if unique_count > 50 and dtype == "object" or dtype == "str":
            lines.append(
                f"Колонка {column_name} имеет высокую кардинальность: {unique_count}"
            )

        if (
            1 < unique_count < 10
            and (dtype == "object" or dtype == "str")
        ):
            lines.append(
                f"Колонка {column_name} подходит для сравнительных категориальных визуализаций"
            )

    num_count = 0
    str_count = 0

    for column_name, dtype in dtypes.items():
        if any(t in str(dtype).lower() for t in ["int", "float"]):
            num_count += 1
        if any(t in str(dtype).lower() for t in ["str", "object"]):
            str_count += 1

    if num_count > 0:
        lines.append(
            "В наборе данных содержатся числовые признаки, пригодные для распределений и сравнений"
        )

    if num_count > 0 and str_count > 0:
        lines.append(
            "В датасете есть сочетание числовых и категориальных признаков, пригодное для bar chart и сравнительного анализа"
        )

    # Выбросы
    outliers = advanced.get("outliers", {})
    for col, info in outliers.items():
        count = info.get("count", 0)
        if count > 0:
            pct = round(count / rows * 100, 1) if rows > 0 else 0
            lines.append(
                f'Колонка "{col}" содержит {count} выброс(ов) ({pct}% строк) по методу IQR'
            )

    # Топ значимые корреляции
    corr = advanced.get("correlations", {})
    seen_pairs: set = set()
    for col_a, row in corr.items():
        for col_b, val in row.items():
            if col_a == col_b:
                continue
            pair = tuple(sorted([col_a, col_b]))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            if abs(val) >= 0.7:
                direction = "положительная" if val > 0 else "отрицательная"
                lines.append(
                    f'Сильная {direction} корреляция между "{col_a}" и "{col_b}": r={round(val, 2)}'
                )
            elif abs(val) >= 0.4:
                direction = "положительная" if val > 0 else "отрицательная"
                lines.append(
                    f'Умеренная {direction} корреляция между "{col_a}" и "{col_b}": r={round(val, 2)}'
                )

    return lines

