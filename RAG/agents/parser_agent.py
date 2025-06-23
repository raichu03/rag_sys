from bs4 import BeautifulSoup
from typing import Dict, Any

class ParserAgent:
    """
    The Parser Agent is responsible for extracting meaningful text and metadata
    from the raw content obtained by the Crawler Agent.
    It can handle various formats (HTML, PDF, plain text, etc.).
    """

    def parse(self, raw_content: str, content_type: str = "text/html") -> Dict[str, Any]:
        """
        Parses the raw content based on its type and extracts structured data.
        This example primarily focuses on HTML parsing using BeautifulSoup.
        For other types (PDF, DOCX), you'd integrate libraries like `PyPDF2`, `python-docx`, etc.

        Args:
            raw_content (str): The raw content string from the crawler.
            content_type (str): The MIME type of the content (e.g., "text/html", "application/pdf").

        Returns:
            Dict[str, Any]: A dictionary containing extracted text and metadata.
                            Returns an empty dict if parsing fails or content is empty.
        """
        if not raw_content:
            return {}

        parsed_data = {"text": "", "metadata": {}}

        try:
            if content_type == "text/html":
                soup = BeautifulSoup(raw_content, 'html.parser')

                paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                text_content = "\n".join([p.get_text(separator=' ', strip=True) for p in paragraphs])
                parsed_data["text"] = text_content

                title_tag = soup.find('title')
                if title_tag:
                    parsed_data["metadata"]["title"] = title_tag.get_text(strip=True)

                meta_description = soup.find('meta', attrs={'name': 'description'})
                if meta_description and meta_description.get('content'):
                    parsed_data["metadata"]["description"] = meta_description['content'].strip()

            elif content_type == "text/plain":
                parsed_data["text"] = raw_content

            else:
                return {}

        except Exception as e:
            return {}

        return parsed_data