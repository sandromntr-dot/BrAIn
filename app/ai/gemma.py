import base64
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

    def generate(self, prompt, system=None, response_format=None, images=None):
        if not prompt or not prompt.strip():
            raise ValueError("prompt must not be empty")

        options = {
            "temperature": 0.2,
            "num_predict": 256,
        }
        payload = {
            "model": self.model,
            "stream": False,
            "think": False,
            "options": options,
        }

        if images:
            messages = []

            if system:
                messages.append({"role": "system", "content": system})

            messages.append({
                "role": "user",
                "content": prompt,
                "images": [
                    base64.b64encode(image).decode("ascii")
                    for image in images
                ],
            })
            payload["messages"] = messages
            endpoint = "/api/chat"
        else:
            payload["prompt"] = prompt
            endpoint = "/api/generate"

        if system and not images:
            payload["system"] = system

        if response_format:
            payload["format"] = response_format

        request = Request(
            f"{self.base_url}{endpoint}",
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

        if images:
            generated_text = data.get("message", {}).get("content")
        else:
            generated_text = data.get("response")

        if generated_text is None:
            raise GemmaError("A resposta do Ollama não contém texto gerado")

        return GemmaResponse(
            text=generated_text.strip(),
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
