import json
from typing import Union
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from chat import Chat
import uvicorn
from pathlib import Path

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


chatService = Chat()
class Query(BaseModel):
    text: str
    fileName: str

@app.post("/index_document")
async def upload_document(file: UploadFile = File(...)):
    return chatService.index_document(file)

@app.post("/index_youtubelink")
def index_youtubelink(
    link:str
):
    return chatService.youtube_link(link)

@app.post("/Query")
def get_answer(query:Query):
    return chatService.getQueryResponse(query)

@app.get("/get_file_name")
def get_file_name():
    return chatService.getFileName()

@app.get("/{fileName}/summary/")
def get_summary(fileName: str):
    return chatService.getSummary(fileName)

@app.delete("/remove_item/{fileName}")
def remove_item(fileName: str):
    return chatService.remove_item(fileName)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)