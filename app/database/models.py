from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StoredDocument:
    id: int
    name: str
    path: Path
    extension: str | None
    size: int | None
    created_at: str | None
    summary: str | None
    category: str | None
    processed: bool
    indexed_at: str
    available: bool
    missing_at: str | None
    analysis_error: str | None
    analysis_failed_at: str | None


@dataclass(frozen=True)
class AnalysisHistoryEntry:
    id: int
    document_path: Path
    document_name: str
    status: str
    category: str | None
    details: str | None
    created_at: str
