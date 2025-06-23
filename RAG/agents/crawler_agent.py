import httpx

class CrawlerAgent:
    """
    The Crawler Agent is responsible for fetching raw content from various sources,
    such as web pages, files, or APIs.
    """
    async def crawl(self, source_url: str) -> str:
        """
        Fetches the raw content from a given URL.
        This is a simplified example; a real crawler would handle
        various content types, error handling, politeness, etc.

        Args:
            source_url (str): The URL or path to the document source.

        Returns:
            str: The raw content as a string, or an empty string if failed.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(source_url, timeout=10)
                response.raise_for_status()
                content = response.text
                return content
        except httpx.RequestError as e:
            return ""
        except Exception as e:
            return ""