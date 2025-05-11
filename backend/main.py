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
    allow_origins=["*"],  # Allows your frontend origin
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



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async def sender():
        while True:
            await asyncio.sleep(5)
            await websocket.send_text("⏱️ Messaggio automatico dal server")

    async def receiver():
        while True:
            try:
                data = await websocket.receive_text()
                print("Ricevuto:", data)
                await websocket.send_text(f"✅ Ricevuto: {data}")
            except Exception as e:
                print("❌ Connessione chiusa:", e)
                break

    # Avvia entrambi in parallelo
    send_task = asyncio.create_task(sender())
    recv_task = asyncio.create_task(receiver())

    # Aspetta che uno dei due finisca (es. client disconnesso)
    done, pending = await asyncio.wait(
        [send_task, recv_task],
        return_when=asyncio.FIRST_COMPLETED
    )

    # Cancella il task rimasto in attesa
    for task in pending:
        task.cancel()

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
