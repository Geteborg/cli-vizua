import pandas as pd


def advance_profilling(df: pd.DataFrame, results: dict) -> dict:
    num_columns = []
    advanced_results = {}

    for column_name in results["dtypes"]:
        if (
            results["dtypes"][column_name] == "int64"
            or results["dtypes"][column_name] == "float64"
        ):
            num_columns.append(column_name)

    if num_columns:
        correlation_matrix = df[num_columns].corr(method="pearson")
        advanced_results["correlations"] = correlation_matrix.to_dict()

        variance = df[num_columns].var()
        advanced_results["variances"] = variance.to_dict()

        skewness = df[num_columns].skew()
        advanced_results["skewness"] = skewness.to_dict()

        quantiles = df[num_columns].quantile([0.25, 0.75])

        iqr = quantiles.loc[0.75] - quantiles.loc[0.25]

        lower_bound = quantiles.loc[0.25] - 1.5 * iqr
        upper_bound = quantiles.loc[0.75] + 1.5 * iqr

        outliers = {}

        for column_name in num_columns:
            outliers[column_name] = df[
                (df[column_name] < lower_bound[column_name])
                | (df[column_name] > upper_bound[column_name])
            ].index.tolist()

        advanced_results["outliers"] = outliers

    results.update(advanced_results)

    return results
