from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from typing import List

from urls import extract_urls_from_text
from orchestration_layer import OrchestrationLayer

app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="templates"), name="static")

class ConnectionManager:
    def __init__(self):
        self.active_connection: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connection.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connection.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        for connection in self.active_connection:
            await connection.send_json(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connection:
            await connection.send_json(message)
    

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(
        name="index.html",
        context=context
    )
    
manager = ConnectionManager()

@app.get("/test")
async def test():
    return "helo"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    orchestrator = OrchestrationLayer()
    count = 0
    try:
        while True:
            user_query = await websocket.receive_json()
            urls, query = extract_urls_from_text(user_query['query'])
            print(user_query)
            print(urls)
            print(query)
            if count == 0 and len(urls) == 0:
                message = {"message": "You did not provide any urls"}
                await manager.broadcast(message)
            
            if len(urls) != 0:
                
                ingestion_success = await orchestrator.ingest_document_workflow(urls[0], "user_docs")
            
            if not ingestion_success:
                print("database")
                print(ingestion_success)
                message = {"message": "Could not get the data"}
                await manager.broadcast(message)
            
            count += 1
            
            response = await orchestrator.handle_query_workflow(query)
            message = {"message": response.get('response')}
            await manager.broadcast(message)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client has disconnected.")