import os
import requests
import json
import numpy as np
import re
from sentence_transformers import SentenceTransformer
from groq import Groq

# -----------------------------
# CONFIG
# -----------------------------
BASE_URL = "http://localhost:8080"
INDEX_NAME = "schemes"
TOP_K = 3

SEARCH_URL = f"{BASE_URL}/api/v1/index/{INDEX_NAME}/search"

# 🔑 Set GROQ_API_KEY in your environment (e.g. in a .env file or shell export)
client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

# -----------------------------
# LOAD EMBEDDING MODEL
# -----------------------------
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# SAFE JSON (handles dirty response)
# -----------------------------
def safe_json(response):
    text = response.text.strip()

    json_objects = re.findall(r'\{.*?\}', text)

    parsed_results = []
    for obj in json_objects:
        try:
            parsed_results.append(json.loads(obj))
        except:
            continue

    if not parsed_results:
        print("❌ No valid JSON found")
        print(text[:300])
        return None

    return parsed_results

# -----------------------------
# SEARCH ENDEE
# -----------------------------
def search_endee(query_embedding):
    payload = {
        "vector": query_embedding,
        "k": TOP_K,
        "include_vectors": False
    }

    try:
        response = requests.post(SEARCH_URL, json=payload, timeout=10)

        print("📡 Status:", response.status_code)

        if response.status_code != 200:
            print("❌ Error:", response.text)
            return []

        data = safe_json(response)

        if not data:
            return []

        results = []

        for item in data:
            if isinstance(item, dict):
                if "matches" in item:
                    results.extend(item["matches"])
                elif "results" in item:
                    results.extend(item["results"])
                elif "text" in item:
                    results.append(item)

        return results

    except Exception as e:
        print("❌ Request failed:", str(e))
        return []

# -----------------------------
# BUILD CONTEXT
# -----------------------------
def build_context(results):
    texts = []

    for r in results:
        try:
            if "text" in r:
                text = r["text"]
            elif "meta" in r:
                meta = json.loads(r["meta"])
                text = meta.get("text", "")
            else:
                continue

            text = text.replace("\u007f", "").replace("\xa0", " ")

            if text:
                texts.append(text)

        except Exception as e:
            print("⚠️ Context error:", e)

    return "\n\n".join(texts[:TOP_K])

# -----------------------------
# GROQ LLM
# -----------------------------
def generate_answer(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are an expert assistant for Indian Government Schemes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("❌ Groq error:", e)
        return "Error generating answer."

# -----------------------------
# MAIN RAG FUNCTION
# -----------------------------
def ask(query):
    print(f"\n🔍 Query: {query}")

    # Step 1: Embed
    embedding = embedder.encode(query)
    embedding = np.array(embedding, dtype=np.float32).tolist()

    print("📏 Embedding dim:", len(embedding))

    # Step 2: Retrieve
    results = search_endee(embedding)

    if not results:
        return "No relevant schemes found."

    # Step 3: Context
    context = build_context(results)

    if not context:
        return "No usable data found."

    # Step 4: Prompt
    prompt = f"""
Answer the question using ONLY the context below.

Context:
{context}

Question:
{query}

Answer clearly:
"""

    # Step 5: Groq LLM
    answer = generate_answer(prompt)

    return answer

# -----------------------------
# RUN LOOP
# -----------------------------
if __name__ == "__main__":
    while True:
        q = input("\nAsk: ").strip()

        if not q:
            continue

        if q.lower() in ["exit", "quit"]:
            break

        answer = ask(q)
        print("\n💡 Answer:", answer)