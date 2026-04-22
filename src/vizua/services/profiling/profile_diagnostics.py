def profile_diagnostics(results: dict) -> list[str]:
    lines = []
    
    if results["duplicated_rows"] == 0:
        lines.append(f'Дубликатов строк не обнаружено')
    else:
        lines.append(f'Обнаружено {results["duplicated_rows"]} дублированных строк')
    
    for column_name in results['missing_by_column']:
        missing_count = results['missing_by_column'][column_name]

        if missing_count > 0:
            lines.append(f'Колонка {column_name} имеет {missing_count} пропусков')
    
    for column_name in results['unique_by_column']:
        
        unique_count = results['unique_by_column'][column_name]

        column_is_id = False

        column_name_lower = column_name.replace(" ", "_").lower()
        
        if column_name_lower == "id" or column_name_lower.endswith("_id") or column_name_lower.startswith("id_") or "uuid" in column_name_lower:
            column_is_id = True


        if float(unique_count /  results["rows"]) > 0.95 and column_is_id:
            lines.append(f'Колонка "{column_name}" похожа на идентификатор: почти все значения уникальны')
        
        elif float(unique_count /  results["rows"]) > 0.95 or column_is_id:
            lines.append(f'Колонка "{column_name}" похожа на уникальный технический признак / почти все значения уникальны')

        if unique_count > 50 and results['dtypes'][column_name] == 'str':
            lines.append(f'Колонка {column_name} имеет высокую кардинальность: {unique_count}')

        if  unique_count < 10 and unique_count > 1 and results['dtypes'][column_name] == 'str':
            lines.append(f'Колонка {column_name} подходит для сравнительных категориальных визуализаций')
    
    num_count = 0
    str_count = 0
    
    for column_name in results['dtypes']:
        if results['dtypes'][column_name] == 'int64' or results['dtypes'][column_name] == 'float64':
            num_count += 1
        if results['dtypes'][column_name] == 'str':
            str_count += 1
    
    if num_count > 0:
        lines.append(f'В наборе данных содержатся числовые признаки, пригодные для распределений и сравнений')
    
    if num_count > 0 and str_count > 0:
        lines.append(f'В датасете есть сочетание числовых и категориальных признаков, пригодное для bar chart и сравнительного анализа')
    
    return lines