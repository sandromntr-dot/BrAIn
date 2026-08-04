import json
from pathlib import Path


class Config:

    def __init__(self):
        self.file = Path("config/settings.json")

    def load(self):
        with self.file.open("r", encoding="utf-8") as file:
            return json.load(file)