import chromadb
from sentence_transformers import SentenceTransformer

# Load a small, fast, free embedding model (384-dim vectors)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="./chroma_db")  # saved to disk

def get_or_create_collection(name: str = "documents"):
    return client.get_or_create_collection(name=name)

def index_chunks(chunks: list[dict], collection_name: str = "documents"):
    collection = get_or_create_collection(collection_name)

    texts = [c["text"] for c in chunks]
    ids = [f"chunk_{c['chunk_id']}" for c in chunks]
    metadatas = [{"page": c["page"]} for c in chunks]

    # Embed all chunks in one batch (fast)
    embeddings = embedder.encode(texts).tolist()

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )
    print(f"Indexed {len(chunks)} chunks into '{collection_name}'.")

def retrieve(query: str, top_k: int = 4, collection_name: str = "documents") -> list[dict]:
    collection = get_or_create_collection(collection_name)
    query_embedding = embedder.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
    )

    hits = []
    for i in range(len(results["documents"][0])):
        hits.append({
            "text": results["documents"][0][i],
            "page": results["metadatas"][0][i]["page"],
            "distance": results["distances"][0][i],
        })
    return hits