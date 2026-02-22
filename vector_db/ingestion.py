import os

try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMA = True
except Exception as e:
    print(f"Warning: chromadb could not be imported (likely Python 3.14 compatibility issue): {e}")
    HAS_CHROMA = False

class VectorDB:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.client = None
        if HAS_CHROMA:
            # Ensures directory exists
            os.makedirs(persist_directory, exist_ok=True)
            self.client = chromadb.PersistentClient(path=persist_directory)
    
    def get_or_create_collection(self, collection_name: str="financial_documents"):
        """Gets or creates a collection for document storage."""
        if not HAS_CHROMA:
            return None
        return self.client.get_or_create_collection(name=collection_name)

    def index_documents(self, collection_name: str, documents: list[str], metadatas: list[dict], ids: list[str]):
        """Index a batch of documents."""
        if not HAS_CHROMA:
            return
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Indexed {len(documents)} documents into {collection_name}")

    def search(self, collection_name: str, query_text: str, n_results: int = 3) -> list:
        """Search the vector database."""
        if not HAS_CHROMA:
            return []
        collection = self.get_or_create_collection(collection_name)
        
        # Checking if collection is empty
        if collection.count() == 0:
            return []

        results = collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

# Singleton-like instance for ease of use
db_instance = VectorDB()

def index_text(text: str, metadata: dict, doc_id: str, collection="financial_documents"):
    db_instance.index_documents(collection, [text], [metadata], [doc_id])

def search_db(query: str, n_results: int=3, collection="financial_documents"):
    return db_instance.search(collection, query, n_results)
