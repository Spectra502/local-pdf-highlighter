import numpy as np

class Searcher:
    def __init__(self, indexer):
        self.indexer = indexer

    def search(self, query, k=3, threshold=0.0):
        if not self.indexer.index or self.indexer.embeddings is None:
            return []

        # Encode query
        query_embedding = self.indexer.model.encode(
            [query],
            normalize_embeddings=True
        )[0]

        # Compute cosine similarity
        # Since embeddings are normalized, dot product is cosine similarity
        similarities = np.dot(self.indexer.embeddings, query_embedding)

        # Get top k indices
        top_k_indices = np.argsort(similarities)[::-1][:k]

        results = []
        for idx in top_k_indices:
            score = float(similarities[idx])
            if score >= threshold:
                item = self.indexer.index[idx].copy()
                item['score'] = score
                results.append(item)

        return results
