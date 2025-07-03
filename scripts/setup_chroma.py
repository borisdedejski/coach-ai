#!/usr/bin/env python3
"""
Setup ChromaDB vector store from existing embeddings
"""
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agents.rag.chroma_store import ChromaVectorStore
from agents.rag.retriever import RAGRetriever

def main():
    """Set up ChromaDB vector store"""
    print("🔍 Setting up ChromaDB Vector Store")
    print("=" * 40)
    
    try:
        # Create ChromaDB vector store
        print("Creating ChromaDB collection from existing embeddings...")
        vector_store = ChromaVectorStore()
        
        # Initialize with existing embeddings
        vector_store.create_from_embeddings()
        
        # Test the retriever
        print("\nTesting RAG retriever with ChromaDB...")
        retriever = RAGRetriever(use_chroma=True)
        
        # Get stats
        stats = retriever.get_vector_store_stats()
        print(f"\n✅ Vector Store Statistics:")
        print(f"   Total vectors: {stats['total_vectors']}")
        print(f"   Total chunks: {stats['total_chunks']}")
        print(f"   Index type: {stats['index_type']}")
        print(f"   Collection: {stats['collection_name']}")
        
        # Test search
        test_queries = [
            "I'm feeling stressed about work",
            "How can I improve my sleep?",
            "I need help with anxiety"
        ]
        
        print(f"\n🧪 Testing search functionality:")
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = retriever.retrieve_relevant_chunks(query, top_k=2)
            print(f"Found {len(results)} relevant chunks:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. Score: {result['similarity_score']:.3f}")
                print(f"     Text: {result['chunk'][:80]}...")
        
        print(f"\n🎉 ChromaDB vector store setup complete!")
        print(f"   The system is now using ChromaDB for efficient similarity search.")
        
    except Exception as e:
        print(f"❌ Error setting up ChromaDB: {e}")
        print("Make sure you have run 'python scripts/index_knowledge_base.py' first.")
        return False
    
    return True

if __name__ == "__main__":
    main() 