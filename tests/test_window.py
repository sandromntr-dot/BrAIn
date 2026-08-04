import queue
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from app.ui.window import MainWindow


class BatchAnalysisTest(unittest.TestCase):

    def test_batch_skips_failure_and_continues_with_next_document(self):
        error = RuntimeError("arquivo sem texto")
        outcome = SimpleNamespace(
            document=SimpleNamespace(name="documento.txt"),
        )
        window = MainWindow.__new__(MainWindow)
        window.analysis_service = Mock()
        first = SimpleNamespace(name="falha.pdf")
        second = outcome.document
        window.analysis_service.next_pending_document.side_effect = [
            first,
            second,
            None,
        ]
        window.analysis_service.analyze_document.side_effect = [error, outcome]
        window._batch_stop_requested = threading.Event()
        window._batch_events = queue.Queue()

        window._run_batch_analysis()

        self.assertEqual(
            window.analysis_service.next_pending_document.call_count,
            3,
        )
        self.assertEqual(window.analysis_service.analyze_document.call_count, 2)
        self.assertEqual(
            list(window._batch_events.queue),
            [
                ("started", first, 0, 0),
                ("progress", 0, 1, None, error),
                ("started", second, 0, 1),
                ("progress", 1, 1, outcome, None),
                ("finished", 1, 1, False),
            ],
        )


class SearchInteractionTest(unittest.TestCase):

    def test_search_button_updates_results_and_visible_counter(self):
        documents = [SimpleNamespace(name="report.pdf")]
        window = MainWindow.__new__(MainWindow)
        window.query = Mock()
        window.query.get.return_value = "  report  "
        window.search_service = Mock()
        window.search_service.search.return_value = documents
        window.results = Mock()
        window.result_count = Mock()
        window.status = Mock()

        window.search()

        window.search_service.search.assert_called_once_with("report")
        window.results.set_documents.assert_called_once_with(documents)
        window.result_count.set.assert_called_once_with("1 resultado(s)")
        window.status.set.assert_called_once_with(
            "Busca concluída: 1 documento(s) encontrado(s)"
        )


if __name__ == "__main__":
    unittest.main()
