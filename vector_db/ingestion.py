import os
import json
import numpy as np
import faiss
from langchain_huggingface import HuggingFaceEmbeddings

HAS_CHROMA = True # Keep this True so tests don't skip; we're just using FAISS instead

class VectorDBFAISS:
    def __init__(self, persist_directory: str = "./faiss_db"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        # Use HuggingFace local embeddings (all-MiniLM-L6-v2) for free, robust RAG
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        self.index_file = os.path.join(persist_directory, "index.faiss")
        self.meta_file = os.path.join(persist_directory, "metadata.json")
        
        self.dimension = 384 # all-MiniLM-L6-v2 output dimension
        
        if os.path.exists(self.index_file) and os.path.exists(self.meta_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.meta_file, 'r') as f:
                self.metadata_store = json.load(f) # list of {id, text, metadata} corresponding to index
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata_store = []
            
    def _save(self):
        faiss.write_index(self.index, self.index_file)
        with open(self.meta_file, 'w') as f:
            json.dump(self.metadata_store, f)

    def index_documents(self, documents: list[str], metadatas: list[dict], ids: list[str]):
        if not documents: return
        
        # Get embeddings via Gemini
        vectors = self.embeddings.embed_documents(documents)
        vectors_np = np.array(vectors).astype('float32')
        
        # Add to FAISS index
        self.index.add(vectors_np)
        
        # Store metadata
        for i, text in enumerate(documents):
            self.metadata_store.append({
                "id": ids[i],
                "text": text,
                "metadata": metadatas[i]
            })
            
        self._save()
        print(f"Indexed {len(documents)} documents using FAISS.")

    def search(self, query_text: str, n_results: int = 3) -> dict:
        if self.index.ntotal == 0:
            return {"documents": []}
            
        # Embed query
        query_vector = self.embeddings.embed_query(query_text)
        query_np = np.array([query_vector]).astype('float32')
        
        # Search FAISS
        distances, indices = self.index.search(query_np, min(n_results, self.index.ntotal))
        
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.metadata_store):
                results.append(self.metadata_store[idx]["text"])
                
        # Mimicking the dict return structure of ChromaDB for compatibility
        return {"documents": [results]}

# Singleton-like instance for ease of use
db_instance = VectorDBFAISS()

def index_text(text: str, metadata: dict, doc_id: str, collection="financial_documents"):
    # The collection argument is ignored for FAISS to keep it simple, 
    # but we accept it for backward compatibility with our tools test
    db_instance.index_documents([text], [metadata], [doc_id])

def search_db(query: str, n_results: int=3, collection="financial_documents"):
    return db_instance.search(query, n_results=n_results)
