import json
import math
import os
from typing import List, Dict, Any

from agents import ChunkingEmbeddingAgent

class VectorDatabaseConnector:
    """
    Connects to and interacts with a vector database.
    It provides methods for adding documents (embeddings) and performing semantic searches.
    This version uses a JSON file for persistent storage and cosine similarity for search.
    """
    def __init__(self, db_file_path: str = "vector_db.json"):
        self.db_file_path = db_file_path
        if not os.path.exists(self.db_file_path):
            with open(self.db_file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def _load_db(self) -> Dict[str, Dict[str, Any]]:
        """Loads the entire database from the JSON file."""
        try:
            with open(self.db_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
        except FileNotFoundError:
            return {}

    def _save_db(self, db_data: Dict[str, Dict[str, Any]]):
        """Saves the entire database to the JSON file."""
        try:
            with open(self.db_file_path, 'w', encoding='utf-8') as f:
                json.dump(db_data, f, indent=4)
        except Exception as e:
            pass

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculates the cosine similarity between two vectors.
        Cosine similarity is a measure of similarity between two non-zero vectors
        of an inner product space that measures the cosine of the angle between them.
        """
        dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(v1**2 for v1 in vec1))
        magnitude2 = math.sqrt(sum(v2**2 for v2 in vec2))

        if not magnitude1 or not magnitude2:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

    def add_documents(self, document_id: str, chunks_with_embeddings: List[Dict[str, Any]]) -> bool:
        """
        Adds multiple document chunks and their embeddings to the vector database.
        Stores the data in the JSON file.

        Args:
            document_id (str): The ID of the original document.
            chunks_with_embeddings (List[Dict[str, Any]]): A list of dictionaries,
                                                           each containing 'chunk_id', 'text', 'embedding' (List[float]), and 'metadata'.

        Returns:
            bool: True if documents were added successfully, False otherwise.
        """
        try:
            db_data = self._load_db()
            for chunk_info in chunks_with_embeddings:
                chunk_id = chunk_info['chunk_id']
                db_data[chunk_id] = {
                    "text": chunk_info["text"],
                    "embedding": chunk_info["embedding"],
                    "metadata": {**chunk_info["metadata"], "document_id": document_id}
                }
            self._save_db(db_data)
            return True
        except Exception as e:
            return False

    def search(self, query_embedding_or_text: Any, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a semantic search in the vector database to find the most relevant chunks
        using cosine similarity.

        Args:
            query_embedding_or_text (Any): The query (either raw text or its pre-generated embedding).
            top_k (int): The number of top relevant chunks to retrieve.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a retrieved chunk
                                  with its text, metadata, and score.
        """
        retrieved_chunks = []
        db_data = self._load_db()

        if not db_data:
            return []

        query_embedding = None
        if isinstance(query_embedding_or_text, list) and all(isinstance(x, (float, int)) for x in query_embedding_or_text):
            query_embedding = [float(x) for x in query_embedding_or_text]
        elif isinstance(query_embedding_or_text, str):
            temp_chunk_embedder = ChunkingEmbeddingAgent()
            query_embedding = temp_chunk_embedder._generate_embedding(query_embedding_or_text)
        else:
            return []

        if not query_embedding:
            return []

        scores = []
        for chunk_id, chunk_data in db_data.items():
            db_embedding = chunk_data["embedding"]
            if len(query_embedding) != len(db_embedding):
                continue
            similarity = self._cosine_similarity(query_embedding, db_embedding)
            scores.append((similarity, chunk_id, chunk_data))

        scores.sort(key=lambda x: x[0], reverse=True)

        for i in range(min(top_k, len(scores))):
            similarity, chunk_id, chunk_data = scores[i]
            retrieved_chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_data["text"],
                "metadata": chunk_data["metadata"],
                "score": similarity
            })

        return retrieved_chunks