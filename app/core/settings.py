from dataclasses import dataclass


@dataclass
class Settings:
    monitor_downloads: bool = True
    monitor_documents: bool = True
    monitor_desktop: bool = False