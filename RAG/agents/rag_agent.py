from typing import List, Dict, Any
import ollama

class RAGAgent:
    """
    The RAG (Retrieval-Augmented Generation) Agent takes the user query
    and retrieved relevant document chunks, and then uses a local Ollama Llama3.2 model
    to synthesize a coherent and informative answer based on the provided context.
    """
    def __init__(self, model_name: str = "llama3.2"):
        """
        Initialize the RAG Agent with a specific Ollama model.
        
        Args:
            model_name (str): Name of the Ollama model to use (default: "llama3")
        """
        self.model_name = model_name

    def generate_response(self, user_query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a response using Ollama Llama3.2, conditioned on the user query and
        the retrieved document chunks.

        Args:
            user_query (str): The original query from the user.
            retrieved_chunks (List[Dict[str, Any]]): A list of relevant document chunks,
                                                     each containing 'text' and 'metadata'.

        Returns:
            Dict[str, Any]: A dictionary containing the generated response text and
                            references to the source chunks.
        """

        if not retrieved_chunks:
            return {"response_text": "I couldn't find enough information to answer your question.", "sources": []}

        context_texts = [chunk["text"] for chunk in retrieved_chunks]
        context_str = "\n\n".join(f"Context from source {i+1}:\n{text}" for i, text in enumerate(context_texts))

        prompt = (
            f"You are an AI assistant tasked with answering questions based *only* on the provided context. "
            f"If the answer cannot be found in the context, state that you don't have enough information. "
            f"Do not make up information.\n\n"
            f"User Query: {user_query}\n\n"
            f"Context:\n{context_str}\n\n"
            f"Answer:"
        )

        generated_text = self._call_ollama(prompt)

        sources = []
        for chunk in retrieved_chunks:
            source_info = {
                "chunk_id": chunk.get("chunk_id"),
                "document_id": chunk.get("metadata", {}).get("document_id"),
                "page": chunk.get("metadata", {}).get("page"),
                "text_snippet": chunk.get("text", "")[:100] + "..." # Small snippet for reference
            }
            sources.append(source_info)

        return {"response_text": generated_text, "sources": sources}

    def _call_ollama(self, prompt: str) -> str:
        """
        Internal method to call the local Ollama model.
        
        Args:
            prompt (str): The complete prompt to send to the model
            
        Returns:
            str: The generated response from the model
        """
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                stream=False
            )
            return response['response']
        except Exception as e:
            return "Error: Could not get response from the LLM."