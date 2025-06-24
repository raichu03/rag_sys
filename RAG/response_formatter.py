from typing import Dict, Any

class ResponseFormatter:
    """
    The Response Formatter takes the final generated response and any associated
    metadata (like sources) and formats it into a user-friendly output.
    This could involve adding markdown, links, or structuring the output.
    """

    def format(self, rag_response: Dict[str, Any]) -> str:
        """
        Formats the final response for the end-user.

        Args:
            rag_response (Dict[str, Any]): A dictionary containing the 'response_text'
                                           and a list of 'sources'.

        Returns:
            str: The beautifully formatted response string.
        """
        response_text = rag_response.get("response_text", "An unexpected error occurred and no response was generated.")
        sources = rag_response.get("sources", [])

        formatted_output = f"{response_text}\n\n"

        if sources:
            formatted_output += "--- Sources ---\n"
            seen_document_ids = set()
            unique_sources = []
            for source in sources:
                doc_id = source.get("document_id", "Unknown Document")
                if doc_id not in seen_document_ids:
                    unique_sources.append(source)
                    seen_document_ids.add(doc_id)

            for i, source in enumerate(unique_sources):
                doc_id = source.get("document_id", "Unknown Document")
                page_info = f" (Page: {source['page']})" if source.get("page") else ""
                snippet = source.get("text_snippet", "")
                formatted_output += f"{i+1}. Document: {doc_id}{page_info}\n"
                if snippet:
                    formatted_output += f"   Snippet: '{snippet}'\n"

        return formatted_output