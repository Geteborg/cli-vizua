import uuid
import pandas as pd
from typing import Dict, Any, Optional
from io import BytesIO, StringIO


class DatasetManager:
    """
    Управляет сессиями и загруженными датасетами в памяти бэкенда.
    """
    def __init__(self):
        self._datasets: Dict[str, Dict[str, Any]] = {}

    def add_dataset(self, filename: str, content: bytes) -> str:
        """
        Парсит CSV из байтов и сохраняет датасет. Возвращает уникальный dataset_id.
        """
        dataset_id = str(uuid.uuid4())[:8]
        
        try:
            # Читаем CSV с помощью pandas
            df = pd.read_csv(BytesIO(content))
        except Exception as e:
            # Резервное чтение с utf-8 / latin-1
            try:
                text = content.decode("utf-8", errors="replace")
                df = pd.read_csv(StringIO(text))
            except Exception as inner_e:
                raise ValueError(f"Не удалось распознать CSV-файл: {e}")

        self._datasets[dataset_id] = {
            "id": dataset_id,
            "filename": filename,
            "df": df,
            "profile_cache": None,
            "candidates_cache": None
        }
        return dataset_id

    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        return self._datasets.get(dataset_id)

    def get_dataframe(self, dataset_id: str) -> Optional[pd.DataFrame]:
        item = self.get_dataset(dataset_id)
        return item["df"] if item else None

    def list_datasets(self) -> list[dict]:
        return [
            {
                "id": d_id,
                "filename": item["filename"],
                "rows": item["df"].shape[0],
                "cols": item["df"].shape[1]
            }
            for d_id, item in self._datasets.items()
        ]

    def delete_dataset(self, dataset_id: str) -> bool:
        if dataset_id in self._datasets:
            del self._datasets[dataset_id]
            return True
        return False


dataset_manager = DatasetManager()
