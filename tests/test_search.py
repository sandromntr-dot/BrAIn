import unittest
from unittest.mock import Mock

from app.services.search import SearchService


class SearchServiceTest(unittest.TestCase):

    def test_delegates_search_to_repository(self):
        repository = Mock()
        repository.search.return_value = ["document"]
        service = SearchService(repository)

        results = service.search("architecture", limit=25)

        repository.search.assert_called_once_with("architecture", limit=25)
        self.assertEqual(results, ["document"])


if __name__ == "__main__":
    unittest.main()
