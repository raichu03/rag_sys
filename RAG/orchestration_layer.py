import asyncio
from typing import Dict, Any, List

from agents import CrawlerAgent
from agents import ParserAgent
from agents import ChunkingEmbeddingAgent
from agents import QueryAgent
from agents import RAGAgent
from agents import ValidationQAAgent

from vector_database_connector import VectorDatabaseConnector # Connector class
from response_formatter import ResponseFormatter

class OrchestrationLayer:
    """
    The Orchestration Layer coordinates the workflow between different agents
    and manages communication within the Multi-Agent RAG system.
    """
    def __init__(self):
        self.crawler_agent = CrawlerAgent()
        self.parser_agent = ParserAgent()
        self.chunking_embedding_agent = ChunkingEmbeddingAgent()
        self.vector_db_connector = VectorDatabaseConnector()
        self.query_agent = QueryAgent()
        self.rag_agent = RAGAgent()
        self.validation_qa_agent = ValidationQAAgent()
        self.response_formatter = ResponseFormatter()

    async def ingest_document_workflow(self, document_source: str, document_id: str) -> bool:
        """
        Manages the workflow for ingesting a new document into the RAG system.
        This involves crawling, parsing, chunking, embedding, and storing.

        Args:
            document_source (str): The source or URL of the document to ingest.
            document_id (str): A unique ID for the document.

        Returns:
            bool: True if ingestion was successful, False otherwise.
        """
        try:
            raw_content = await self.crawler_agent.crawl(document_source)
            if not raw_content:
                return False

            parsed_data = self.parser_agent.parse(raw_content)
            if not parsed_data:
                return False

            chunks_with_embeddings = self.chunking_embedding_agent.process(parsed_data)
            if not chunks_with_embeddings:
                return False

            success = self.vector_db_connector.add_documents(document_id, chunks_with_embeddings)
            if not success:
                return False

            return True

        except Exception as e:
            return False

    async def handle_query_workflow(self, user_query: str) -> Dict[str, Any]:
        """
        Manages the workflow for handling a user query.
        This involves querying, RAG processing, validation, and response formatting.

        Args:
            user_query (str): The query from the user.

        Returns:
            Dict[str, Any]: A dictionary containing the final response and metadata.
        """
        try:
            processed_query = await self.query_agent.process_query(user_query)
            if not processed_query:
                return {"response": "Could not process your query.", "status": "failed"}

            retrieved_chunks = self.vector_db_connector.search(processed_query.get("enhanced_query", user_query), top_k=5)
            if not retrieved_chunks:
                return {"response": "I couldn't find any relevant information for your query.", "status": "no_results"}

            rag_response = self.rag_agent.generate_response(user_query, retrieved_chunks)
            if not rag_response:
                return {"response": "An error occurred while generating the response.", "status": "failed"}

            validation_result = await self.validation_qa_agent.validate(rag_response, user_query, retrieved_chunks)
            if not validation_result.get("is_valid"):
                return {"response": f"Response validation failed. Reason: {validation_result.get('reason', 'Unknown')}. Please rephrase your query.", "status": "validation_failed"}

            final_response = self.response_formatter.format(rag_response)
            return {"response": final_response, "status": "success", "source_chunks": retrieved_chunks}

        except Exception as e:
            return {"response": f"An unexpected error occurred: {e}", "status": "error"}