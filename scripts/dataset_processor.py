#!/usr/bin/env python3
"""
Advanced dataset processor for mental health knowledge base extension
Supports multiple datasets and provides data quality control
"""
import sys
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@dataclass
class DatasetConfig:
    """Configuration for dataset processing"""
    name: str
    dataset_id: str
    chunk_size: int = 500
    chunk_overlap: int = 50
    min_length: int = 50
    max_length: int = 2000
    quality_threshold: float = 0.7

class MentalHealthDatasetProcessor:
    """Processor for mental health datasets"""
    
    def __init__(self, config: DatasetConfig):
        self.config = config
        self.processed_chunks = []
        self.stats = {
            "total_examples": 0,
            "processed_chunks": 0,
            "filtered_out": 0,
            "quality_issues": 0
        }
    
    def load_dataset(self) -> Optional[Dict]:
        """Load dataset from Hugging Face"""
        try:
            from datasets import load_dataset
            print(f"📊 Loading dataset: {self.config.dataset_id}")
            
            dataset = load_dataset(self.config.dataset_id)
            
            print(f"✅ Dataset loaded successfully!")
            for split_name, split_data in dataset.items():
                print(f"   {split_name}: {len(split_data)} examples")
            
            return dataset
            
        except ImportError:
            print("❌ 'datasets' package not found. Installing...")
            os.system("pip install datasets")
            return self.load_dataset()
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text or not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', text)
        
        return text
    
    def assess_quality(self, text: str) -> float:
        """Assess the quality of a text chunk"""
        if not text:
            return 0.0
        
        # Length-based quality
        length_score = min(len(text) / self.config.max_length, 1.0)
        
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
    
    def process_example(self, example: Dict[str, Any]) -> List[str]:
        """Process a single dataset example into knowledge chunks"""
        chunks = []
        
        # Handle different dataset formats
        if 'instruction' in example and example['instruction']:
            instruction = self.clean_text(example['instruction'])
            output = self.clean_text(example.get('output', ''))
            
            if instruction and len(instruction) >= self.config.min_length:
                chunk = f"Mental Health Guidance: {instruction}"
                if output:
                    chunk += f"\n\nResponse: {output}"
                
                quality = self.assess_quality(chunk)
                if quality >= self.config.quality_threshold:
                    chunks.append(chunk)
                else:
                    self.stats["quality_issues"] += 1
        
        elif 'input' in example and example['input']:
            input_text = self.clean_text(example['input'])
            output = self.clean_text(example.get('output', ''))
            
            if input_text and len(input_text) >= self.config.min_length:
                chunk = f"Mental Health Question: {input_text}"
                if output:
                    chunk += f"\n\nResponse: {output}"
                
                quality = self.assess_quality(chunk)
                if quality >= self.config.quality_threshold:
                    chunks.append(chunk)
                else:
                    self.stats["quality_issues"] += 1
        
        elif 'text' in example and example['text']:
            text = self.clean_text(example['text'])
            
            if text and len(text) >= self.config.min_length:
                quality = self.assess_quality(text)
                if quality >= self.config.quality_threshold:
                    chunks.append(text)
                else:
                    self.stats["quality_issues"] += 1
        
        return chunks
    
    def process_dataset(self, dataset: Dict) -> List[str]:
        """Process the entire dataset"""
        print(f"🔧 Processing dataset: {self.config.name}")
        
        all_chunks = []
        
        for split_name, split_data in dataset.items():
            print(f"   Processing {split_name} split...")
            
            for i, example in enumerate(split_data):
                self.stats["total_examples"] += 1
                
                chunks = self.process_example(example)
                all_chunks.extend(chunks)
                
                # Progress indicator
                if (i + 1) % 1000 == 0:
                    print(f"     Processed {i + 1} examples...")
        
        # Filter chunks by length
        filtered_chunks = []
        for chunk in all_chunks:
            if self.config.min_length <= len(chunk) <= self.config.max_length:
                filtered_chunks.append(chunk)
            else:
                self.stats["filtered_out"] += 1
        
        self.stats["processed_chunks"] = len(filtered_chunks)
        self.processed_chunks = filtered_chunks
        
        print(f"✅ Processing complete!")
        print(f"   Total examples: {self.stats['total_examples']}")
        print(f"   Processed chunks: {self.stats['processed_chunks']}")
        print(f"   Filtered out: {self.stats['filtered_out']}")
        print(f"   Quality issues: {self.stats['quality_issues']}")
        
        return filtered_chunks
    
    def save_processed_data(self, output_dir: str = "knowledge/embeddings"):
        """Save processed data to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save chunks
        chunks_file = os.path.join(output_dir, f"{self.config.name}_chunks.json")
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(self.processed_chunks, f, ensure_ascii=False, indent=2)
        
        # Save stats
        stats_file = os.path.join(output_dir, f"{self.config.name}_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved {len(self.processed_chunks)} chunks to {chunks_file}")
        print(f"💾 Saved stats to {stats_file}")

def get_dataset_configs() -> List[DatasetConfig]:
    """Get configurations for different mental health datasets"""
    return [
        DatasetConfig(
            name="mental_health_chatbot",
            dataset_id="heliosbrahma/mental_health_chatbot_dataset",
            chunk_size=500,
            chunk_overlap=50,
            min_length=100,
            max_length=1500,
            quality_threshold=0.6
        ),
        DatasetConfig(
            name="mental_health_qa",
            dataset_id="mental/mental_health_qa",
            chunk_size=400,
            chunk_overlap=50,
            min_length=80,
            max_length=1200,
            quality_threshold=0.7
        ),
        DatasetConfig(
            name="therapy_conversations",
            dataset_id="AlekseyKorshuk/therapy-conversations",
            chunk_size=600,
            chunk_overlap=100,
            min_length=150,
            max_length=2000,
            quality_threshold=0.8
        )
    ]

def main():
    """Main function to process datasets"""
    print("🚀 Mental Health Dataset Processor")
    print("=" * 40)
    
    configs = get_dataset_configs()
    
    for config in configs:
        print(f"\n📋 Processing dataset: {config.name}")
        print("-" * 30)
        
        # Create processor
        processor = MentalHealthDatasetProcessor(config)
        
        # Load dataset
        dataset = processor.load_dataset()
        if not dataset:
            print(f"❌ Failed to load dataset: {config.dataset_id}")
            continue
        
        # Process dataset
        chunks = processor.process_dataset(dataset)
        
        if chunks:
            # Save processed data
            processor.save_processed_data()
            
            # Add to vector store
            try:
                from agents.rag.chroma_store import ChromaVectorStore
                vector_store = ChromaVectorStore()
                vector_store.add_documents(chunks, config.chunk_size, config.chunk_overlap)
                print(f"✅ Added {len(chunks)} chunks to vector store")
            except Exception as e:
                print(f"❌ Error adding to vector store: {e}")
        else:
            print(f"⚠️  No valid chunks generated for {config.name}")
    
    print(f"\n🎉 Dataset processing complete!")

if __name__ == "__main__":
    main() 