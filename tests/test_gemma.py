import json
import unittest
from urllib.error import URLError
from unittest.mock import Mock, patch

from app.ai.gemma import GemmaClient, GemmaError


class GemmaClientTest(unittest.TestCase):

    def test_generates_non_streaming_response(self):
        api_response = {
            "model": "gemma4:latest",
            "response": "Documento financeiro",
            "prompt_eval_count": 12,
            "eval_count": 3,
            "total_duration": 1000,
        }
        response = Mock()
        response.read.return_value = json.dumps(api_response).encode("utf-8")
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)

        with patch("app.ai.gemma.urlopen", return_value=response) as urlopen_mock:
            result = GemmaClient().generate(
                "Classifique este documento",
                system="Responda de forma objetiva",
            )

        request = urlopen_mock.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))

        self.assertEqual(request.full_url, "http://localhost:11434/api/generate")
        self.assertEqual(payload["model"], "gemma4:latest")
        self.assertFalse(payload["stream"])
        self.assertFalse(payload["think"])
        self.assertEqual(payload["system"], "Responda de forma objetiva")
        self.assertEqual(result.text, "Documento financeiro")
        self.assertEqual(result.prompt_tokens, 12)
        self.assertEqual(result.response_tokens, 3)

    def test_rejects_empty_prompt(self):
        with self.assertRaises(ValueError):
            GemmaClient().generate("  ")

    def test_sends_structured_response_format(self):
        response = Mock()
        response.read.return_value = b'{"response": "{}"}'
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        schema = {"type": "object"}

        with patch("app.ai.gemma.urlopen", return_value=response) as urlopen_mock:
            GemmaClient().generate("Analise", response_format=schema)

        request = urlopen_mock.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["format"], schema)

    def test_reports_unavailable_ollama(self):
        with patch(
            "app.ai.gemma.urlopen",
            side_effect=URLError("connection refused"),
        ):
            with self.assertRaisesRegex(GemmaError, "não está disponível"):
                GemmaClient().generate("Olá")

    def test_reports_invalid_json_response(self):
        response = Mock()
        response.read.return_value = b"not-json"
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)

        with patch("app.ai.gemma.urlopen", return_value=response):
            with self.assertRaisesRegex(GemmaError, "resposta inválida"):
                GemmaClient().generate("Olá")


if __name__ == "__main__":
    unittest.main()
