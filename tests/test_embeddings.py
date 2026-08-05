import json
import unittest
from unittest.mock import patch
from urllib.error import URLError

from app.ai.embeddings import EmbeddingError, OllamaEmbeddingClient


class FakeResponse:

    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.data).encode("utf-8")


class OllamaEmbeddingClientTest(unittest.TestCase):

    @patch("app.ai.embeddings.urlopen")
    def test_generates_embedding(self, urlopen):
        urlopen.return_value = FakeResponse({"embeddings": [[0.1, 0.2]]})
        client = OllamaEmbeddingClient(model="embedding-model")

        embedding = client.embed("document content")

        self.assertEqual(embedding, [0.1, 0.2])
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request.full_url, "http://localhost:11434/api/embed")
        self.assertEqual(payload, {
            "model": "embedding-model",
            "input": "document content",
        })

    def test_rejects_empty_text(self):
        with self.assertRaises(ValueError):
            OllamaEmbeddingClient().embed("  ")

    @patch("app.ai.embeddings.urlopen")
    def test_reports_unavailable_ollama(self, urlopen):
        urlopen.side_effect = URLError("connection refused")

        with self.assertRaisesRegex(EmbeddingError, "não está disponível"):
            OllamaEmbeddingClient().embed("query")


if __name__ == "__main__":
    unittest.main()
