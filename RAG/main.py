from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from typing import List, Dict

from urls import extract_urls_from_text
from orchestration_layer import OrchestrationLayer

app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="templates"), name="static")

class ConnectionManager:
    """Manages active WebSocket connections."""
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accepts a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New connection accepted. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Disconnects a WebSocket."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"A client has disconnected. Total clients: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Sends a JSON message to a specific client."""
        try:
            await websocket.send_json(dict(message))
        except Exception as e:
            print(f"Could not send message to a client: {e}")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(
        name="index.html",
        context=context
    )

manager = ConnectionManager()

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles the WebSocket connection lifecycle and message processing.
    
    This revised structure uses a `try...finally` block to guarantee that the
    `manager.disconnect()` cleanup logic is always executed, whether the client
    disconnects gracefully, an error occurs, or the server is shut down.
    """
    await manager.connect(websocket)
    orchestrator = OrchestrationLayer()
    
    try:
        while True:
            try:
                user_query = await websocket.receive_json()

                query_text = user_query.get('query')
                if not query_text:
                    await manager.send_personal_message({"message": "Invalid request: 'query' field is missing."}, websocket)
                    continue

                urls, query = extract_urls_from_text(query_text)

                if not urls:
                    await manager.send_personal_message({"message": "You did not provide any URLs in your query. Please provide at least one URL for ingestion."}, websocket)
                    continue

                ingestion_success = await orchestrator.ingest_document_workflow(urls[0], "user_docs")
                
                if not ingestion_success:
                    await manager.send_personal_message({"message": f"Could not get data from the provided URL: {urls[0]}. Please check the URL and try again."}, websocket)
                    continue

                response_data = await orchestrator.handle_query_workflow(query)
                
                if response_data and response_data.get('response'):
                    await manager.send_personal_message({"message": response_data['response']}, websocket)
                else:
                    await manager.send_personal_message({"message": "I couldn't generate a response for your query. Please try rephrasing."}, websocket)

            except WebSocketDisconnect:
                print("Client disconnected gracefully.")
                break

            except Exception as e:
                print(f"An unexpected error occurred during message processing: {e}")
                await manager.send_personal_message({"message": "An internal server error occurred while processing your request."}, websocket)

    except Exception as e:
        print(f"A critical WebSocket error occurred: {e}")
    
    finally:
        manager.disconnect(websocket)