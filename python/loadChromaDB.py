# index.py
import os
import chromadb
from sentence_transformers import SentenceTransformer

# Load a local embedding model (free, no API needed)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Create a local ChromaDB (stored on disk)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("my_docs")

def chunk_text(text, chunk_size=200, overlap=50):
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def index_file(filepath):
    with open(filepath, "r") as f:
        text = f.read()
    
    chunks = chunk_text(text)
    filename = os.path.basename(filepath)
    
    for i, chunk in enumerate(chunks):
        embedding = embedder.encode(chunk).tolist()
        collection.add(
            ids=[f"{filename}_chunk_{i}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"source": filename}]
        )
        print(f"  Indexed: {filename} chunk {i}")

# Index your files
index_file("C:\\Users\\mbala\\Claude\\data\\company_policy.txt")
index_file("C:\\Users\\mbala\\Claude\\data\\product_faq.txt")
print("Indexing complete!")