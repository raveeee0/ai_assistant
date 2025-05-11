from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from lang import summary_email, process_email, EmailState
from services.gmail_service import (
    authenticate,
    get_unread_messages,
    parse_message,
    send_reply_email,
    mark_as_read,
    get_message_by_rfc822_message_id
)
from googleapiclient.discovery import build
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from googleapiclient.discovery import build
import base64

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class IdRequest(BaseModel):
    original_id: str

class EmailReplyRequest(BaseModel):
    to: str
    subject: str
    message: str
    thread_id: str
    original_message_id: str


def get_message_by_rfc822_message_id(service, rfc822_id):
    query = f'rfc822msgid:{rfc822_id}'
    response = service.users().messages().list(userId='me', q=query).execute()
    messages = response.get('messages', [])

    if not messages:
        return None

    message_id = messages[0]['id']
    return service.users().messages().get(userId='me', id=message_id, format='full').execute()

def parse_message(message):
    headers = message['payload']['headers']
    payload = message['payload']

    def get_header(name):
        return next((h['value'] for h in headers if h['name'].lower() == name.lower()), None)

    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    else:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

    return {
        "from": get_header("From"),
        "to": get_header("To"),
        "subject": get_header("Subject"),
        "date": get_header("Date"),
        "body": body.strip()
    }


@app.websocket("/summary/{mail_id}/ws")
async def websocket_summary(websocket: WebSocket, mail_id: str):
    await websocket.accept()

    try:
        creds = authenticate()
        service = build('gmail', 'v1', credentials=creds)

        # Usa lo stesso metodo che già utilizzi
        raw_msg = get_message_by_rfc822_message_id(service, mail_id)
        if raw_msg is None:
            await websocket.send_text("❌ Message not found")
            return

        parsed = parse_message(raw_msg)

        # Crea il testo completo
        full_text = f"""Subject: {parsed['subject']}
                        From: {parsed['from']}
                        To: {parsed['to']}
                        Date: {parsed['date']}
                        
                        {parsed['body']}"""

        stream = summary_email(full_text)

        for chunk in stream:
            await websocket.send_text(chunk)
            await asyncio.sleep(0.5)

    except Exception as e:
        # check if the socket is still open before sending a message
        if websocket.client_state == WebSocket.OPEN:
            await websocket.send_text(f"❌ Error: {str(e)}")
    finally:
        await websocket.close()


@app.websocket("/draft/{mail_id}/ws")
async def websocket_draft(websocket: WebSocket, mail_id: str):
    await websocket.accept()

    try:
        creds = authenticate()
        service = build('gmail', 'v1', credentials=creds)

        # Recupera la mail reale
        raw_msg = get_message_by_rfc822_message_id(service, mail_id)
        if raw_msg is None:
            await websocket.send_text("❌ Message not found")
            return

        parsed = parse_message(raw_msg)

        state = EmailState(
            subject=parsed["subject"],
            username=parsed["from"].split(" ")[0] if " " in parsed["from"] else parsed["from"],
            email_content=parsed["body"],
            destination_email=parsed["from"],
            is_reply=False
        )
        stream = process_email(state)

        for chunk in stream:
            await websocket.send_text(chunk)
            await asyncio.sleep(0.5)

    except Exception as e:
        # check if the socket is still open before sending a message
        if websocket.client_state == WebSocket.OPEN:
            await websocket.send_text(f"❌ Error: {str(e)}")

    finally:
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



@app.post("/get_from_id")
def get_from_id(request: IdRequest):
    try:
        creds = authenticate()
        service = build('gmail', 'v1', credentials=creds)

        raw_msg = get_message_by_rfc822_message_id(service, request.original_id)
        if raw_msg is None:
            return JSONResponse(content={"error": "Message not found"}, status_code=404)

        parsed = parse_message(raw_msg)
        return {"status": "success", "message": parsed}

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
