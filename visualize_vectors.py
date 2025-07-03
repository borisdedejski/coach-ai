#!/usr/bin/env python3
"""
Visualize ChromaDB vectors in 2D space using t-SNE and Plotly
"""
import sys
import os
import numpy as np
import json
from pathlib import Path

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    from sklearn.manifold import TSNE
    from sklearn.decomposition import PCA
    import chromadb
except ImportError as e:
    print(f"❌ Missing required packages: {e}")
    print("Please install: pip install plotly scikit-learn")
    sys.exit(1)

def load_vector_data():
    """Load vectors and metadata from ChromaDB"""
    print("📊 Loading vector data from ChromaDB...")
    
    try:
        # Connect to ChromaDB
        db_path = "knowledge/embeddings/chroma_db"
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(name="mental_health_knowledge")
        
        # Get all data
        all_data = collection.get()
        
        if not all_data['documents']:
            print("❌ No documents found in ChromaDB")
            return None, None, None, None
        
        documents = all_data['documents']
        metadatas = all_data['metadatas']
        ids = all_data['ids']
        
        # Get embeddings (we'll need to regenerate them since ChromaDB doesn't store them by default)
        print("🔄 Generating embeddings for visualization...")
        from agents.rag.embedder import embed_texts
        vectors_list = embed_texts(documents)
        
        # Convert to numpy array
        vectors = np.array(vectors_list)
        
        return vectors, documents, metadatas, ids
        
    except Exception as e:
        print(f"❌ Error loading vector data: {e}")
        return None, None, None, None

def create_2d_visualization(vectors, documents, metadatas, ids):
    """Create 2D visualization using t-SNE"""
    print("🎨 Creating 2D visualization...")
    
    # Prepare data
    doc_types = [meta.get('source', 'unknown') for meta in metadatas]
    doc_ids = [f"chunk_{i}" for i in range(len(documents))]
    
    # Create colors based on document types
    unique_types = list(set(doc_types))
    color_map = {doc_type: i for i, doc_type in enumerate(unique_types)}
    colors = [color_map[doc_type] for doc_type in doc_types]
    
    # Reduce dimensionality to 2D using t-SNE
    print("🔧 Reducing dimensions with t-SNE...")
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(vectors)-1))
    reduced_vectors = tsne.fit_transform(vectors)
    
    # Create the 2D scatter plot
    fig = go.Figure(data=[go.Scatter(
        x=reduced_vectors[:, 0],
        y=reduced_vectors[:, 1],
        mode='markers+text',
        marker=dict(
            size=15, 
            color=colors, 
            opacity=0.8,
            colorscale='viridis',
            showscale=True,
            colorbar=dict(title="Document Type")
        ),
        text=doc_ids,
        textposition="top center",
        textfont=dict(size=10),
        hovertemplate="<b>ID:</b> %{text}<br>" +
                     "<b>Type:</b> %{customdata[0]}<br>" +
                     "<b>Content:</b> %{customdata[1]}<br>" +
                     "<b>X:</b> %{x:.3f}<br>" +
                     "<b>Y:</b> %{y:.3f}<extra></extra>",
        customdata=list(zip(doc_types, [doc[:100] + "..." for doc in documents]))
    )])
    
    fig.update_layout(
        title='ChromaDB Vector Store - 2D t-SNE Visualization',
        xaxis_title='t-SNE Dimension 1',
        yaxis_title='t-SNE Dimension 2',
        width=1000,
        height=700,
        margin=dict(r=20, b=10, l=10, t=40),
        showlegend=False
    )
    
    return fig

def create_pca_visualization(vectors, documents, metadatas, ids):
    """Create 2D visualization using PCA"""
    print("🎨 Creating PCA visualization...")
    
    # Prepare data
    doc_types = [meta.get('source', 'unknown') for meta in metadatas]
    doc_ids = [f"chunk_{i}" for i in range(len(documents))]
    
    # Create colors based on document types
    unique_types = list(set(doc_types))
    color_map = {doc_type: i for i, doc_type in enumerate(unique_types)}
    colors = [color_map[doc_type] for doc_type in doc_types]
    
    # Reduce dimensionality to 2D using PCA
    print("🔧 Reducing dimensions with PCA...")
    pca = PCA(n_components=2, random_state=42)
    reduced_vectors = pca.fit_transform(vectors)
    
    # Calculate explained variance
    explained_variance = pca.explained_variance_ratio_
    
    # Create the 2D scatter plot
    fig = go.Figure(data=[go.Scatter(
        x=reduced_vectors[:, 0],
        y=reduced_vectors[:, 1],
        mode='markers+text',
        marker=dict(
            size=15, 
            color=colors, 
            opacity=0.8,
            colorscale='plasma',
            showscale=True,
            colorbar=dict(title="Document Type")
        ),
        text=doc_ids,
        textposition="top center",
        textfont=dict(size=10),
        hovertemplate="<b>ID:</b> %{text}<br>" +
                     "<b>Type:</b> %{customdata[0]}<br>" +
                     "<b>Content:</b> %{customdata[1]}<br>" +
                     "<b>PC1:</b> %{x:.3f}<br>" +
                     "<b>PC2:</b> %{y:.3f}<extra></extra>",
        customdata=list(zip(doc_types, [doc[:100] + "..." for doc in documents]))
    )])
    
    fig.update_layout(
        title=f'ChromaDB Vector Store - 2D PCA Visualization<br><sub>Explained Variance: PC1={explained_variance[0]:.1%}, PC2={explained_variance[1]:.1%}</sub>',
        xaxis_title='Principal Component 1',
        yaxis_title='Principal Component 2',
        width=1000,
        height=700,
        margin=dict(r=20, b=10, l=10, t=40),
        showlegend=False
    )
    
    return fig

def create_similarity_heatmap(vectors, documents, ids):
    """Create similarity heatmap between vectors"""
    print("🔥 Creating similarity heatmap...")
    
    # Calculate cosine similarity matrix
    from sklearn.metrics.pairwise import cosine_similarity
    similarity_matrix = cosine_similarity(vectors)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=similarity_matrix,
        x=ids,
        y=ids,
        colorscale='RdBu_r',
        zmid=0.5,
        text=[[f"{val:.3f}" for val in row] for row in similarity_matrix],
        texttemplate="%{text}",
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title='Vector Similarity Heatmap',
        xaxis_title='Document ID',
        yaxis_title='Document ID',
        width=800,
        height=600,
        margin=dict(r=20, b=10, l=10, t=40)
    )
    
    return fig

def create_comprehensive_visualization(vectors, documents, metadatas, ids):
    """Create a comprehensive visualization with multiple plots"""
    print("🎨 Creating comprehensive visualization...")
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('t-SNE 2D Projection', 'PCA 2D Projection', 'Similarity Heatmap', 'Vector Statistics'),
        specs=[[{"type": "scatter"}, {"type": "scatter"}],
               [{"type": "heatmap"}, {"type": "bar"}]]
    )
    
    # Prepare data
    doc_types = [meta.get('source', 'unknown') for meta in metadatas]
    doc_ids = [f"chunk_{i}" for i in range(len(documents))]
    
    # Create colors
    unique_types = list(set(doc_types))
    color_map = {doc_type: i for i, doc_type in enumerate(unique_types)}
    colors = [color_map[doc_type] for doc_type in doc_types]
    
    # 1. t-SNE plot
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(vectors)-1))
    reduced_vectors_tsne = tsne.fit_transform(vectors)
    
    fig.add_trace(
        go.Scatter(
            x=reduced_vectors_tsne[:, 0],
            y=reduced_vectors_tsne[:, 1],
            mode='markers+text',
            marker=dict(size=12, color=colors, colorscale='viridis'),
            text=doc_ids,
            textposition="top center",
            textfont=dict(size=8),
            name='t-SNE',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # 2. PCA plot
    pca = PCA(n_components=2, random_state=42)
    reduced_vectors_pca = pca.fit_transform(vectors)
    
    fig.add_trace(
        go.Scatter(
            x=reduced_vectors_pca[:, 0],
            y=reduced_vectors_pca[:, 1],
            mode='markers+text',
            marker=dict(size=12, color=colors, colorscale='plasma'),
            text=doc_ids,
            textposition="top center",
            textfont=dict(size=8),
            name='PCA',
            showlegend=False
        ),
        row=1, col=2
    )
    
    # 3. Similarity heatmap
    from sklearn.metrics.pairwise import cosine_similarity
    similarity_matrix = cosine_similarity(vectors)
    
    fig.add_trace(
        go.Heatmap(
            z=similarity_matrix,
            x=doc_ids,
            y=doc_ids,
            colorscale='RdBu_r',
            zmid=0.5,
            showscale=True,
            name='Similarity'
        ),
        row=2, col=1
    )
    
    # 4. Vector statistics
    vector_norms = np.linalg.norm(vectors, axis=1)
    fig.add_trace(
        go.Bar(
            x=doc_ids,
            y=vector_norms,
            name='Vector Norm',
            marker_color=colors,
            text=[f"{norm:.3f}" for norm in vector_norms],
            textposition='auto'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title='ChromaDB Vector Store - Comprehensive Analysis',
        width=1200,
        height=800,
        showlegend=False
    )
    
    return fig

def main():
    """Main function to create visualizations"""
    print("🎨 ChromaDB Vector Visualization")
    print("=" * 40)
    
    # Load data
    vectors, documents, metadatas, ids = load_vector_data()
    
    if vectors is None:
        print("❌ Failed to load vector data")
        return
    
    print(f"✅ Loaded {len(documents)} documents with {vectors.shape[1]}-dimensional vectors")
    
    # Create visualizations
    try:
        # 1. t-SNE visualization
        print("\n1️⃣ Creating t-SNE visualization...")
        fig_tsne = create_2d_visualization(vectors, documents, metadatas, ids)
        fig_tsne.show()
        
        # 2. PCA visualization
        print("\n2️⃣ Creating PCA visualization...")
        fig_pca = create_pca_visualization(vectors, documents, metadatas, ids)
        fig_pca.show()
        
        # 3. Similarity heatmap
        print("\n3️⃣ Creating similarity heatmap...")
        fig_heatmap = create_similarity_heatmap(vectors, documents, ids)
        fig_heatmap.show()
        
        # 4. Comprehensive visualization
        print("\n4️⃣ Creating comprehensive visualization...")
        fig_comprehensive = create_comprehensive_visualization(vectors, documents, metadatas, ids)
        fig_comprehensive.show()
        
        print("\n✅ All visualizations created successfully!")
        print("💡 Tips:")
        print("   - t-SNE shows local structure and clusters")
        print("   - PCA shows global variance patterns")
        print("   - Heatmap shows pairwise similarities")
        print("   - Vector norms show embedding magnitudes")
        
    except Exception as e:
        print(f"❌ Error creating visualizations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 