# Multi-Agent RAG

Multi-Agent RAG is a system that allows multiple agents to collaborate on a task useing a shared knowledge base. It is designed to be modular and extensible, allowing for easy integration of new agents and knowledge sources.This system allows the user to input the url of a knowledge base, which is then used to create a shared knowledge base for the agents. The agents can then query this knowledge base to answer questions and perform tasks.

## Features
- Modular and extensible architecture
- Multiple agents can collaborate on a task
- Shared knowledge base
- Agents can query the knowledge base to answer questions and perform tasks

## Installation
This system uses python 3.10 or higher. Create a virtual environment and install the requirements.

1. Clone the repository:
   ```bash
   git clone https://github.com/raichu03/rag_sys.git
   ```
2. Download and install [Ollama](https://ollama.com/download):
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
   ```
3. Install the required Ollama models:
   ```bash
   ollama pull llama3.2
   ```
4. Navigate to the project directory and install the requirements:
   ```bash
   cd multi-agent-rag
   pip install -r requirements.txt
   ```
5. Navigate to the `RAG` directoru and run the following command to start the RAG server:
   ```bash
   cd RAG
   uvicorn main:app
   ```
Click on the link in the terminal to open the RAG server in your browser.

## Usage
1. Open the RAG server in your browser.
2. Input the URL of the knowledge base you want to use.
3. Send the message to the agents.
4. The agents will collaborate to answer your question using the shared knowledge base.

