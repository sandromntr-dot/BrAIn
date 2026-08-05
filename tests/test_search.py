import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from app.ai.embeddings import EmbeddingError
from app.services.search import SearchService


class SearchServiceTest(unittest.TestCase):

    def test_delegates_search_to_repository(self):
        repository = Mock()
        repository.search.return_value = ["document"]
        service = SearchService(repository)

        results = service.search("architecture", limit=25)

        repository.search.assert_called_once_with("architecture", limit=25)
        self.assertEqual(results, ["document"])

    def test_combines_text_and_semantic_results_without_duplicates(self):
        lexical = SimpleNamespace(path=Path("lexical.txt"))
        semantic = SimpleNamespace(
            path=Path("semantic.txt"),
            name="Guide",
            category="Architecture",
            summary="Explains distributed systems.",
        )
        repository = Mock()
        repository.search.return_value = [lexical]
        repository.semantic_search_documents.return_value = [
            (semantic, None, None),
        ]
        client = Mock(model="embeddinggemma:latest")
        client.embed.side_effect = [[1.0, 0.0], [0.9, 0.1]]

        results = SearchService(repository, client).search("system design")

        self.assertEqual(results, [lexical, semantic])
        repository.save_embedding.assert_called_once_with(
            semantic.path,
            client.model,
            "Guide\nArchitecture\nExplains distributed systems.",
            [0.9, 0.1],
        )

    def test_reuses_cached_document_embedding(self):
        document = SimpleNamespace(
            path=Path("guide.txt"),
            name="Guide",
            category="Manual",
            summary="Installation instructions.",
        )
        source = "Guide\nManual\nInstallation instructions."
        repository = Mock()
        repository.search.return_value = []
        repository.semantic_search_documents.return_value = [
            (document, source, [1.0, 0.0]),
        ]
        client = Mock(model="embeddinggemma:latest")
        client.embed.return_value = [1.0, 0.0]

        results = SearchService(repository, client).search("setup")

        self.assertEqual(results, [document])
        client.embed.assert_called_once_with("setup")
        repository.save_embedding.assert_not_called()

    def test_falls_back_to_text_search_when_embeddings_fail(self):
        document = SimpleNamespace(path=Path("guide.txt"))
        repository = Mock()
        repository.search.return_value = [document]
        repository.semantic_search_documents.return_value = []
        client = Mock(model="embeddinggemma:latest")
        client.embed.side_effect = EmbeddingError("Ollama unavailable")

        results = SearchService(repository, client).search("setup")

        self.assertEqual(results, [document])

    def test_cosine_similarity_rejects_vectors_with_different_dimensions(self):
        similarity = SearchService._cosine_similarity([1.0], [1.0, 0.0])

        self.assertEqual(similarity, 0.0)


if __name__ == "__main__":
    unittest.main()
