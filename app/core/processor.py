from pathlib import Path


class DocumentProcessingError(RuntimeError):
    """Erro ao extrair conteúdo de um documento."""


class TextDocumentProcessor:

    def __init__(self, max_characters=12_000):
        if max_characters < 1:
            raise ValueError("max_characters must be greater than zero")

        self.max_characters = max_characters

    def extract(self, path):
        path = Path(path)

        if path.suffix.casefold() != ".txt":
            raise DocumentProcessingError(
                f"Formato ainda não suportado: {path.suffix or 'sem extensão'}"
            )

        try:
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = path.read_text(encoding="cp1252")
        except OSError as error:
            raise DocumentProcessingError(
                f"Não foi possível ler {path}: {error}"
            ) from error

        content = content.strip()

        if not content:
            raise DocumentProcessingError(f"O documento está vazio: {path}")

        return content[:self.max_characters]
