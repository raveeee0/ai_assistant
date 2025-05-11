import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain.document_loaders import JSONLoader, TextLoader, PyPDFLoader, CSVLoader
import os

text_splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=10)

class RAGModule:
    def __init__(self, index_path="../faiss_index", model_name="all-MiniLM-L6-v2"):
        # Embedding + vector store
        self.embedding_model = HuggingFaceEmbeddings(model_name=model_name)
        try:
            self.vectorstore = FAISS.load_local(index_path, self.embedding_model, allow_dangerous_deserialization=True)
        except:
            print("-------------")
            print(index_path)
            raise FileNotFoundError(f"L'indice FAISS non è stato trovato in: {index_path}. Esegui prima 'index_all.py'.")



    def get_similar_cases(self, message, k=5):
        """Ritorna i k documenti più simili dal DB"""
        return self.vectorstore.similarity_search(message, k=k)

    def build_context(self, similar_docs):
        context = ""
        for i, doc in enumerate(similar_docs):
            context += f"\nDocumento {i+1} (Fonte: {doc.metadata.get('source', 'Sconosciuta')}):\n{doc.page_content}\n"


        print(context)
        return context

    def generate_context(self, message):
        similar_docs = self.get_similar_cases(message)
        context = self.build_context(similar_docs)
        return context

    def update_index(self, data_path, file_type="json"):
        """Aggiorna l'indice FAISS con nuovi documenti, applicando il chunking."""
        documents_to_add = self.load_and_process(data_path, file_type)
        self.vectorstore.add_documents(documents_to_add)
        self.vectorstore.save_local("./faiss_index")
        print(f"✅ Indice FAISS aggiornato con chunking da: {data_path}")

    def load_and_process(self, file_path, file_type):
        raw_documents = []
        if file_type == "json":
            loader = JSONLoader(
                file_path=file_path,
                jq_schema='.[]',
                text_content=False
            )
            data = loader.load()
            for item in data:
                text = f"{item['message']}\nResponse: {item['response']}"
                raw_documents.append(Document(page_content=text, metadata={"source": file_path, "id": item.get("id")}))
        elif file_type == "txt":
            loader = TextLoader(file_path)
            raw_documents = loader.load()
            for doc in raw_documents:
                doc.metadata["source"] = file_path
        elif file_type == "pdf":
            loader = PyPDFLoader(file_path)
            raw_documents = loader.load()
            for doc in raw_documents:
                doc.metadata["source"] = file_path
        elif file_type == "csv":
            loader = CSVLoader(file_path)
            raw_documents = loader.load()
            for doc in raw_documents:
                doc.metadata["source"] = file_path

        documents = []
        for doc in raw_documents:
            split_docs = text_splitter.split_documents([doc])
            documents.extend(split_docs)
        return documents



