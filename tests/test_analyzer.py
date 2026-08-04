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
        document = SimpleNamespace(
            name="document.txt",
            extension=".txt",
        )
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
        repository.count_pending_analysis.side_effect = [3, 4, 5, 6, 7, 8]

        count = AnalysisService(repository, Mock()).pending_count()

        self.assertEqual(repository.count_pending_analysis.call_count, 6)
        self.assertEqual(count, 33)

    def test_analyzes_docx_when_no_text_document_is_pending(self):
        document = SimpleNamespace(
            name="document.docx",
            extension=".docx",
        )
        repository = Mock()
        repository.pending_analysis.side_effect = [[], [document]]
        analyzer = Mock()
        analyzer.analyze.return_value = SimpleNamespace(category="Report")

        outcome = AnalysisService(repository, analyzer).analyze_next()

        self.assertEqual(outcome.document, document)
        self.assertEqual(repository.pending_analysis.call_count, 2)
        analyzer.analyze.assert_called_once_with(document)

    def test_analyzes_selected_supported_document(self):
        document = SimpleNamespace(
            name="selected.pdf",
            extension=".pdf",
            available=True,
        )
        analyzer = Mock()
        analyzer.analyze.return_value = SimpleNamespace(category="Report")
        service = AnalysisService(Mock(), analyzer)

        outcome = service.analyze_document(document)

        analyzer.analyze.assert_called_once_with(document)
        self.assertEqual(outcome.document, document)
        self.assertTrue(service.supports(document))

    def test_rejects_selected_unsupported_document(self):
        document = SimpleNamespace(
            name="image.png",
            extension=".png",
            available=True,
        )
        service = AnalysisService(Mock(), Mock())

        with self.assertRaisesRegex(DocumentAnalysisError, "não suportado"):
            service.analyze_document(document)

        self.assertFalse(service.supports(document))

    def test_persists_failure_and_allows_queue_to_continue(self):
        document = SimpleNamespace(
            name="scan.pdf",
            path=Path("scan.pdf"),
            extension=".pdf",
            available=True,
        )
        repository = Mock()
        analyzer = Mock()
        analyzer.analyze.side_effect = RuntimeError("OCR required")
        service = AnalysisService(repository, analyzer)

        with self.assertRaisesRegex(RuntimeError, "OCR required"):
            service.analyze_document(document)

        repository.save_analysis_error.assert_called_once_with(
            document.path,
            analyzer.analyze.side_effect,
        )


if __name__ == "__main__":
    unittest.main()
