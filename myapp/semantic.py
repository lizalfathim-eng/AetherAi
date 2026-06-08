import json
import numpy as np
import faiss
import re
import os
import pickle
from sentence_transformers import SentenceTransformer

# ======================================================
# SETTINGS
# ======================================================
JSON_PATH = r"C:\AetherAI\AetherAI\media\uploaded_data.json"
# JSON_PATH = r"C:\Users\jishn\Downloads\Telegram Desktop\uploaded_data.json"
INDEX_PATH = "legal_index.faiss"
METADATA_PATH = "metadata.pkl"
PROCESSED_IDS_PATH = "processed_ids.pkl"

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"  # Faster & efficient

# ======================================================
# LOAD MODEL
# ======================================================
print("Loading model...")
model = SentenceTransformer(MODEL_NAME)

# ======================================================
# LOAD JSON
# ======================================================
print("Loading JSON...")
with open(JSON_PATH, "r", encoding="utf-8") as f:
    documents = json.load(f)

# ======================================================
# CLEAN FUNCTION
# ======================================================
def is_valid_document(doc):
    text = doc.get("content", "").strip()

    if (
        len(text) < 100 or
        "Text extraction not implemented" in text
    ):
        return False

    return True


# ======================================================
# LEGAL CHUNKING (PARAGRAPH BASED)
# ======================================================
def chunk_legal_text(text, min_words=40):
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if len(p.split()) >= min_words]


# ======================================================
# INITIALIZE OR LOAD EXISTING SYSTEM
# ======================================================
if os.path.exists(INDEX_PATH):

    print("Loading existing FAISS index...")
    index = faiss.read_index(INDEX_PATH)

    with open(METADATA_PATH, "rb") as f:
        metadata = pickle.load(f)

    with open(PROCESSED_IDS_PATH, "rb") as f:
        processed_ids = pickle.load(f)

else:
    print("Creating new FAISS index...")
    metadata = []
    processed_ids = set()

    # Prepare initial data
    all_chunks = []

    for doc in documents:
        if not is_valid_document(doc):
            continue

        chunks = chunk_legal_text(doc["content"])

        for chunk in chunks:
            all_chunks.append(chunk)
            metadata.append({
                "doc_id": doc["id"],
                "date": doc.get("date", ""),
                "staff": doc.get("staff", ""),
                "text": chunk
            })

        processed_ids.add(doc["id"])

    print("Generating initial embeddings...")
    embeddings = model.encode(
        all_chunks,
        batch_size=128,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    embeddings = embeddings / np.linalg.norm(
        embeddings, axis=1, keepdims=True
    )

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    faiss.write_index(index, INDEX_PATH)

    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    with open(PROCESSED_IDS_PATH, "wb") as f:
        pickle.dump(processed_ids, f)

    print("Initial index created successfully.")


# ======================================================
# DAILY UPDATE — ADD ONLY NEW DOCUMENTS
# ======================================================
print("Checking for new documents...")

new_documents = [
    doc for doc in documents
    if doc["id"] not in processed_ids and is_valid_document(doc)
]

print("New documents found:", len(new_documents))

if len(new_documents) > 0:

    new_chunks = []
    new_metadata = []

    for doc in new_documents:
        chunks = chunk_legal_text(doc["content"])

        for chunk in chunks:
            new_chunks.append(chunk)
            new_metadata.append({
                "doc_id": doc["id"],
                "date": doc.get("date", ""),
                "staff": doc.get("staff", ""),
                "text": chunk
            })

        processed_ids.add(doc["id"])

    print("Generating embeddings for new documents...")

    new_embeddings = model.encode(
        new_chunks,
        batch_size=128,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    new_embeddings = new_embeddings / np.linalg.norm(
        new_embeddings, axis=1, keepdims=True
    )

    index.add(new_embeddings)
    metadata.extend(new_metadata)

    faiss.write_index(index, INDEX_PATH)

    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    with open(PROCESSED_IDS_PATH, "wb") as f:
        pickle.dump(processed_ids, f)

    print("Daily update completed successfully.")

else:
    print("No new documents to update.")


# ======================================================
# LEGAL SEARCH FUNCTION
# ======================================================
def legal_search(query, top_k=5):

    query_embedding = model.encode([query])
    query_embedding = query_embedding / np.linalg.norm(query_embedding)

    distances, indices = index.search(
        np.array(query_embedding),
        top_k * 3
    )

    seen = set()
    results = []

    for score, idx in zip(distances[0], indices[0]):

        if idx >= len(metadata):
            continue

        data = metadata[idx]

        if data["text"] in seen:
            continue

        seen.add(data["text"])

        # Keyword Boost
        boost = 0.1 if query.lower() in data["text"].lower() else 0.0

        results.append({
            "score": round(float(score + boost), 4),
            "doc_id": data["doc_id"],
            "date": data["date"],
            "staff": data["staff"],
            "snippet": data["text"][:600]
        })

        if len(results) == top_k:
            break

    return results


# ======================================================
# INTERACTIVE SEARCH
# ======================================================
print("\n⚖️ Legal Search Ready")
print("Type 'exit' to stop.\n")

while True:
    query = input("Enter legal query: ")

    if query.lower() == "exit":
        break

    results = legal_search(query)

    print("\nRESULTS:\n")

    for r in results:
        print("Score:", r["score"])
        print("Doc ID:", r["doc_id"])
        print("Date:", r["date"])
        print("Staff:", r["staff"])
        print("Snippet:\n", r["snippet"])
        print("=" * 80)