import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ===============================
# LOAD PRETRAINED MODEL
# ===============================
model = SentenceTransformer('all-MiniLM-L6-v2')

# ===============================
# LOAD JSON DATA
# ===============================
with open('C:\\Users\\amaya\\PycharmProjects\\AetherAI\\media\\uploaded_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract contents and ids
contents = [item['content'] for item in data]
ids = [item['id'] for item in data]

# ===============================
# CREATE EMBEDDINGS FOR ALL CONTENT
# ===============================
content_embeddings = model.encode(contents)


# ===============================
# SEARCH FUNCTION
# ===============================
def search_query(query, threshold=0.5):
    query_embedding = model.encode([query])

    similarities = cosine_similarity(query_embedding, content_embeddings)[0]

    results = []
    for i, score in enumerate(similarities):
        if score >= threshold:
            results.append((ids[i], contents[i], score))

    # Sort by highest similarity
    results = sorted(results, key=lambda x: x[2], reverse=True)

    return results


# ===============================
# USER INPUT
# ===============================
query = input("Enter keyword or context: ")

results = search_query(query)

if results:
    print("\nRelevant IDs Found:\n")
    for r in results:
        print(f"ID: {r[0]} | Score: {r[2]:.2f}")
        print("Content:", r[1])
        print("-" * 50)
else:
    print("No relevant content found.")