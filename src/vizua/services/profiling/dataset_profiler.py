import pandas as pd

def profile_dataset(df: pd.DataFrame) -> dict:
    results = {}

    rows, cols = df.shape

    columns = df.columns.tolist()

    dtypes = df.dtypes.astype(str).to_dict()

    missing_by_column = df.isnull().sum().to_dict()
    
    duplicated_rows = int(df.duplicated().sum())

    unique_by_column = df.nunique().to_dict()

    results.update({'rows' : rows, 'cols' : cols, 'columns' : columns, 'dtypes' : dtypes, 'missing_by_column' : missing_by_column, 'duplicated_rows' : duplicated_rows, 'unique_by_column' : unique_by_column})



    return results