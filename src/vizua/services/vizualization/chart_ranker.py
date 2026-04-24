def rank_pairs(candidates: list[dict], results: dict, top_n: int) -> list[dict]:
    ranked_candidates = []

    for candidate in candidates:
        chart_type = candidate["chart_type"]
        x = candidate["x"]
        y = candidate["y"]

        if chart_type == "bar":
            score = 0
            base = 2

            if (
                results["missing"]["missing_by_column"][x] == 0
                and results["missing"]["missing_by_column"][y] == 0
            ):
                score += 1

            if (
                results["unique"]["unique_by_column"][x] >= 2
                and results["unique"]["unique_by_column"][x] <= 8
            ):
                score += 3

            if (
                results["unique"]["unique_by_column"][x] >= 9
                and results["unique"]["unique_by_column"][x] <= 15
            ):
                score += 1

            if (
                results["unique"]["unique_by_column"][x] > 15
                or results["unique"]["unique_by_column"][x] < 2
            ):
                score += -3

            if (
                results["basic"]["dtypes"][y] == "int64"
                or results["basic"]["dtypes"][y] == "float64"
            ):
                score += 2

            score += base
            candidate.update({"score": score})

        elif chart_type == "histogram":
            score = 0
            base = 2

            if (
                results["basic"]["dtypes"][x] == "int64"
                or results["basic"]["dtypes"][x] == "float64"
            ):
                score += 2

            if results["missing"]["missing_by_column"][x] == 0:
                score += 1

            score += base
            candidate.update({"score": score})

        elif chart_type == "boxplot":
            score = 0
            base = 2

            if (
                results["basic"]["dtypes"][x] == "int64"
                or results["basic"]["dtypes"][x] == "float64"
            ):
                score += 2

            if results["missing"]["missing_by_column"][x] == 0:
                score += 1

            score += base
            candidate.update({"score": score})

        elif chart_type == "scatter":
            score = 0
            base = 2

            if (
                results["basic"]["dtypes"][x] == "int64"
                or results["basic"]["dtypes"][x] == "float64"
            ) and (
                results["basic"]["dtypes"][y] == "int64"
                or results["basic"]["dtypes"][y] == "float64"
            ):
                score += 2

            if (
                results["missing"]["missing_by_column"][x] == 0
                and results["missing"]["missing_by_column"][y] == 0
            ):
                score += 1

            score += base
            candidate.update({"score": score})

        ranked_candidates.append(candidate)

    ranked_candidates = sorted(
        ranked_candidates, key=lambda candidate: candidate["score"], reverse=True
    )

    return ranked_candidates
