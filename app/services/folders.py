from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FolderSettings:
    downloads: bool
    documents: bool
    desktop: bool
    custom_folders: tuple[Path, ...]


class FolderSettingsService:

    def __init__(self, config):
        self.config = config

    def load(self):
        settings = self.config.load()
        monitor = settings["monitor"]
        return FolderSettings(
            downloads=monitor["downloads"],
            documents=monitor["documents"],
            desktop=monitor["desktop"],
            custom_folders=tuple(
                Path(path) for path in settings["custom_folders"]
            ),
        )

    def save(self, downloads, documents, desktop, custom_folders):
        settings = self.config.load()
        settings["monitor"] = {
            "downloads": bool(downloads),
            "documents": bool(documents),
            "desktop": bool(desktop),
        }
        settings["custom_folders"] = self._unique_paths(custom_folders)
        self.config.save(settings)
        return self.load()

    @staticmethod
    def _unique_paths(paths):
        unique = []
        seen = set()

        for value in paths:
            path = Path(value).resolve(strict=False)
            normalized = str(path).casefold()

            if normalized not in seen:
                seen.add(normalized)
                unique.append(str(path))

        return unique
