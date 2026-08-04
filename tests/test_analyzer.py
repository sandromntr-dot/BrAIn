import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from app.services.analyzer import (
    AnalysisService,
    DocumentAnalyzer,
    DocumentAnalysisError,
)


class DocumentAnalyzerTest(unittest.TestCase):

    def setUp(self):
        self.client = Mock()
        self.repository = Mock()
        self.processor = Mock()
        self.processor.extract.return_value = "Document content"
        self.document = SimpleNamespace(
            name="document.txt",
            path=Path("document.txt"),
        )
        self.analyzer = DocumentAnalyzer(
            self.client,
            self.repository,
            self.processor,
        )

    def test_analyzes_and_persists_document(self):
        self.client.generate.return_value = SimpleNamespace(
            text=json.dumps({
                "summary": "Resumo do documento.",
                "category": "Relatório",
            }),
            prompt_tokens=20,
            response_tokens=8,
        )
        self.repository.save_analysis.return_value = True

        result = self.analyzer.analyze(self.document)

        self.repository.save_analysis.assert_called_once_with(
            self.document.path,
            "Resumo do documento.",
            "Relatório",
        )
        self.assertEqual(result.summary, "Resumo do documento.")
        self.assertEqual(result.category, "Relatório")
        self.assertEqual(result.prompt_tokens, 20)
        self.assertEqual(result.response_tokens, 8)

    def test_rejects_invalid_model_response(self):
        self.client.generate.return_value = SimpleNamespace(
            text="not-json",
            prompt_tokens=0,
            response_tokens=0,
        )

        with self.assertRaisesRegex(DocumentAnalysisError, "não é JSON"):
            self.analyzer.analyze(self.document)

        self.repository.save_analysis.assert_not_called()


class AnalysisServiceTest(unittest.TestCase):

    def test_analyzes_next_pending_text_document(self):
        document = SimpleNamespace(name="document.txt")
        analysis = SimpleNamespace(category="Report")
        repository = Mock()
        repository.pending_analysis.return_value = [document]
        analyzer = Mock()
        analyzer.analyze.return_value = analysis

        outcome = AnalysisService(repository, analyzer).analyze_next()

        repository.pending_analysis.assert_called_once_with(
            extension=".txt",
            limit=1,
        )
        analyzer.analyze.assert_called_once_with(document)
        self.assertEqual(outcome.document, document)
        self.assertEqual(outcome.analysis, analysis)

    def test_returns_none_when_no_text_document_is_pending(self):
        repository = Mock()
        repository.pending_analysis.return_value = []
        analyzer = Mock()

        outcome = AnalysisService(repository, analyzer).analyze_next()

        self.assertIsNone(outcome)
        analyzer.analyze.assert_not_called()

    def test_reports_pending_text_document_count(self):
        repository = Mock()
        repository.count_pending_analysis.return_value = 3

        count = AnalysisService(repository, Mock()).pending_count()

        repository.count_pending_analysis.assert_called_once_with(extension=".txt")
        self.assertEqual(count, 3)


if __name__ == "__main__":
    unittest.main()
