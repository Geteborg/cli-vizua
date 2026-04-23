def generate_pairs(results: dict) -> list[dict]:
    candidates = []
    numerical_columns = []
    categorical_columns = []

    for column_name in results["basic"]["columns"]:
        column_is_id = False

        column_name_lower = column_name.replace(" ", "_").lower()

        if (
            column_name_lower == "id"
            or column_name_lower.endswith("_id")
            or column_name_lower.startswith("id_")
            or "uuid" in column_name_lower
        ):
            column_is_id = True

        if (
            results["basic"]["dtypes"][column_name] == "int64"
            or results["basic"]["dtypes"][column_name] == "float64"
        ) and not column_is_id:
            numerical_columns.append(column_name)

        if (
            results["basic"]["dtypes"][column_name] == "str"
            and not column_is_id
            and results["unique"]["unique_by_column"][column_name] > 1
            and results["unique"]["unique_by_column"][column_name] < 10
        ):
            categorical_columns.append(column_name)

    for num in numerical_columns:
        for cat in categorical_columns:
            candidate = {}
            candidate.update(
                {
                    "chart_type": "bar",
                    "x": cat,
                    "y": num,
                    "title": f"{num} by {cat}",
                    "reason": "Категориальная колонка с низкой кардинальностью и числовая метрика подходят для сравнения.",
                    "source_rule": "category_numeric_bar",
                }
            )
            candidates.append(candidate)

    for num in numerical_columns:
        candidate = {}
        candidate.update(
            {
                "chart_type": "histogram",
                "x": num,
                "y": None,
                "title": f"Distribution by {num}",
                "reason": "Числовая колонка подходит для анализа распределения.",
                "source_rule": "single_numeric_histogram",
            }
        )
        candidates.append(candidate)

    for num in numerical_columns:
        candidate = {}
        candidate.update(
            {
                "chart_type": "boxplot",
                "x": num,
                "y": None,
                "title": f"Distribution by {num}",
                "reason": "омогает оценить разброс значений и возможные выбросы.",
                "source_rule": "single_numeric_boxplot",
            }
        )
        candidates.append(candidate)

    for i in range(len(numerical_columns) - 1):
        for k in range(i + 1, len(numerical_columns)):
            candidate = {}
            candidate.update(
                {
                    "chart_type": "scatter",
                    "x": numerical_columns[i],
                    "y": numerical_columns[k],
                    "title": f"Scatter {numerical_columns[i]} by {numerical_columns[k]}",
                    "reason": "Возможная зависимость числовых признаков.",
                    "source_rule": "numeric_numeric_scatter",
                }
            )
            candidates.append(candidate)

    return candidates
