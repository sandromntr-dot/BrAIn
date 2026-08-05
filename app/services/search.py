import math

from app.ai.embeddings import EmbeddingError


class SearchService:

    def __init__(self, repository, embedding_client=None, minimum_similarity=0.35):
        self.repository = repository
        self.embedding_client = embedding_client
        self.minimum_similarity = minimum_similarity

    def search(self, query, limit=100):
        text_results = self.repository.search(query, limit=limit)
        query = query.strip()

        if not query or self.embedding_client is None:
            return text_results

        try:
            semantic_results = self._semantic_search(query, limit)
        except EmbeddingError:
            return text_results

        combined = []
        seen_paths = set()

        for document in [*text_results, *semantic_results]:
            if document.path in seen_paths:
                continue
            combined.append(document)
            seen_paths.add(document.path)

            if len(combined) == limit:
                break

        return combined

    def _semantic_search(self, query, limit):
        model = self.embedding_client.model
        candidates = self.repository.semantic_search_documents(model)
        query_embedding = self.embedding_client.embed(query)
        ranked = []

        for document, stored_source, embedding in candidates:
            source = self._document_source(document)

            if embedding is None or stored_source != source:
                embedding = self.embedding_client.embed(source)
                self.repository.save_embedding(
                    document.path,
                    model,
                    source,
                    embedding,
                )

            similarity = self._cosine_similarity(query_embedding, embedding)
            if similarity >= self.minimum_similarity:
                ranked.append((similarity, document))

        ranked.sort(key=lambda item: item[0], reverse=True)
        return [document for _, document in ranked[:limit]]

    @staticmethod
    def _document_source(document):
        return "\n".join(filter(None, (
            document.name,
            document.category,
            document.summary,
        )))

    @staticmethod
    def _cosine_similarity(left, right):
        if len(left) != len(right) or not left:
            return 0.0

        dot_product = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))

        if left_norm == 0 or right_norm == 0:
            return 0.0

        return dot_product / (left_norm * right_norm)
