import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class GemmaError(RuntimeError):
    """Erro ao comunicar com o modelo local."""


@dataclass(frozen=True)
class GemmaResponse:
    text: str
    model: str
    prompt_tokens: int
    response_tokens: int
    total_duration: int


class GemmaClient:

    def __init__(
        self,
        model="gemma4:latest",
        base_url="http://localhost:11434",
        timeout=300,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(self, prompt, system=None, response_format=None):
        if not prompt or not prompt.strip():
            raise ValueError("prompt must not be empty")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 256,
            },
        }

        if system:
            payload["system"] = system

        if response_format:
            payload["format"] = response_format

        request = Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            raise GemmaError(self._http_error_message(error)) from error
        except TimeoutError as error:
            raise GemmaError(
                "O Gemma excedeu o tempo limite de análise. "
                "O documento permanece pendente e pode ser tentado novamente."
            ) from error
        except URLError as error:
            raise GemmaError(
                "O Ollama local não está disponível em "
                f"{self.base_url}: {error.reason}"
            ) from error
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise GemmaError("O Ollama retornou uma resposta inválida") from error

        if "error" in data:
            raise GemmaError(data["error"])

        if "response" not in data:
            raise GemmaError("A resposta do Ollama não contém texto gerado")

        return GemmaResponse(
            text=data["response"].strip(),
            model=data.get("model", self.model),
            prompt_tokens=data.get("prompt_eval_count", 0),
            response_tokens=data.get("eval_count", 0),
            total_duration=data.get("total_duration", 0),
        )

    @staticmethod
    def _http_error_message(error):
        try:
            data = json.loads(error.read().decode("utf-8"))
            return data.get("error", f"Ollama retornou HTTP {error.code}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return f"Ollama retornou HTTP {error.code}"
