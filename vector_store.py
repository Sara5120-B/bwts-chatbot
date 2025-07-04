import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import uuid

class VectorStore:
    def __init__(self, persist_directory: str = "./vectordb"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = self.client.get_or_create_collection(
            name="bwts_documents",
            metadata={"description": "BWTS technical documents"}
        )

    def add_documents(self, chunks: List[Dict]):
        if not chunks:
            return

        documents = [chunk['content'] for chunk in chunks]
        metadatas = [{
            'source': chunk['source'],
            'page': chunk['page'],
            'doc_type': chunk['doc_type']
        } for chunk in chunks]

        # Use UUIDs for unique IDs
        ids = [str(uuid.uuid4()) for _ in chunks]

        embeddings = self.embedding_model.encode(documents).tolist()

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )

    def search(self, query: str, n_results: int = 5, doc_type: str = None) -> List[Dict]:
        query_embedding = self.embedding_model.encode([query]).tolist()[0]

        where_clause = None
        if doc_type and doc_type != 'all':
            where_clause = {"doc_type": doc_type}

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause
        )

        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })

        return formatted_results

    def get_collection_stats(self):
        return {
            'total_documents': self.collection.count(),
            'collection_name': self.collection.name
        }
