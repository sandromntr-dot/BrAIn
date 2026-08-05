import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class EmbeddingError(RuntimeError):
    """Erro ao gerar embeddings com o Ollama local."""


class OllamaEmbeddingClient:

    def __init__(
        self,
        model="embeddinggemma:latest",
        base_url="http://localhost:11434",
        timeout=60,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def embed(self, text):
        if not text or not text.strip():
            raise ValueError("text must not be empty")

        request = Request(
            f"{self.base_url}/api/embed",
            data=json.dumps({
                "model": self.model,
                "input": text.strip(),
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise EmbeddingError(self._http_error_message(error)) from error
        except TimeoutError as error:
            raise EmbeddingError(
                "O Ollama excedeu o tempo limite ao gerar o embedding"
            ) from error
        except URLError as error:
            raise EmbeddingError(
                "O Ollama local não está disponível em "
                f"{self.base_url}: {error.reason}"
            ) from error
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise EmbeddingError("O Ollama retornou um embedding inválido") from error

        embeddings = data.get("embeddings")
        if not embeddings or not isinstance(embeddings[0], list):
            raise EmbeddingError("O Ollama não retornou um vetor de embedding")

        return embeddings[0]

    @staticmethod
    def _http_error_message(error):
        try:
            data = json.loads(error.read().decode("utf-8"))
            return data.get("error", f"Ollama retornou HTTP {error.code}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return f"Ollama retornou HTTP {error.code}"
