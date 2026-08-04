from pathlib import Path


class Scanner:
    """Responsável por localizar arquivos em um diretório."""

    def __init__(self, folder: Path):
        self.folder = folder

    def scan(self) -> list[Path]:
        """Retorna todos os arquivos da pasta."""

        if not self.folder.exists():
            return []

        return [
            file
            for file in self.folder.iterdir()
            if file.is_file()
        ]