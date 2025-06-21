import requests
import ollama

# --- 3. Interact with Ollama ---
def get_ollama_response(prompt: str) -> str:
    """
    Sends a prompt to the Ollama server and gets a response from the specified model.

    Args:
        prompt (str): The prompt to send to the LLM.
        model (str): The name of the Ollama model to use (default: llama3.2b).

    Returns:
        str: The generated response from the LLM, or an error message if something goes wrong.
    """
    try:

        # Use the chat API for a more conversational style, even for simple prompts
        response = ollama.chat(
            model="llama3.2b",
            messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ],
            options={
                'temperature': 0.1, # Lower temperature for more factual, less creative answers
            }
        )
        return response['message']['content'].strip()
    except ollama.ResponseError as e:
        return f"Error from Ollama: {e}. Please ensure Ollama server is running and 'ollama3.2b' model is pulled."
    except requests.exceptions.ConnectionError as e:
        return f"Could not connect to Ollama server. Error: {e}. Please ensure Ollama server is running."
    except Exception as e:
        return f"An unexpected error occur"
    
