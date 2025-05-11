import json
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import TextLoader, JSONLoader, PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import re
import nltk
from nltk.tokenize import sent_tokenize

# Scarica il tokenizer per le frasi
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# === CONFIG ===
DATA_PATHS = {
    "../data/kb.txt": "txt",
    "../data/company_policies.pdf": "pdf",
    "../data/product_info.txt": "txt",
    "../data/daily_reports_01052025.csv": "csv",
    # Aggiungi qui altri file e i loro tipi
}
INDEX_PATH = "faiss_index"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000  # Dimensione dei chunk
CHUNK_OVERLAP = 200  # Sovrapposizione tra i chunk


# Classe per il chunking semantico
class SemanticChunker:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text, metadata=None):
        """
        Divide il testo in chunk semantici, rispettando i confini di frase
        e mantenendo il contesto.
        """
        # Normalizza gli spazi e i newline
        text = re.sub(r'\s+', ' ', text).strip()

        # Tokenizza in frasi
        sentences = sent_tokenize(text)

        chunks = []
        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_len = len(sentence)

            # Se la frase è troppo lunga, dividiamola ulteriormente
            if sentence_len > self.chunk_size:
                if current_chunk:
                    # Salva il chunk corrente prima di processare la frase lunga
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_size = 0

                # Divide la frase lunga in parti più piccole
                words = sentence.split()
                temp_chunk = []
                temp_size = 0

                for word in words:
                    if temp_size + len(word) + 1 <= self.chunk_size:
                        temp_chunk.append(word)
                        temp_size += len(word) + 1
                    else:
                        chunks.append(" ".join(temp_chunk))
                        temp_chunk = [word]
                        temp_size = len(word)

                if temp_chunk:
                    current_chunk = temp_chunk
                    current_size = temp_size

            # Gestione normale per frasi di lunghezza standard
            elif current_size + sentence_len + 1 <= self.chunk_size:
                current_chunk.append(sentence)
                current_size += sentence_len + 1
            else:
                # Il chunk corrente è pieno, salvalo e iniziane uno nuovo
                chunks.append(" ".join(current_chunk))

                # Inizia un nuovo chunk con sovrapposizione
                overlap_size = 0
                overlap_chunk = []

                # Calcola quante frasi includere nella sovrapposizione
                for i in range(len(current_chunk) - 1, -1, -1):
                    if overlap_size + len(current_chunk[i]) <= self.chunk_overlap:
                        overlap_chunk.insert(0, current_chunk[i])
                        overlap_size += len(current_chunk[i]) + 1
                    else:
                        break

                current_chunk = overlap_chunk + [sentence]
                current_size = sum(len(s) for s in current_chunk) + len(current_chunk)

        # Aggiungi l'ultimo chunk se non è vuoto
        if current_chunk:
            chunks.append(" ".join(current_chunk))

        # Converti in oggetti Document
        documents = []
        for i, chunk in enumerate(chunks):
            doc_metadata = metadata.copy() if metadata else {}
            doc_metadata["chunk"] = i
            documents.append(Document(page_content=chunk, metadata=doc_metadata))

        return documents


def load_and_process(file_path, file_type):
    """
    Carica documenti dal percorso specificato e applica il chunking semantico.
    """
    print(f"Elaborazione di: {file_path}")
    chunker = SemanticChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    documents = []

    try:
        if file_type == "txt":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                metadata = {"source": file_path, "type": "txt"}
                documents.extend(chunker.split_text(text, metadata))

        elif file_type == "pdf":
            loader = PyPDFLoader(file_path)
            pdf_docs = loader.load()

            # Processa ogni pagina separatamente
            for doc in pdf_docs:
                page_text = doc.page_content
                page_num = doc.metadata.get("page", 0)
                metadata = {"source": file_path, "type": "pdf", "page": page_num}
                documents.extend(chunker.split_text(page_text, metadata))

        elif file_type == "csv":
            loader = CSVLoader(file_path)
            csv_docs = loader.load()

            # Combina righe simili per context
            current_text = ""
            current_metadata = {"source": file_path, "type": "csv"}

            for i, doc in enumerate(csv_docs):
                row_text = doc.page_content

                # Aggiungi la riga corrente
                if len(current_text) + len(row_text) <= CHUNK_SIZE:
                    current_text += row_text + "\n"
                else:
                    # Chunking del testo accumulato
                    documents.extend(chunker.split_text(current_text, current_metadata))
                    current_text = row_text + "\n"

            # Aggiungi l'ultimo chunk
            if current_text:
                documents.extend(chunker.split_text(current_text, current_metadata))

        elif file_type == "json":
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            # Gestione ricorsiva per JSON annidati
            def process_json_item(item, path=""):
                if isinstance(item, dict):
                    for key, value in item.items():
                        current_path = f"{path}.{key}" if path else key
                        if isinstance(value, (dict, list)):
                            process_json_item(value, current_path)
                        elif isinstance(value, str) and len(value) > 20:  # Processa solo stringhe significative
                            metadata = {"source": file_path, "type": "json", "path": current_path}
                            documents.extend(chunker.split_text(value, metadata))
                elif isinstance(item, list):
                    for i, subitem in enumerate(item):
                        current_path = f"{path}[{i}]"
                        process_json_item(subitem, current_path)

            process_json_item(json_data)

        print(f"Creati {len(documents)} chunk da {file_path}")
        return documents

    except Exception as e:
        print(f"Errore nell'elaborazione di {file_path}: {str(e)}")
        return []


if __name__ == "__main__":
    all_documents = []
    for path, file_type in DATA_PATHS.items():
        try:
            docs = load_and_process(path, file_type)
            all_documents.extend(docs)
        except Exception as e:
            print(f"Errore nel processare {path}: {str(e)}")

    print(f"Numero totale di chunks creati: {len(all_documents)}")

    # Creazione dell'indice
    if all_documents:
        embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        vectorstore = FAISS.from_documents(all_documents, embedding_model)
        vectorstore.save_local(INDEX_PATH)
        print(f"✅ Indice FAISS creato e salvato in: {INDEX_PATH}")
    else:
        print("⚠️ Nessun documento elaborato, indice non creato.")