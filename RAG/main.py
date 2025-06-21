from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

templates = Jinja2Templates(directory='templates')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],       # List of allowed origins
    allow_credentials=True,      # Allow cookies and authorization headers to be sent
    allow_methods=["*"],         # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],         # Allow all headers
)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(
        name="index.html",
        context=context
)

class InitialQuery(BaseModel):
    query: str

@app.post("/initial", response_class=JSONResponse)
async def knowledge(message: InitialQuery):
    print("success")
    print("message: ", message.query)
        