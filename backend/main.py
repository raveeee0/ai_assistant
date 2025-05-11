from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from services.gmail_service import (
    authenticate,
    get_unread_messages,
    parse_message,
    send_reply_email,
    mark_as_read
)
from googleapiclient.discovery import build
import asyncio

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class EmailReplyRequest(BaseModel):
    to: str
    subject: str
    message: str
    thread_id: str
    original_message_id: str



@app.websocket("/summary/{summary_id}/ws")
async def websocket_endpoint(websocket: WebSocket, summary_id: str):
    await websocket.accept()

    # Create the summary and send it by chunk each 0.5 seconds
    for i in range(5):
        await asyncio.sleep(0.5)
        await websocket.send_text(f"Message {i + 1} for summary {summary_id}")
    
    await websocket.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Gmail API FastAPI!"}

@app.get("/unread-mails")
def read_unread_emails():
    try:
        creds = authenticate()
        service = build('gmail', 'v1', credentials=creds)

        messages = get_unread_messages(service)
        if not messages:
            return {"count": 0, "messages": []}

        parsed_messages = [parse_message(service, msg['id']) for msg in messages]
        return {"count": len(parsed_messages), "messages": parsed_messages}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/reply-mail")
def reply_to_email(request: EmailReplyRequest):
    try:
        creds = authenticate()
        service = build('gmail', 'v1', credentials=creds)

        result = send_reply_email(
            service,
            to=request.to,
            subject=request.subject,
            message_text=request.message,
            thread_id=request.thread_id,
            original_message_id=request.original_message_id
        )
        return {"status": "success", "message_id": result["id"]}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/mark-as-read")
def mark_as_read(message_id: str):
    try:
        creds = authenticate()
        service = build('gmail', 'v1', credentials=creds)
        result = mark_as_read(service, message_id)
        return {"status": "success", "result": result["id"]}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
