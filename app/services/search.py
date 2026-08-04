class SearchService:

    def __init__(self, repository):
        self.repository = repository

    def search(self, query, limit=100):
        return self.repository.search(query, limit=limit)
