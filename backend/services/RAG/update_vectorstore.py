import os
import json
from datetime import datetime
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

CONVERSATION_DIR = "../../conversations"
VECTORSTORE_DIR = "faiss_index"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

def get_today_filename():
    today = datetime.today().strftime("%Y-%m-%d")
    return os.path.join(CONVERSATION_DIR, f"conversations_{today}.json")

def update_vectorstore_from_today():
    json_path = get_today_filename()
    if not os.path.exists(json_path):
        print("❌ Nessun file JSON per oggi.")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    all_texts = []
    for thread_id, thread in data.items():
        conversation = f"Subject: {thread['subject']}\n\n"
        for msg in thread["messages"]:
            conversation += f"{msg['from']} ({msg['email']}) on {msg['date']}:\n{msg['text']}\n\n"
        all_texts.append(conversation)
    print(all_texts)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = splitter.create_documents(all_texts)


    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    if not docs:
        print("❌ Nessun documento da aggiungere.")
        return

    if os.path.exists(VECTORSTORE_DIR):
        db = FAISS.load_local(VECTORSTORE_DIR, embeddings=embeddings, allow_dangerous_deserialization=True)

    else:
        db = FAISS.from_documents(docs, embeddings)

    if os.path.exists(VECTORSTORE_DIR):
        db.add_documents(docs)

    db.save_local(VECTORSTORE_DIR)
    print("✅ Vettoriale aggiornato con le conversazioni del giorno.")


if __name__ == "__main__":
    update_vectorstore_from_today()
