import pandas as pd


def advanced_profiling(df: pd.DataFrame, results: dict) -> dict:
    """
    Выполняет расширенное профилирование числовых данных: корреляции, вариативность,
    асимметрия, эксцесс и поиск выбросов.
    """
    # Автоматически выбираем все числовые колонки (int, float всех разрядностей)
    num_df = df.select_dtypes(include=['number'])
    num_columns = num_df.columns.tolist()
    advanced_results = {}

    if num_columns:
        # Матрица корреляции Пирсона
        correlation_matrix = num_df.corr(method="pearson")
        advanced_results["correlations"] = correlation_matrix.to_dict()

        # Статистические показатели (рассчитываются сразу для всех колонок)
        variance = num_df.var()
        advanced_results["variances"] = variance.to_dict()

        skewness = num_df.skew()
        advanced_results["skewness"] = skewness.to_dict()

        # Добавляем эксцесс (kurtosis)
        kurtosis = num_df.kurt()
        advanced_results["kurtosis"] = kurtosis.to_dict()

        # Поиск выбросов по методу межквартильного размаха (IQR)
        quantiles = num_df.quantile([0.25, 0.75])
        iqr = quantiles.loc[0.75] - quantiles.loc[0.25]
        lower_bound = quantiles.loc[0.25] - 1.5 * iqr
        upper_bound = quantiles.loc[0.75] + 1.5 * iqr

        outliers = {}
        for column_name in num_columns:
            mask = (num_df[column_name] < lower_bound[column_name]) | (num_df[column_name] > upper_bound[column_name])
            outliers[column_name] = {
                "count": int(mask.sum()),
                "sample_indices": num_df.index[mask].tolist()[:100]  # Ограничиваем список индексов
            }

        advanced_results["outliers"] = outliers

    results.update(advanced_results)
    return results
