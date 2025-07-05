import numpy as np
import os
import sys
import json
import re
import csv
import pandas as pd
from typing import List, Dict, Any

# Add the project root to the path so we can import from agents
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agents.rag.embedder import embed_texts
from agents.rag.loader import load_and_split

def load_mental_health_dataset():
    """Load the mental health chatbot dataset from Hugging Face"""
    try:
        from datasets import load_dataset
        print("📊 Loading mental health chatbot dataset...")
        
        # Load the dataset
        ds = load_dataset("heliosbrahma/mental_health_chatbot_dataset")
        
        print(f"✅ Dataset loaded successfully!")
        for split_name, split_data in ds.items():
            print(f"   {split_name}: {len(split_data)} examples")
        
        return ds
        
    except ImportError:
        print("❌ 'datasets' package not found. Installing...")
        os.system("pip install datasets")
        from datasets import load_dataset
        return load_mental_health_dataset()
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        return None

def load_intents_dataset():
    """Load the intents.json file"""
    try:
        intents_path = os.path.join(project_root, 'knowledge', 'intents.json')
        print("📊 Loading intents dataset...")
        
        with open(intents_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        intents = data.get('intents', [])
        print(f"✅ Loaded {len(intents)} intents")
        
        return intents
        
    except Exception as e:
        print(f"❌ Error loading intents: {e}")
        return None

def load_healthanxiety_dataset():
    """Load the healthanxiety_dataset.csv file"""
    try:
        csv_path = os.path.join(project_root, 'knowledge', 'healthanxiety_dataset.csv')
        print("📊 Loading health anxiety dataset...")
        
        # Read CSV with pandas for better handling of large files
        df = pd.read_csv(csv_path)
        
        print(f"✅ Loaded {len(df)} health anxiety posts")
        print(f"   Columns: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading health anxiety dataset: {e}")
        return None

def load_mental_health_survey_dataset():
    """Load the Mental Health Dataset.csv file"""
    try:
        csv_path = os.path.join(project_root, 'knowledge', 'Mental Health Dataset.csv')
        print("📊 Loading mental health survey dataset...")
        
        # Read CSV with pandas
        df = pd.read_csv(csv_path)
        
        print(f"✅ Loaded {len(df)} survey responses")
        print(f"   Columns: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading mental health survey dataset: {e}")
        return None

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text or not isinstance(text, str):
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', text)
    
    return text

def assess_quality(text: str) -> float:
    """Assess the quality of a text chunk"""
    if not text:
        return 0.0
    
    # Length-based quality
    length_score = min(len(text) / 1500, 1.0)
    
    # Content-based quality indicators
    has_mental_health_keywords = any(keyword in text.lower() for keyword in [
        'mental', 'health', 'anxiety', 'depression', 'stress', 'therapy',
        'coping', 'emotion', 'feeling', 'mood', 'support', 'help',
        'counseling', 'psychology', 'wellness', 'mindfulness'
    ])
    
    # Structure-based quality
    has_structure = any(marker in text for marker in [':', '.', '?', '!'])
    
    # Calculate overall quality score
    quality_score = (
        length_score * 0.4 +
        (1.0 if has_mental_health_keywords else 0.0) * 0.4 +
        (1.0 if has_structure else 0.0) * 0.2
    )
    
    return quality_score

def process_intents_for_knowledge_base(intents):
    """Process intents into knowledge base chunks"""
    print("🔧 Processing intents for knowledge base...")
    
    knowledge_chunks = []
    stats = {
        "total_intents": 0,
        "processed_chunks": 0,
        "quality_issues": 0
    }
    
    for intent in intents:
        stats["total_intents"] += 1
        
        tag = intent.get('tag', 'unknown')
        patterns = intent.get('patterns', [])
        responses = intent.get('responses', [])
        
        # Create chunks from patterns and responses
        for i, pattern in enumerate(patterns):
            if pattern and len(pattern) >= 10:
                # Create a Q&A chunk
                chunk = f"Intent: {tag}\nQuestion: {clean_text(pattern)}"
                
                # Add a response if available
                if responses and i < len(responses):
                    chunk += f"\n\nResponse: {clean_text(responses[i])}"
                elif responses:
                    chunk += f"\n\nResponse: {clean_text(responses[0])}"
                
                quality = assess_quality(chunk)
                if quality >= 0.5 and len(chunk) <= 1500:
                    knowledge_chunks.append(chunk)
                    stats["processed_chunks"] += 1
                else:
                    stats["quality_issues"] += 1
    
    print(f"✅ Processed {len(knowledge_chunks)} intent chunks")
    print(f"   Total intents: {stats['total_intents']}")
    print(f"   Processed chunks: {stats['processed_chunks']}")
    print(f"   Quality issues: {stats['quality_issues']}")
    
    return knowledge_chunks

def process_healthanxiety_for_knowledge_base(df):
    """Process health anxiety dataset into knowledge base chunks"""
    print("🔧 Processing health anxiety dataset for knowledge base...")
    
    knowledge_chunks = []
    stats = {
        "total_posts": 0,
        "processed_chunks": 0,
        "quality_issues": 0
    }
    
    # Focus on the 'post' column which contains the main content
    for idx, row in df.iterrows():
        stats["total_posts"] += 1
        
        post_text = row.get('post', '')
        if post_text and len(post_text) >= 50:
            # Clean and process the post
            cleaned_text = clean_text(post_text)
            
            # Create a chunk with context
            chunk = f"Health Anxiety Experience: {cleaned_text}"
            
            quality = assess_quality(chunk)
            if quality >= 0.6 and len(chunk) <= 1500:
                knowledge_chunks.append(chunk)
                stats["processed_chunks"] += 1
            else:
                stats["quality_issues"] += 1
        
        # Progress indicator
        if (idx + 1) % 1000 == 0:
            print(f"     Processed {idx + 1} posts...")
    
    print(f"✅ Processed {len(knowledge_chunks)} health anxiety chunks")
    print(f"   Total posts: {stats['total_posts']}")
    print(f"   Processed chunks: {stats['processed_chunks']}")
    print(f"   Quality issues: {stats['quality_issues']}")
    
    return knowledge_chunks

def process_mental_health_survey_for_knowledge_base(df):
    """Process mental health survey dataset into knowledge base chunks"""
    print("🔧 Processing mental health survey dataset for knowledge base...")
    
    knowledge_chunks = []
    stats = {
        "total_responses": 0,
        "processed_chunks": 0,
        "quality_issues": 0
    }
    
    # Focus on the 'mental_health_interview' column which contains detailed responses
    for idx, row in df.iterrows():
        stats["total_responses"] += 1
        
        interview_text = row.get('mental_health_interview', '')
        if interview_text and len(interview_text) >= 30:
            # Clean and process the interview text
            cleaned_text = clean_text(interview_text)
            
            # Create a chunk with demographic context
            gender = row.get('Gender', 'Unknown')
            country = row.get('Country', 'Unknown')
            occupation = row.get('Occupation', 'Unknown')
            
            chunk = f"Mental Health Survey Response:\nDemographics: {gender}, {country}, {occupation}\n\nResponse: {cleaned_text}"
            
            quality = assess_quality(chunk)
            if quality >= 0.5 and len(chunk) <= 1500:
                knowledge_chunks.append(chunk)
                stats["processed_chunks"] += 1
            else:
                stats["quality_issues"] += 1
        
        # Progress indicator
        if (idx + 1) % 1000 == 0:
            print(f"     Processed {idx + 1} responses...")
    
    print(f"✅ Processed {len(knowledge_chunks)} survey response chunks")
    print(f"   Total responses: {stats['total_responses']}")
    print(f"   Processed chunks: {stats['processed_chunks']}")
    print(f"   Quality issues: {stats['quality_issues']}")
    
    return knowledge_chunks

def process_dataset_for_knowledge_base(dataset):
    """Process the dataset into knowledge base chunks"""
    print("🔧 Processing dataset for knowledge base...")
    
    knowledge_chunks = []
    stats = {
        "total_examples": 0,
        "processed_chunks": 0,
        "filtered_out": 0,
        "quality_issues": 0
    }
    
    # Process each split
    for split_name, split_data in dataset.items():
        print(f"   Processing {split_name} split...")
        
        for i, example in enumerate(split_data):
            stats["total_examples"] += 1
            
            # Handle conversation format in 'text' field
            if 'text' in example and example['text']:
                text = clean_text(example['text'])
                
                if text and len(text) >= 50:
                    # Split conversation into question and answer
                    if '<HUMAN>:' in text and '<ASSISTANT>:' in text:
                        parts = text.split('<ASSISTANT>:')
                        if len(parts) == 2:
                            human_part = parts[0].replace('<HUMAN>:', '').strip()
                            assistant_part = parts[1].strip()
                            
                            chunk = f"Mental Health Question: {human_part}\n\nResponse: {assistant_part}"
                            
                            quality = assess_quality(chunk)
                            if quality >= 0.6 and len(chunk) <= 1500:
                                knowledge_chunks.append(chunk)
                                stats["processed_chunks"] += 1
                            else:
                                stats["quality_issues"] += 1
                        else:
                            stats["quality_issues"] += 1
                    else:
                        # If not in conversation format, treat as general text
                        quality = assess_quality(text)
                        if quality >= 0.6 and len(text) <= 1500:
                            knowledge_chunks.append(text)
                            stats["processed_chunks"] += 1
                        else:
                            stats["quality_issues"] += 1
            
            # Handle instruction/output format (fallback)
            elif 'instruction' in example and example['instruction']:
                instruction = clean_text(example['instruction'])
                output = clean_text(example.get('output', ''))
                
                if instruction and len(instruction) >= 50:
                    chunk = f"Mental Health Guidance: {instruction}"
                    if output:
                        chunk += f"\n\nResponse: {output}"
                    
                    quality = assess_quality(chunk)
                    if quality >= 0.6 and len(chunk) <= 1500:
                        knowledge_chunks.append(chunk)
                        stats["processed_chunks"] += 1
                    else:
                        stats["quality_issues"] += 1
            
            # Handle input/output format (fallback)
            elif 'input' in example and example['input']:
                input_text = clean_text(example['input'])
                output = clean_text(example.get('output', ''))
                
                if input_text and len(input_text) >= 50:
                    chunk = f"Mental Health Question: {input_text}"
                    if output:
                        chunk += f"\n\nResponse: {output}"
                    
                    quality = assess_quality(chunk)
                    if quality >= 0.6 and len(chunk) <= 1500:
                        knowledge_chunks.append(chunk)
                        stats["processed_chunks"] += 1
                    else:
                        stats["quality_issues"] += 1
    
    print(f"✅ Processed {len(knowledge_chunks)} knowledge chunks")
    print(f"   Total examples: {stats['total_examples']}")
    print(f"   Processed chunks: {stats['processed_chunks']}")
    print(f"   Quality issues: {stats['quality_issues']}")
    
    return knowledge_chunks

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    knowledge_path = os.path.join(project_root, 'knowledge', 'mental_health_tips.md')
    embeddings_dir = os.path.join(project_root, 'knowledge', 'embeddings')
    embeddings_path = os.path.join(embeddings_dir, 'mental_health_embeddings.npy')
    chunks_path = os.path.join(embeddings_dir, 'mental_health_chunks.json')

    print("🚀 Indexing Mental Health Knowledge Base")
    print("=" * 50)

    # Step 1: Load existing knowledge base
    print("📖 Loading existing knowledge base...")
    chunks = load_and_split(knowledge_path)
    print(f"✅ Loaded {len(chunks)} chunks from existing knowledge base")

    # Step 2: Load and process Hugging Face dataset
    print("\n📊 Loading mental health dataset...")
    dataset = load_mental_health_dataset()
    if dataset:
        dataset_chunks = process_dataset_for_knowledge_base(dataset)
        chunks.extend(dataset_chunks)
        print(f"✅ Added {len(dataset_chunks)} chunks from Hugging Face dataset")
    else:
        print("⚠️  Could not load Hugging Face dataset, continuing...")

    # Step 3: Load and process intents dataset
    print("\n📊 Loading intents dataset...")
    intents = load_intents_dataset()
    if intents:
        intents_chunks = process_intents_for_knowledge_base(intents)
        chunks.extend(intents_chunks)
        print(f"✅ Added {len(intents_chunks)} chunks from intents dataset")
    else:
        print("⚠️  Could not load intents dataset, continuing...")

    # Step 4: Load and process health anxiety dataset
    print("\n📊 Loading health anxiety dataset...")
    health_anxiety_df = load_healthanxiety_dataset()
    if health_anxiety_df is not None:
        health_anxiety_chunks = process_healthanxiety_for_knowledge_base(health_anxiety_df)
        chunks.extend(health_anxiety_chunks)
        print(f"✅ Added {len(health_anxiety_chunks)} chunks from health anxiety dataset")
    else:
        print("⚠️  Could not load health anxiety dataset, continuing...")

    # Step 5: Load and process mental health survey dataset
    print("\n📊 Loading mental health survey dataset...")
    survey_df = load_mental_health_survey_dataset()
    if survey_df is not None:
        survey_chunks = process_mental_health_survey_for_knowledge_base(survey_df)
        chunks.extend(survey_chunks)
        print(f"✅ Added {len(survey_chunks)} chunks from mental health survey dataset")
    else:
        print("⚠️  Could not load mental health survey dataset, continuing...")

    # Step 6: Generate embeddings
    print(f"\n🔧 Generating embeddings for {len(chunks)} total chunks...")
    embeddings = embed_texts(chunks)
    
    # Step 7: Save to files
    os.makedirs(embeddings_dir, exist_ok=True)
    np.save(embeddings_path, embeddings)
    with open(chunks_path, 'w') as f:
        json.dump(chunks, f)
    
    print(f"✅ Saved {len(embeddings)} embeddings and {len(chunks)} chunks.")
    print(f"💾 Files saved to:")
    print(f"   Embeddings: {embeddings_path}")
    print(f"   Chunks: {chunks_path}")

    # Step 8: Update ChromaDB if available
    try:
        print("\n🔧 Updating ChromaDB vector store...")
        from agents.rag.chroma_store import ChromaVectorStore
        vector_store = ChromaVectorStore()
        
        # Check if we have new chunks to add
        existing_count = vector_store.collection.count()
        print(f"   Current ChromaDB documents: {existing_count}")
        print(f"   Total chunks to add: {len(chunks)}")
        
        if existing_count < len(chunks):
            # We have new chunks to add
            print("   Adding new chunks to ChromaDB...")
            # Get only the new chunks (skip the first existing_count chunks)
            new_chunks = chunks[existing_count:]
            vector_store.add_chunks(new_chunks, source="extended_knowledge_base")
            print(f"✅ Added {len(new_chunks)} new chunks to ChromaDB!")
        else:
            # Recreate from embeddings (fallback)
            print("   Recreating ChromaDB from embeddings...")
            vector_store.create_from_embeddings()
            print("✅ ChromaDB vector store updated successfully!")
            
    except Exception as e:
        print(f"⚠️  Could not update ChromaDB: {e}")

    print("\n🎉 Knowledge base indexing complete!")
    print(f"📊 Summary:")
    print(f"   Total knowledge chunks: {len(chunks)}")
    print(f"   Total embeddings: {len(embeddings)}")
    print(f"   ChromaDB documents: {existing_count if 'existing_count' in locals() else 'Unknown'}")

if __name__ == "__main__":
    main()
