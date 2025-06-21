import re

# --- Utility: Extract URLs from Text ---
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
    # Regex to find common URL patterns (http, https, www. and direct domains)
    # This pattern is robust but might miss some edge cases.
    url_pattern = r"(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+(?:/[^\s]*)?)"
    urls = re.findall(url_pattern, text)

    # Remove URLs from the text to get the clean question
    cleaned_text = re.sub(url_pattern, "", text)
    # Remove extra spaces left behind after URL removal
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    return urls, cleaned_text


# --- 2. Process Content: Chunking ---
def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """
    Splits a long string of text into smaller, overlapping chunks.

    Args:
        text (str): The input text to chunk.
        chunk_size (int): The maximum size of each chunk (in characters).
        chunk_overlap (int): The number of characters to overlap between consecutive chunks.

    Returns:
        list[str]: A list of text chunks.
    """
    # Debugging: Print the type and length of 'text' at the start of the function
    print(f"DEBUG: Entering chunk_text. Type of 'text': {type(text)}, Length: {len(text) if isinstance(text, str) else 'N/A'}")

    # Ensure 'text' is indeed a string. If not, this is likely the cause of KeyError.
    if not isinstance(text, str):
        print(f"ERROR: Expected 'text' to be a string, but received type {type(text)}. Returning empty chunks.")
        return []

    if not text: # This handles cases where the string is empty
        return []

    # Use a simpler, character-based chunking for demonstration
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Additional safety check for slicing, though standard Python slicing is robust
        if start > len(text) or end < start:
            print(f"WARNING: Invalid slice indices detected (start={start}, end={end}, text_len={len(text)}). Breaking loop.")
            break

        chunk = text[start:end] # This is the line where the user reported the error
        chunks.append(chunk)
        if end == len(text):
            break
        start += (chunk_size - chunk_overlap) # Move cursor forward, accounting for overlap

    print(f"Text chunked into {len(chunks)} pieces.")
    return chunks