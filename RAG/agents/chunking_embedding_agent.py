from typing import List, Dict, Any
import hashlib
import ollama

class ChunkingEmbeddingAgent:
    """
    The Chunking/Embedding Agent takes parsed text, breaks it into smaller,
    manageable chunks, and then generates vector embeddings for each chunk.
    These embeddings are numerical representations of the text's semantic meaning.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, 
                 embedding_model: str = "llama3.2"):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model

    def _chunk_text(self, text: str) -> List[str]:
        """
        Breaks down a long text into smaller chunks with optional overlap.
        This is a simple character-based chunking. More advanced methods
        might consider sentences, paragraphs, or token limits.

        Args:
            text (str): The input text to be chunked.

        Returns:
            List[str]: A list of text chunks.
        """
        chunks = []
        if not text:
            return chunks

        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += (self.chunk_size - self.chunk_overlap)
            if self.chunk_overlap > 0 and start >= len(text):
                break

        if start - (self.chunk_size - self.chunk_overlap) < len(text) and text[start-(self.chunk_size - self.chunk_overlap):] not in chunks:
             if len(text) > start - (self.chunk_size - self.chunk_overlap):
                chunks.append(text[start-(self.chunk_size - self.chunk_overlap):])

        seen_chunks = set()
        unique_chunks = []
        for chunk in chunks:
            if chunk not in seen_chunks:
                unique_chunks.append(chunk)
                seen_chunks.add(chunk)
        return unique_chunks

    def _generate_embedding(self, text_chunk: str) -> List[float]:
        """
        Generates a vector embedding for a given text chunk using Ollama.

        Args:
            text_chunk (str): The text chunk to embed.

        Returns:
            List[float]: A list of floats representing the vector embedding.
        """
        try:
            response = ollama.embeddings(model=self.embedding_model, prompt=text_chunk)
            return response['embedding']
        except Exception as e:
            return [float(ord(c)) / 100 for c in text_chunk[:100]] + [0.0] * max(0, 100 - len(text_chunk))

    def process(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Processes parsed document data: chunks the text and generates embeddings.

        Args:
            parsed_data (Dict[str, Any]): A dictionary containing 'text' and 'metadata'.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing 'chunk_id',
                                  'text', 'embedding', and 'metadata'.
        """
        text = parsed_data.get("text", "")
        metadata = parsed_data.get("metadata", {})
        chunks_with_embeddings = []

        if not text:
            return chunks_with_embeddings

        text_chunks = self._chunk_text(text)

        for i, chunk in enumerate(text_chunks):
            embedding = self._generate_embedding(chunk)
            chunk_id = hashlib.md5((chunk + str(i)).encode('utf-8')).hexdigest()

            chunk_info = {
                "chunk_id": chunk_id,
                "text": chunk,
                "embedding": embedding,
                "metadata": {**metadata, "chunk_index": i}
            }
            chunks_with_embeddings.append(chunk_info)

        return chunks_with_embeddings