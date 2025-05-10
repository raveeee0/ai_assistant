import json
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import TextLoader, JSONLoader, PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

# === CONFIG ===
DATA_PATHS = {
    "mock_data.json": "json",
    "company_policies.pdf": "pdf",
    "product_info.txt": "txt",
    "daily_reports_01052025.csv": "csv",
    # Aggiungi qui altri file e i loro tipi
}
INDEX_PATH = "faiss_index"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Definisci lo splitter di testo con separatori personalizzati, dando priorità al doppio newline
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=50,
    chunk_overlap=10,
    separators=["\n\n", "\n", " ", "",] # Dai priorità al doppio newline
)

def load_and_process(file_path, file_type):
    documents = []
    if file_type == "json":
        loader = JSONLoader(
            file_path=file_path,
            jq_schema='.[]',
            text_content=False
        )
        docs = loader.load()
        for doc in docs:
            # Assumendo che 'message' e 'response' siano dentro il contenuto testuale
            try:
                content = json.loads(doc.page_content)
                text = f"{content['message']}\nResponse: {content['response']}"
            except Exception:
                text = doc.page_content  # fallback in caso di errore
            documents.append(Document(page_content=text, metadata={"source": file_path, **doc.metadata}))
    elif file_type == "txt":
        loader = TextLoader(file_path)
        documents = loader.load()
        for doc in documents:
            doc.metadata["source"] = file_path
    elif file_type == "pdf":
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        for doc in documents:
            doc.metadata["source"] = file_path
    elif file_type == "csv":
        loader = CSVLoader(file_path)
        documents = loader.load()
        for doc in documents:
            doc.metadata["source"] = file_path
    return documents


    # Applica lo splitter di testo ai documenti caricati
    documents = []
    for doc in raw_documents:
        split_docs = text_splitter.split_documents([doc])
        documents.extend(split_docs)
    return documents

if __name__ == "__main__":
    all_documents = []
    for path, file_type in DATA_PATHS.items():
        print(f"Caricamento e processamento di: {path}")
        docs = load_and_process(path, file_type)
        all_documents.extend(docs)

    print(f"Numero totale di chunks creati: {len(all_documents)}")

    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vectorstore = FAISS.from_documents(all_documents, embedding_model)
    vectorstore.save_local(INDEX_PATH)
    print(f"✅ Indice FAISS iniziale creato (con chunking) e salvato in: {INDEX_PATH}")