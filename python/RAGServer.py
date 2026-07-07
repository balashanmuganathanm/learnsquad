from typing import Any
import chromadb
from sentence_transformers import SentenceTransformer
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("rag-server")

# Load embedding model and ChromaDB once at startup (shared across all clients)
print("Loading embedding model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

print("Connecting to ChromaDB...")
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("my_docs")

print("RAG MCP server ready.")


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


@mcp.tool()
def index_file(filepath: str) -> str:
    """Index a local text file into the vector database.

    Args:
        filepath: Absolute or relative path to a .txt file to index
    """
    try:
        import os
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        filename = os.path.basename(filepath)
        chunks = chunk_text(text)

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            ids.append(f"{filename}_chunk_{i}")
            embeddings.append(embedder.encode(chunk).tolist())
            documents.append(chunk)
            metadatas.append({"source": filename, "filepath": filepath})

        # Upsert so re-indexing the same file doesn't duplicate
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        return f"Indexed '{filename}' — {len(chunks)} chunks stored in vector DB."

    except FileNotFoundError:
        return f"Error: File not found at '{filepath}'"
    except Exception as e:
        return f"Error indexing file: {str(e)}"


@mcp.tool()
def search_documents(query: str, top_k: int = 3) -> str:
    """Search the vector database for chunks relevant to a query.

    Args:
        query: The search query or question
        top_k: Number of most relevant chunks to return (default 3)
    """
    try:
        if collection.count() == 0:
            return "Vector DB is empty. Please index some files first using index_file."

        query_vector = embedder.encode(query).tolist()

        results = collection.query(
            query_embeddings=[query_vector],
            n_results=min(top_k, collection.count())
        )

        chunks = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        output = []
        for i, (chunk, meta, dist) in enumerate(zip(chunks, metadatas, distances)):
            relevance = round((1 - dist) * 100, 1)
            output.append(
                f"[Result {i+1} | Source: {meta['source']} | Relevance: {relevance}%]\n{chunk}"
            )

        return "\n\n---\n\n".join(output)

    except Exception as e:
        return f"Error searching documents: {str(e)}"


@mcp.tool()
def list_indexed_sources() -> str:
    """List all files currently indexed in the vector database."""
    try:
        if collection.count() == 0:
            return "Vector DB is empty. No files indexed yet."

        all_items = collection.get(include=["metadatas"])
        sources = {}
        for meta in all_items["metadatas"]:
            src = meta.get("source", "unknown")
            sources[src] = sources.get(src, 0) + 1

        lines = [f"  - {src} ({count} chunks)" for src, count in sorted(sources.items())]
        return f"Indexed sources ({len(sources)} files):\n" + "\n".join(lines)

    except Exception as e:
        return f"Error listing sources: {str(e)}"


@mcp.tool()
def delete_source(filename: str) -> str:
    """Remove a previously indexed file from the vector database.

    Args:
        filename: The filename (not full path) to remove, e.g. 'policy.txt'
    """
    try:
        all_items = collection.get(include=["metadatas"])
        ids_to_delete = [
            id_ for id_, meta in zip(all_items["ids"], all_items["metadatas"])
            if meta.get("source") == filename
        ]

        if not ids_to_delete:
            return f"No indexed chunks found for '{filename}'."

        collection.delete(ids=ids_to_delete)
        return f"Deleted {len(ids_to_delete)} chunks for '{filename}' from vector DB."

    except Exception as e:
        return f"Error deleting source: {str(e)}"


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()