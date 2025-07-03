import numpy as np
import os
import sys
import json

# Add the project root to the path so we can import from agents
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agents.rag.embedder import embed_texts
from agents.rag.loader import load_and_split

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    knowledge_path = os.path.join(project_root, 'knowledge', 'mental_health_tips.md')
    embeddings_dir = os.path.join(project_root, 'knowledge', 'embeddings')
    embeddings_path = os.path.join(embeddings_dir, 'mental_health_embeddings.npy')
    chunks_path = os.path.join(embeddings_dir, 'mental_health_chunks.json')

    chunks = load_and_split(knowledge_path)
    embeddings = embed_texts(chunks)
    
    os.makedirs(embeddings_dir, exist_ok=True)
    np.save(embeddings_path, embeddings)
    with open(chunks_path, 'w') as f:
        json.dump(chunks, f)
    
    print(f"Saved {len(embeddings)} embeddings and {len(chunks)} chunks.")

if __name__ == "__main__":
    main()
