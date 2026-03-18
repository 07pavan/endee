import requests
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from PyPDF2 import PdfReader

# -----------------------------
# CONFIG
# -----------------------------
BASE_URL = "http://localhost:8080"
INDEX_NAME = "schemes"
FILE_PATH = "schemes.pdf"   # ⚠️ no trailing space

# -----------------------------
# LOAD MODEL
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# STEP 1: EXTRACT TEXT FROM PDF
# -----------------------------
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""

    for i, page in enumerate(reader.pages):
        content = page.extract_text()
        if content:
            text += content + "\n"

    print(f"📄 Extracted text from {len(reader.pages)} pages")
    return text

# -----------------------------
# STEP 2: CLEAN TEXT
# -----------------------------
def clean_text(text):
    text = text.replace("\n\n", "\n")
    text = text.replace("  ", " ")
    return text.strip()

# -----------------------------
# STEP 3: CHUNK TEXT (BY SCHEME)
# -----------------------------
def chunk_text(text):
    chunks = text.split("Scheme Name:")

    cleaned_chunks = []
    for chunk in chunks:
        chunk = chunk.strip()
        if len(chunk) > 50:  # avoid noise
            cleaned_chunks.append("Scheme Name: " + chunk)

    print(f"🧩 Total chunks created: {len(cleaned_chunks)}")
    return cleaned_chunks

# -----------------------------
# STEP 4: EMBEDDING
# -----------------------------
def get_embedding(text):
    emb = model.encode(text)
    return np.array(emb, dtype=np.float32).tolist()

# -----------------------------
# STEP 5: INGEST INTO ENDEE
# -----------------------------
def ingest(chunks):
    url = f"{BASE_URL}/api/v1/index/{INDEX_NAME}/vector/insert"

    vectors = []

    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)

        if len(embedding) != 384:
            print(f"❌ Skipping chunk {i}, wrong dim")
            continue

        vectors.append({
            "id": str(i),
            "vector": embedding,
            "meta": json.dumps({
                "text": chunk   # 🔥 important
            })
        })

    print(f"📦 Prepared {len(vectors)} vectors")

    response = requests.post(
        url,
        json=vectors,
        headers={"Content-Type": "application/json"}
    )

    print("📡 Status:", response.status_code)
    print("📨 Response:", response.text[:500])


# -----------------------------
# MAIN PIPELINE
# -----------------------------
def main():
    print("🚀 Starting Pipeline...\n")

    # Step 1
    raw_text = extract_text_from_pdf(FILE_PATH)

    # Step 2
    cleaned_text = clean_text(raw_text)

    # Step 3
    chunks = chunk_text(cleaned_text)

    # Step 4 & 5
    ingest(chunks)

    print("\n✅ Pipeline completed successfully!")


if __name__ == "__main__":
    main()