import json
import os

class DataRepository:
    def __init__(self, file_path: str = "data_storage.json"):
        self.file_path = file_path
        self._initialize_storage()

    def _initialize_storage(self):
        """Membuat file penyimpanan lokal jika belum ada."""
        if not os.path.exists(self.file_path):
            initial_data = {"target_days": 30, "total_pages_read": 0, "logs": []}
            self.save_data(initial_data)

    def load_data(self) -> dict:
        """Membaca data dari file JSON."""
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_data(self, data: dict):
        """Menyimpan data ke file JSON."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)