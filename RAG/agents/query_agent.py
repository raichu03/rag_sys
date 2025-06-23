import ollama
from pydantic import BaseModel, Field, ValidationError
from typing import List, Dict, Any
import json

class ExpandedQueryResponse(BaseModel):
    expanded_terms: List[str] = Field(
        ..., description="A list of 3-5 alternative phrasings, synonyms, and related keywords for the user's query."
    )

class QueryAgent:
    """
    The Query Agent is responsible for processing the user's raw query.
    It uses the Ollama Llama3.2 model for structured query expansion.
    """
    def __init__(self, model_name: str = "llama3.2", temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature

    async def _call_ollama_llama3_structured(self, prompt_message: str) -> List[str]:
        """
        Makes an asynchronous call to the Ollama Llama3 model for structured text generation.
        """
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt_message}],
                format='json',  # Request JSON-structured output
                options={'temperature': self.temperature}
            )

            # Extract and parse the JSON response
            if response and 'message' in response and 'content' in response['message']:
                raw_json_content = response['message']['content']

                try:
                    parsed_response = ExpandedQueryResponse.model_validate_json(raw_json_content)
                    return [term.strip() for term in parsed_response.expanded_terms if term.strip()]
                except ValidationError as e:
                    return []
                except json.JSONDecodeError as e:
                    return []
            else:
                return []

        except Exception as e:
            return []

    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Processes the raw user query, expanding it using Llama3 for better retrieval.
        """

        cleaned_query = user_query.strip().lower()

        prompt = (
            f"You are an expert query expansion tool. Your task is to generate 3 to 5 "
            f"highly relevant alternative phrasings, exact synonyms, and related keywords "
            f"for a given user query. These expanded terms should help in finding more "
            f"information in a document database. "
            f"Do NOT include the original query in the output. "
            f"The output MUST be a JSON object with a single key 'expanded_terms', "
            f"whose value is a JSON array (list) of strings. Each string in the list "
            f"should be a distinct expanded term. "
            f"Do not add any conversational text, explanations, or extraneous characters outside the JSON."
            f"\n\n"
            f"User Query: '{cleaned_query}'\n\n"
            f"Example for 'capital of france': {{ \"expanded_terms\": [\"paris\", \"french capital city\", \"city of light\", \"france's main city\"] }}\n\n"
            f"Your output JSON:"
        )

        expanded_terms_list = await self._call_ollama_llama3_structured(prompt)
        enhanced_query_text = cleaned_query

        if expanded_terms_list:
            all_terms = set([cleaned_query] + expanded_terms_list)
            enhanced_query_text = ", ".join(sorted(list(all_terms)))

        processed_info = {
            "original_query": user_query,
            "cleaned_query": cleaned_query,
            "enhanced_query": enhanced_query_text,
            "detected_intent": "general_qa"  # Placeholder for more advanced intent detection
        }
        return processed_info