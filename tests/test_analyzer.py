import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from app.core.processor import DocumentProcessingError
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

    def test_uses_gemma_vision_when_text_cannot_be_extracted(self):
        self.processor.extract.side_effect = DocumentProcessingError("OCR")
        visual_processor = Mock()
        visual_processor.supports.return_value = True
        visual_processor.page_count.return_value = 1
        visual_processor.extract_page.return_value = b"slide"
        self.client.generate.return_value = SimpleNamespace(
            text=json.dumps({"summary": "Resumo visual.", "category": "Slide"}),
            prompt_tokens=30,
            response_tokens=10,
        )
        self.repository.save_analysis.return_value = True
        analyzer = DocumentAnalyzer(
            self.client,
            self.repository,
            self.processor,
            visual_processor,
            visual_gemma_client=self.client,
        )

        result = analyzer.analyze(self.document)

        self.assertEqual(result.summary, "Resumo visual.")
        self.assertEqual(
            self.client.generate.call_args.kwargs["images"],
            [b"slide"],
        )

    def test_rejects_visual_response_that_did_not_receive_image(self):
        self.processor.extract.side_effect = DocumentProcessingError("OCR")
        visual_processor = Mock()
        visual_processor.supports.return_value = True
        visual_processor.page_count.return_value = 1
        visual_processor.extract_page.return_value = b"slide"
        visual_client = Mock()
        visual_client.generate.return_value = SimpleNamespace(
            text=json.dumps({
                "summary": "Não consigo ver nenhuma imagem anexada.",
                "category": "Indefinido",
            }),
            prompt_tokens=10,
            response_tokens=5,
        )
        analyzer = DocumentAnalyzer(
            self.client,
            self.repository,
            self.processor,
            visual_processor,
            visual_gemma_client=visual_client,
        )

        with self.assertRaisesRegex(DocumentAnalysisError, "acessar a imagem"):
            analyzer.analyze(self.document)

        self.repository.save_analysis.assert_not_called()

    def test_resumes_visual_analysis_from_saved_page(self):
        self.processor.extract.side_effect = DocumentProcessingError("OCR")
        visual_processor = Mock()
        visual_processor.supports.return_value = True
        visual_processor.page_count.return_value = 2
        visual_processor.extract_page.return_value = b"second-page"
        self.repository.visual_analysis_chunks.return_value = {
            0: json.dumps({
                "summary": "Primeira página já analisada.",
                "category": "Relatório",
            })
        }
        visual_client = Mock()
        visual_client.generate.return_value = SimpleNamespace(
            text=json.dumps({
                "summary": "Segunda página.",
                "category": "Relatório",
            }),
            prompt_tokens=12,
            response_tokens=6,
        )
        self.client.generate.return_value = SimpleNamespace(
            text=json.dumps({
                "summary": "Resumo consolidado.",
                "category": "Relatório",
            }),
            prompt_tokens=15,
            response_tokens=7,
        )
        self.repository.save_analysis.return_value = True
        analyzer = DocumentAnalyzer(
            self.client,
            self.repository,
            self.processor,
            visual_processor,
            visual_gemma_client=visual_client,
        )

        result = analyzer.analyze(self.document)

        self.assertEqual(result.summary, "Resumo consolidado.")
        visual_processor.extract_page.assert_called_once_with(
            self.document.path,
            1,
        )
        self.repository.save_visual_analysis_chunk.assert_called_once()
        self.repository.clear_visual_analysis_chunks.assert_called_once_with(
            self.document.path
        )


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

    def test_returns_next_pending_document_without_analyzing_it(self):
        document = SimpleNamespace(name="document.txt", extension=".txt")
        repository = Mock()
        repository.pending_analysis.return_value = [document]
        analyzer = Mock()

        selected = AnalysisService(repository, analyzer).next_pending_document()

        self.assertIs(selected, document)
        analyzer.analyze.assert_not_called()

    def test_returns_none_when_no_text_document_is_pending(self):
        repository = Mock()
        repository.pending_analysis.return_value = []
        analyzer = Mock()

        outcome = AnalysisService(repository, analyzer).analyze_next()

        self.assertIsNone(outcome)
        analyzer.analyze.assert_not_called()

    def test_reports_pending_text_document_count(self):
        repository = Mock()
        repository.count_pending_analysis.side_effect = range(1, 11)

        count = AnalysisService(repository, Mock()).pending_count()

        self.assertEqual(repository.count_pending_analysis.call_count, 10)
        self.assertEqual(count, 55)

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
            name="program.exe",
            extension=".exe",
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
