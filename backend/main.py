from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from lang import summary_email
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

@app.websocket("/summary/{mail_id}/ws")
async def websocket_endpoint(websocket: WebSocket, mail_id: str):
    await websocket.accept()

    # Create the summary and send it by chunk each 0.5 seconds
    stream = summary_email("""**Subject: Inquiry: Partnership Opportunity for [Your Company Name]**

**From: Alex Chen <alex.chen@examplecompany.com>**
**To: Sarah Miller <sarah.miller@partnersolutions.com>**
**Date: Monday, May 12, 2025, 10:00 AM CEST**

Hi Sarah,

I hope this email finds you well.

My name is Alex Chen, and I am the Business Development Manager at Example Company. We specialize in cloud-based software solutions for data analytics and visualization.

I've been following the work of Partner Solutions for some time, particularly your innovative approach to AI-driven marketing strategies. Your recent case study on enhancing customer engagement for e-commerce businesses truly impressed us.

At Example Company, we believe there's a significant synergy between our data analytics platform and your AI marketing expertise. We envision a potential partnership where our clients could leverage your marketing insights, and vice-versa, creating a more comprehensive solution for businesses looking to optimize their operations and outreach.

Would you be open to a brief 20-minute introductory call sometime next week to explore how our companies might collaborate? I'm available on Wednesday, May 21st, or Thursday, May 22nd, in the afternoon.

Please let me know if either of those times works for you, or if you have another preferred time.

Thank you for your time and consideration.

Best regards,

Alex Chen
Business Development Manager
Example Company
www.examplecompany.com
+39 02 1234 5678
                           
**Subject: Re: Inquiry: Partnership Opportunity for [Your Company Name]**

**From: Sarah Miller <sarah.miller@partnersolutions.com>**
**To: Alex Chen <alex.chen@examplecompany.com>**
**Date: Monday, May 12, 2025, 02:30 PM CEST**

Hi Alex,

Thank you for reaching out! It's great to hear from you.

I appreciate your kind words about our work; we're very proud of our recent e-commerce successes. I agree that a collaboration between our companies could indeed be mutually beneficial, especially given the increasing demand for data-driven marketing solutions.

I'd be happy to schedule an introductory call. Wednesday, May 21st, at 3:00 PM CEST works well for me.

Please send a calendar invite with the meeting link.

Looking forward to speaking with you.

Best,

Sarah Miller
Head of Partnerships
Partner Solutions
www.partnersolutions.com
+39 02 9876 5432""")

    for chunk in stream:
        await websocket.send_text(chunk)
        await asyncio.sleep(0.2)  # Simulate processing time
    
    await websocket.close()

@app.websocket("/draft/{mail_id}/ws")
async def websocket_endpoint(websocket: WebSocket, mail_id: str):
    await websocket.accept()

    # Create the summary and send it by chunk each 0.5 seconds
    for i in range(5):
        await asyncio.sleep(0.5)
        await websocket.send_text(f"Message {i + 1} for mail {mail_id}")
    
    await websocket.close()

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
