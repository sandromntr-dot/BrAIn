class DashboardService:

    def __init__(self, repository, supported_extensions):
        self.repository = repository
        self.supported_extensions = tuple(supported_extensions)

    def statistics(self):
        return self.repository.statistics(self.supported_extensions)
