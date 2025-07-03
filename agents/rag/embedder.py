from sentence_transformers import SentenceTransformer
from langchain_openai import OpenAIEmbeddings

def embed_texts(chunks: list[str]):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    return embeddings.embed_documents(chunks)

