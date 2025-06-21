import requests
from bs4 import BeautifulSoup

# --- 1. Fetch Content from URLs ---
def fetch_urls_content(urls: list[str]) -> dict[str, str]:
    """
    Fetches content from a list of URLs and extracts readable text.

    Args:
        urls (list[str]): A list of URLs to fetch.

    Returns:
        dict[str, str]: A dictionary where keys are URLs and values are
                        the extracted text content. Returns an empty string
                        for URLs that fail to fetch or parse.
    """
    all_content = {}
    for url in urls:
        try:
            print(f"Fetching content from: {url}")
            response = requests.get(url, timeout=10) # 10 second timeout
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script, style, and other non-visible elements
            for script_or_style in soup(['script', 'style', 'header', 'footer', 'nav', 'form']):
                script_or_style.decompose()

            text = soup.get_text(separator=' ', strip=True)
            all_content[url] = text
            print(f"Successfully fetched content from {url} (Length: {len(text)} characters)")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            all_content[url] = "" # Store empty string for failed URLs
        except Exception as e:
            print(f"An unexpected error occurred while processing {url}: {e}")
            all_content[url] = ""
    return all_content
