import pandas as pd


def profile_dataset(df: pd.DataFrame) -> dict:
    results = {}
    basic = {}
    missing = {}
    unique = {}

    rows, cols = df.shape

    columns = df.columns.tolist()

    dtypes = df.dtypes.astype(str).to_dict()

    basic.update(rows, cols, columns, dtypes)

    missing_by_column = df.isnull().sum().to_dict()

    duplicated_rows = int(df.duplicated().sum())

    missing.update(missing_by_column, duplicated_rows)

    unique_by_column = df.nunique().to_dict()

    unique.update(unique_by_column)

    results['basic'] = basic
    results['missing'] = missing
    results['unique'] = unique

    return results
