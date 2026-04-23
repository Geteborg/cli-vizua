def select_top_candidates(ranked_candidates: list[dict], top_n: int) -> list[dict]:
    selected_candidates = []
    chart_type_counts = {"boxplot": 0, "histogram": 0, "bar": 0, "scatter": 0}
    x_usage = {candidate["x"]: 0 for candidate in ranked_candidates}
    y_usage = {candidate["y"]: 0 for candidate in ranked_candidates}
    used_pairs = set()

    for candidate in ranked_candidates:
        if len(selected_candidates) == top_n:
            break

        if chart_type_counts[candidate["chart_type"]] == 2:
            continue

        if (candidate["x"], candidate["y"]) in used_pairs:
            continue

        if x_usage[candidate["x"]] == 2:
            continue

        if y_usage[candidate["y"]] == 2:
            continue

        selected_candidates.append(candidate)
        x_usage[candidate["x"]] += 1
        if candidate["y"] != None:
            y_usage[candidate["y"]] += 1
        chart_type_counts[candidate["chart_type"]] += 1
        if candidate["chart_type"] == "scatter":
            used_pairs.add(tuple(sorted((candidate["x"], candidate["y"]))))
        else:
            used_pairs.add((candidate["x"], candidate["y"]))

    if len(selected_candidates) < top_n:
        for candidate in ranked_candidates:
            if len(selected_candidates) == top_n:
                break

            if (candidate["x"], candidate["y"]) in used_pairs:
                continue

            selected_candidates.append(candidate)

            if candidate["chart_type"] == "scatter":
                used_pairs.add(tuple(sorted((candidate["x"], candidate["y"]))))
            else:
                used_pairs.add((candidate["x"], candidate["y"]))

    return selected_candidates
