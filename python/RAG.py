# query.py
import chromadb
from anthropic import Anthropic
from sentence_transformers import SentenceTransformer
import dotenv,os


dotenv.load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

embedder = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection("my_docs")
anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

def query_rag(user_question: str, top_k: int = 3):
    # Step 1: Embed the user's question
    query_vector = embedder.encode(user_question).tolist()
    
    # Step 2: Retrieve top-K similar chunks from ChromaDB
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k
    )
    
    retrieved_chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    
    print(f"\nRetrieved {len(retrieved_chunks)} chunks from: {set(sources)}")
    
    # Step 3: Build prompt with retrieved context injected
    context = "\n\n".join(
        f"[Source: {src}]\n{chunk}"
        for chunk, src in zip(retrieved_chunks, sources)
    )
    
    prompt = f"""Answer the question using ONLY the context below.
If the answer isn't in the context, say "I don't have that information."

Context:
{context}

Question: {user_question}"""
    
    # Step 4: Send to Claude
    response = anthropic.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text

# Try it out
questions = [
    "How many vacation days do employees get?",
    "What does the premium plan cost?",
    "Is remote work allowed?",
    "Can I take loan?"
]

for q in questions:
    print(f"\nQ: {q}")
    print(f"A: {query_rag(q)}")