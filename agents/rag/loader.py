from langchain.text_splitter import CharacterTextSplitter

def load_and_split(filepath: str, chunk_size: int = 500, chunk_overlap: int = 50):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    splitter = CharacterTextSplitter(
        separator="\n\n",  # Split by paragraphs (you can change this)
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = splitter.split_text(text)
    return chunks
