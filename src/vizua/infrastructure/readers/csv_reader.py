from pathlib import Path 

import pandas as pd

def read_csv_file(file_path: str) -> pd.DataFrame:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    if not path.is_file():
        raise ValueError(f"Указанный путь не является файлом: {file_path}")
    
    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise ValueError(f"Не удалось прочитать содержимое CSV-файла: {e}") from e
    
    return df
