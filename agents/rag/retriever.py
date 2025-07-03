import numpy as np
import json
import os
from typing import List, Tuple, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
from agents.rag.embedder import embed_texts
from agents.rag.chroma_store import ChromaVectorStore

class RAGRetriever:
    def __init__(self, embeddings_dir: str = "knowledge/embeddings", use_chroma: bool = True):
        self.embeddings_dir = embeddings_dir
        self.use_chroma = use_chroma
        
        if use_chroma:
            self.vector_store = ChromaVectorStore(embeddings_dir)
            self.embeddings = None
            self.chunks = None
        else:
            self.vector_store = None
            self.embeddings = None
            self.chunks = None
            self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load the pre-computed embeddings and chunks (fallback method)"""
        embeddings_path = os.path.join(self.embeddings_dir, "mental_health_embeddings.npy")
        chunks_path = os.path.join(self.embeddings_dir, "mental_health_chunks.json")
        
        if os.path.exists(embeddings_path) and os.path.exists(chunks_path):
            self.embeddings = np.load(embeddings_path)
            with open(chunks_path, 'r') as f:
                self.chunks = json.load(f)
        else:
            raise FileNotFoundError("Knowledge base not found. Please run scripts/index_knowledge_base.py first.")
    
    def retrieve_relevant_chunks(self, query: str, top_k: int = 3, similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant chunks for a given query
        
        Args:
            query: The user's query
            top_k: Number of top chunks to retrieve
            similarity_threshold: Minimum similarity score to include a chunk
            
        Returns:
            List of dictionaries containing chunk text and similarity score
        """
        if self.use_chroma and self.vector_store:
            # Use ChromaDB for retrieval
            return self.vector_store.search(query, top_k, similarity_threshold)
        else:
            # Fallback to numpy-based retrieval
            return self._numpy_retrieval(query, top_k, similarity_threshold)
    
    def _numpy_retrieval(self, query: str, top_k: int = 3, similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Fallback numpy-based retrieval method"""
        if self.embeddings is None or self.chunks is None:
            return []
        
        # Embed the query
        query_embedding = embed_texts([query])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top-k most similar chunks
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            similarity_score = similarities[idx]
            if similarity_score >= similarity_threshold:
                results.append({
                    "chunk": self.chunks[idx],
                    "similarity_score": float(similarity_score),
                    "index": int(idx)
                })
        
        return results
    
    def get_context_for_response(self, query: str, max_chunks: int = 2) -> str:
        """
        Get formatted context from knowledge base for response generation
        
        Args:
            query: The user's query
            max_chunks: Maximum number of chunks to include in context
            
        Returns:
            Formatted context string
        """
        relevant_chunks = self.retrieve_relevant_chunks(query, top_k=max_chunks)
        
        if not relevant_chunks:
            return "No relevant information found in knowledge base."
        
        context_parts = ["Relevant information from knowledge base:"]
        for i, result in enumerate(relevant_chunks, 1):
            context_parts.append(f"{i}. {result['chunk']}")
        
        return "\n".join(context_parts)
    
    def get_similarity_score(self, query: str) -> float:
        """
        Get the highest similarity score for a query
        
        Args:
            query: The user's query
            
        Returns:
            Highest similarity score
        """
        relevant_chunks = self.retrieve_relevant_chunks(query, top_k=1)
        return relevant_chunks[0]["similarity_score"] if relevant_chunks else 0.0
    
    def get_vector_store_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        if self.use_chroma and self.vector_store:
            return self.vector_store.get_stats()
        else:
            return {
                "total_vectors": len(self.embeddings) if self.embeddings is not None else 0,
                "total_chunks": len(self.chunks) if self.chunks is not None else 0,
                "index_type": "numpy"
            }
    
    def add_documents(self, documents: List[str], chunk_size: int = 500, chunk_overlap: int = 50):
        """Add new documents to the vector store"""
        if self.use_chroma and self.vector_store:
            self.vector_store.add_documents(documents, chunk_size, chunk_overlap)
        else:
            print("Document addition only supported with ChromaDB vector store")
    
    def initialize_chroma(self):
        """Initialize ChromaDB with existing embeddings"""
        if self.use_chroma and self.vector_store:
            self.vector_store.create_from_embeddings() 