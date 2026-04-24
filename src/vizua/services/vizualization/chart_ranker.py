def rank_pairs(candidates: list[dict], results: dict, top_n: int) -> list[dict]:
    ranked_candidates = []

    def is_numeric(col):
        """Вспомогательная функция для проверки типа колонки."""
        dtype = results.get("basic", {}).get("dtypes", {}).get(col, "")
        return any(t in str(dtype).lower() for t in ["int", "float"])

    for candidate in candidates:
        advanced = results.get("advanced", {})
        chart_type = candidate["chart_type"]
        x = candidate["x"]
        y = candidate["y"]
        score = 0
        base = 20

        if chart_type == "bar":
            # Проверка на пропуски (безопасный доступ через get)
            missing = results.get("missing", {}).get("missing_by_column", {})
            if missing.get(x) == 0 and (not y or missing.get(y) == 0):
                score += 10

            # Оценка кардинальности категории
            unique_count = results.get("unique", {}).get("unique_by_column", {}).get(x, 0)
            if 2 <= unique_count <= 10:
                score += 30
            elif 11 <= unique_count <= 20:
                score += 10
            else:
                score -= 50

            # Для Bar-chart Y обычно должен быть числовым
            if y and is_numeric(y):
                score += 20

        elif chart_type == "histogram":
            if is_numeric(x):
                score += 20

            if results.get("missing", {}).get("missing_by_column", {}).get(x) == 0:
                score += 10

            # Бонус за интересное распределение (асимметрия/эксцесс)
            skew = advanced.get("skewness", {}).get(x, 0)
            kurt = advanced.get("kurtosis", {}).get(x, 3)
            if abs(skew) > 1 or (kurt - 3) > 0:
                score += 25

        elif chart_type == "boxplot":
            if is_numeric(x):
                score += 20

            if results.get("missing", {}).get("missing_by_column", {}).get(x) == 0:
                score += 10

            # Главная ценность Boxplot — отображение выбросов
            outlier_info = advanced.get("outliers", {}).get(x, {})
            if outlier_info.get("count", 0) > 0:
                score += 40

        elif chart_type == "scatter":
            if is_numeric(x) and is_numeric(y):
                score += 20

            missing = results.get("missing", {}).get("missing_by_column", {})
            if missing.get(x) == 0 and missing.get(y) == 0:
                score += 10
            
            # Корреляция Пирсона (бонус за взаимосвязь)
            correlations = advanced.get("correlations", {})
            if x in correlations and y in correlations[x]:
                corr_val = correlations[x][y]
                score += int(abs(corr_val) * 60)

        candidate.update({"score": score + base})
        ranked_candidates.append(candidate)

    ranked_candidates = sorted(
        ranked_candidates, key=lambda candidate: candidate["score"], reverse=True
    )

    return ranked_candidates
