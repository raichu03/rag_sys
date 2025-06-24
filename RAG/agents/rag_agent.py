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
        Initialize the RAG Agent with a specific Ollama model and an empty conversation history.
        
        Args:
            model_name (str): Name of the Ollama model to use (default: "llama3.2")
        """
        self.model_name = model_name
        self.conversation_history: List[Dict[str, str]] = []
        self._initialize_system_prompt()

    def _initialize_system_prompt(self):
        """
        Initializes the conversation history with a system prompt.
        This prompt guides the AI's behavior throughout the conversation.
        """
        system_prompt = (
            "You are a highly accurate and concise AI assistant. Your primary goal is to answer "
            "questions based *solely* on the provided context information. "
            "Follow these strict rules:\n"
            "1. **Use only the provided context:** Do not use any outside knowledge. "
            "2. **Directly answer:** Provide a direct and factual answer based on the context. "
            "3. **State limitations:** If the answer cannot be found or fully inferred from the "
            "   given context, clearly state: 'I don't have enough information in the provided context to answer that.' "
            "4. **No fabrication:** Never make up information or speculate beyond the context. "
            "5. **Conciseness:** Be brief and to the point. Avoid verbose explanations. "
            "6. **Attribution (Implicit):** While you don't need to explicitly cite sources within the answer, "
            "   ensure your response is clearly derived from the provided 'Context' section."
        )
        self.conversation_history.append({"role": "system", "content": system_prompt})

    def generate_response(self, user_query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a response using Ollama Llama3.2, conditioned on the user query and
        the retrieved document chunks. The conversation history is maintained for context.

        Args:
            user_query (str): The original query from the user.
            retrieved_chunks (List[Dict[str, Any]]): A list of relevant document chunks,
                                                     each containing 'text' and 'metadata'.

        Returns:
            Dict[str, Any]: A dictionary containing the generated response text and
                            references to the source chunks.
        """

        if not retrieved_chunks:
            self.conversation_history.append({"role": "user", "content": user_query})
            response_text = "I couldn't find enough information in the provided context to answer your question."
            self.conversation_history.append({"role": "assistant", "content": response_text})
            return {"response_text": response_text, "sources": []}

        context_texts = [chunk["text"] for chunk in retrieved_chunks]
        context_str = "\n\n".join(f"Context from source {i+1}:\n{text}" for i, text in enumerate(context_texts))

        user_message_content = (
            f"User Query: {user_query}\n\n"
            f"Context:\n{context_str}\n\n"
            f"Answer:"
        )

        self.conversation_history.append({"role": "user", "content": user_message_content})

        generated_text = self._call_ollama(self.conversation_history)

        self.conversation_history.append({"role": "assistant", "content": generated_text})

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

    def _call_ollama(self, messages: List[Dict[str, str]]) -> str:
        """
        Internal method to call the local Ollama model using the chat API.
        
        Args:
            messages (List[Dict[str, str]]): The conversation history including system, user, and assistant messages.
            
        Returns:
            str: The generated response from the model.
        """
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                stream=False
            )
            return response['message']['content']
        except Exception as e:
            if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                self.conversation_history.pop()
            print(f"Error calling Ollama: {e}") # Log the actual error for debugging
            return "Error: Could not get response from the LLM."

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Returns the current conversation history.
        """
        return self.conversation_history

    def clear_conversation_history(self):
        """
        Clears the conversation history, resetting it to only the initial system prompt.
        """
        self.conversation_history = []
        self._initialize_system_prompt()