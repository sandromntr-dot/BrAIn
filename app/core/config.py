import json
from pathlib import Path


class Config:

    def __init__(self):
        self.file = Path("config/settings.json")

    def load(self):
        with self.file.open("r", encoding="utf-8") as file:
            settings = json.load(file)

        monitor = settings.setdefault("monitor", {})
        monitor.setdefault("downloads", True)
        monitor.setdefault("documents", True)
        monitor.setdefault("desktop", False)
        settings.setdefault("custom_folders", [])
        settings.setdefault("frequency", "manual")
        return settings

    def save(self, settings):
        self.file.parent.mkdir(parents=True, exist_ok=True)
        temporary_file = self.file.with_suffix(".json.tmp")
        temporary_file.write_text(
            json.dumps(settings, ensure_ascii=False, indent=4) + "\n",
            encoding="utf-8",
        )
        temporary_file.replace(self.file)

    def monitored_folders(self, settings=None):
        settings = settings or self.load()
        monitor = settings["monitor"]
        folders = []

        if monitor["downloads"]:
            folders.append(Path.home() / "Downloads")

        if monitor["documents"]:
            folders.append(Path.home() / "Documents")

        if monitor["desktop"]:
            folders.append(Path.home() / "Desktop")

        folders.extend(Path(path) for path in settings["custom_folders"])

        unique_folders = []
        seen = set()

        for folder in folders:
            normalized = str(folder.resolve(strict=False)).casefold()

            if normalized not in seen:
                seen.add(normalized)
                unique_folders.append(folder)

        return unique_folders
