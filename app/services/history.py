class AnalysisHistoryService:

    def __init__(self, repository):
        self.repository = repository

    def recent(self, limit=100):
        return self.repository.analysis_history(limit=limit)
