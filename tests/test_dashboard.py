import unittest
from unittest.mock import Mock

from app.services.dashboard import DashboardService


class DashboardServiceTest(unittest.TestCase):

    def test_requests_statistics_for_supported_extensions(self):
        repository = Mock()
        repository.statistics.return_value = {"available": 10}
        service = DashboardService(repository, (".txt", ".pdf"))

        statistics = service.statistics()

        repository.statistics.assert_called_once_with((".txt", ".pdf"))
        self.assertEqual(statistics, {"available": 10})


if __name__ == "__main__":
    unittest.main()
