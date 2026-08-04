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


if __name__ == "__main__":
    unittest.main()
