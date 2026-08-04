"""
Утилиты для построения компактных промптов из профиля датасета.
Исключает тяжёлые матрицы корреляций и сырые индексы выбросов,
оставляя только содержательную статистику для ИИ-промптов.
"""
from typing import Any, Dict


def build_insights_context(profile_results: dict) -> Dict[str, Any]:
    """
    Формирует компактный контекст из полного профиля датасета для ИИ-промптов.
    """
    basic = profile_results.get("basic", {})
    missing = profile_results.get("missing", {})
    unique = profile_results.get("unique", {})
    advanced = profile_results.get("advanced", {})

    # Компактная статистика по выбросам
    outliers_summary = {}
    for col, info in advanced.get("outliers", {}).items():
        count = info.get("count", 0)
        if count > 0:
            outliers_summary[col] = count

    # Топ-5 значимых корреляций
    top_correlations = []
    corr = advanced.get("correlations", {})
    seen_pairs = set()
    for col_a, row in corr.items():
        for col_b, val in row.items():
            if col_a == col_b:
                continue
            pair = tuple(sorted([col_a, col_b]))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            if abs(val) >= 0.4:
                top_correlations.append({
                    "pair": f"{col_a} / {col_b}",
                    "pearson_r": round(val, 3)
                })

    top_correlations.sort(key=lambda x: abs(x["pearson_r"]), reverse=True)
    top_correlations = top_correlations[:5]

    # Асимметрия — только «интересные» колонки
    skewness_notable = {
        col: round(val, 2)
        for col, val in advanced.get("skewness", {}).items()
        if abs(val) > 1.0
    }

    return {
        "shape": {"rows": basic.get("rows", 0), "cols": basic.get("cols", 0)},
        "columns": basic.get("columns", []),
        "dtypes": basic.get("dtypes", {}),
        "missing_values": {
            col: cnt
            for col, cnt in missing.get("missing_by_column", {}).items()
            if cnt > 0
        },
        "duplicated_rows": missing.get("duplicated_rows", 0),
        "unique_counts": unique.get("unique_by_column", {}),
        "outliers_by_column": outliers_summary,
        "top_correlations": top_correlations,
        "high_skewness_columns": skewness_notable,
    }
