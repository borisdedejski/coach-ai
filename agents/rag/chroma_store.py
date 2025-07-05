import os
import json
from typing import List, Dict, Any, Optional
import chromadb


class ChromaVectorStore:
    def __init__(self, embeddings_dir: str = "knowledge/embeddings"):
        self.embeddings_dir = embeddings_dir
        self.client = None
        self.collection = None
        self.chunks = []
        self.setup_chroma()
    
    def setup_chroma(self):
        """Set up ChromaDB client and collection"""
        try:
            # Initialize ChromaDB client with persistent storage
            db_path = os.path.join(self.embeddings_dir, "chroma_db")
            self.client = chromadb.PersistentClient(path=db_path)
            
            # Get or create collection
            collection_name = "mental_health_knowledge"
            try:
                self.collection = self.client.get_collection(name=collection_name)
                print(f"✅ Loaded existing ChromaDB collection: {collection_name}")
            except:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"description": "Mental health tips and strategies"}
                )
                print(f"✅ Created new ChromaDB collection: {collection_name}")
            
            # Load existing chunks if available
            self.load_chunks()
            
        except Exception as e:
            print(f"❌ Error setting up ChromaDB: {e}")
            raise
    
    def load_chunks(self):
        """Load existing chunks from JSON file"""
        chunks_path = os.path.join(self.embeddings_dir, "mental_health_chunks.json")
        if os.path.exists(chunks_path):
            with open(chunks_path, 'r') as f:
                self.chunks = json.load(f)
            print(f"✅ Loaded {len(self.chunks)} chunks from file")
        else:
            print("⚠️  No existing chunks file found")
    
    def create_from_embeddings(self):
        """Create ChromaDB collection from existing embeddings"""
        embeddings_path = os.path.join(self.embeddings_dir, "mental_health_embeddings.npy")
        chunks_path = os.path.join(self.embeddings_dir, "mental_health_chunks.json")
        
        if not os.path.exists(embeddings_path) or not os.path.exists(chunks_path):
            raise FileNotFoundError("Knowledge base not found. Please run scripts/index_knowledge_base.py first.")
        
        # Load existing chunks
        with open(chunks_path, 'r') as f:
            self.chunks = json.load(f)
        
        # Check if collection is empty
        if self.collection.count() > 0:
            print("✅ ChromaDB collection already populated")
            return
        
        print(f"🔧 Populating ChromaDB with {len(self.chunks)} chunks...")
        
        # Add documents to ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(self.chunks):
            documents.append(chunk)
            metadatas.append({"source": "mental_health_tips", "chunk_id": i})
            ids.append(f"chunk_{i}")
        
        # Add to collection
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Added {len(documents)} documents to ChromaDB")
    
    def search(self, query: str, top_k: int = 3, similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Search for similar documents using ChromaDB
        
        Args:
            query: The search query
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of dictionaries with chunk text and similarity scores
        """
        if self.collection is None:
            return []
        
        try:
            # Search in ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # Process results
            processed_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    # Convert distance to similarity score (ChromaDB uses L2 distance)
                    # Lower distance = higher similarity
                    similarity_score = 1.0 / (1.0 + distance)
                    
                    if similarity_score >= similarity_threshold:
                        processed_results.append({
                            "chunk": doc,
                            "similarity_score": float(similarity_score),
                            "index": metadata.get("chunk_id", i)
                        })
            
            return processed_results
            
        except Exception as e:
            print(f"❌ Error searching ChromaDB: {e}")
            return []
    
    def add_chunks(self, chunks: List[str], source: str = "dataset"):
        """
        Add pre-chunked documents to the vector store
        
        Args:
            chunks: List of pre-chunked document texts
            source: Source identifier for the chunks
        """
        if not chunks:
            return
        
        # Add to ChromaDB
        documents_to_add = []
        metadatas = []
        ids = []
        
        start_id = self.collection.count()
        
        for i, chunk in enumerate(chunks):
            documents_to_add.append(chunk)
            metadatas.append({"source": source, "chunk_id": start_id + i})
            ids.append(f"chunk_{start_id + i}")
        
        # Add to collection
        self.collection.add(
            documents=documents_to_add,
            metadatas=metadatas,
            ids=ids
        )
        
        # Update chunks list
        self.chunks.extend(chunks)
        
        # Save updated chunks
        chunks_path = os.path.join(self.embeddings_dir, "mental_health_chunks.json")
        with open(chunks_path, 'w') as f:
            json.dump(self.chunks, f)
        
        print(f"✅ Added {len(chunks)} new chunks to ChromaDB")
    
    def add_documents(self, documents: List[str], chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Add new documents to the vector store
        
        Args:
            documents: List of document texts
            chunk_size: Size of each chunk
            chunk_overlap: Overlap between chunks
        """
        from agents.rag.loader import load_and_split
        
        # Process documents into chunks
        all_chunks = []
        for doc in documents:
            chunks = load_and_split(doc, chunk_size, chunk_overlap)
            all_chunks.extend(chunks)
        
        if not all_chunks:
            return
        
        # Add to ChromaDB
        documents_to_add = []
        metadatas = []
        ids = []
        
        start_id = self.collection.count()
        
        for i, chunk in enumerate(all_chunks):
            documents_to_add.append(chunk)
            metadatas.append({"source": "new_document", "chunk_id": start_id + i})
            ids.append(f"chunk_{start_id + i}")
        
        # Add to collection
        self.collection.add(
            documents=documents_to_add,
            metadatas=metadatas,
            ids=ids
        )
        
        # Update chunks list
        self.chunks.extend(all_chunks)
        
        # Save updated chunks
        chunks_path = os.path.join(self.embeddings_dir, "mental_health_chunks.json")
        with open(chunks_path, 'w') as f:
            json.dump(self.chunks, f)
        
        print(f"✅ Added {len(all_chunks)} new chunks to ChromaDB")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        if self.collection is None:
            return {"error": "Collection not initialized"}
        
        try:
            count = self.collection.count()
            return {
                "total_vectors": count,
                "total_chunks": len(self.chunks),
                "index_type": "ChromaDB",
                "collection_name": self.collection.name
            }
        except Exception as e:
            return {"error": f"Failed to get stats: {e}"}
    
    def similarity_search(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        Alias for search method for compatibility
        """
        return self.search(query, top_k=k) 