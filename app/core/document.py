from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Document:
    name: str
    path: str
    extension: str
    size: int
    created_at: datetime = field(default_factory=datetime.now)
    category: str | None = None
    summary: str | None = None