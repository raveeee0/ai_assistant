
import os
from rag_service import RAGModule
from datetime import datetime
#TODO: Test if it works, update with chosen reports?
NEW_EMAILS_PATH = f"new_emails_{datetime.now().strftime('%Y%m%d')}.json" # Esempio di nome file giornaliero

if os.path.exists(NEW_EMAILS_PATH):
    rag = RAGModule(index_path="../faiss_index", api_key="YOUR_API_KEY") # Sostituisci con la tua API key
    rag.update_index(NEW_EMAILS_PATH, file_type="json")
    print(f"Aggiornamento dell'indice completato con le nuove email da: {NEW_EMAILS_PATH}")
else:
    print(f"Nessun nuovo file di email trovato per oggi: {NEW_EMAILS_PATH}")