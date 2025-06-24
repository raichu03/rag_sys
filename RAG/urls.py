import re

def extract_urls_from_text(text: str) -> tuple[list[str], str]:
    """
    Extracts URLs from a given text string and returns them as a list,
    along with the text content with URLs removed.

    Args:
        text (str): The input text string, potentially containing URLs.

    Returns:
        tuple[list[str], str]: A tuple containing:
                               - A list of extracted URLs.
                               - The original text with all identified URLs removed.
    """
    url_pattern = r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+(?:/[^\s]*)?)"
    urls = re.findall(url_pattern, text)

    cleaned_text = re.sub(url_pattern, "", text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    return urls, cleaned_text