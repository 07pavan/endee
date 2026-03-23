# 🏛️ Govt Scheme Copilot

An AI-powered **Retrieval-Augmented Generation (RAG)** copilot that answers questions about Indian Government Schemes.  
It uses **Endee** (an open-source vector database) for fast semantic retrieval and **Groq's Llama 3.1** for natural language answer generation.

---

## 📖 Project Overview

Government scheme documents are often long, dense PDFs that are hard for citizens to navigate. **Govt Scheme Copilot** solves this by:

1. **Extracting** text from the source PDF (`schemes.pdf`).
2. **Chunking** the text by individual scheme boundaries.
3. **Embedding** each chunk into a 384-dimensional vector using the `all-MiniLM-L6-v2` sentence-transformer model.
4. **Storing** the vectors (with full-text metadata) in a local **Endee** vector database.
5. **Retrieving** the top-k most relevant chunks for any user question via cosine similarity search.
6. **Generating** a clear, context-grounded answer using the **Groq LLM API** (Llama 3.1 8B Instant).

The result is an interactive **command-line copilot** — type a question and get an accurate, sourced answer in seconds.

---

## 🏗️ System Design

Below is the end-to-end architecture of the RAG pipeline:

```
                        ┌─────────────────────────────────┐
                        │         schemes.pdf             │
                        │   (Source Government Schemes)   │
                        └──────────────┬──────────────────┘
                                       │
                          ┌────────────▼────────────┐
                          │      ingest.py          │
                          │  1. Extract text (PDF)  │
                          │  2. Clean & chunk       │
                          │  3. Embed (MiniLM-L6)   │
                          │  4. Upload to Endee     │
                          └────────────┬────────────┘
                                       │
                                       ▼
                        ┌──────────────────────────┐
                        │     Endee Vector DB      │
                        │   (localhost:8080)        │
                        │   Index: "schemes"        │
                        │   Dim: 384 | Cosine       │
                        └──────────────┬───────────┘
                                       │
            User Query                 │  Top-K Results
                │                      │       │
       ┌────────▼────────┐             │  ┌────▼──────────┐
       │    query.py     │─── search ──┘  │ Build Context │
       │  Embed query    │                │ from metadata │
       │  (MiniLM-L6)   │                └────┬──────────┘
       └─────────────────┘                     │
                                               ▼
                                  ┌─────────────────────────┐
                                  │     Groq LLM API        │
                                  │  (llama-3.1-8b-instant) │
                                  │  Prompt = Context +     │
                                  │          Question        │
                                  └────────────┬────────────┘
                                               │
                                               ▼
                                        💡 Final Answer
```

### Pipeline Stages

| Stage            | Script            | Description                                                                                  |
|------------------|-------------------|----------------------------------------------------------------------------------------------|
| **Index Setup**  | `create_index.py` | Deletes any existing `schemes` index and creates a fresh one (384-dim, cosine distance).     |
| **Ingestion**    | `ingest.py`       | Reads the PDF → cleans text → splits by "Scheme Name:" → embeds → uploads vectors to Endee. |
| **Query / RAG**  | `query.py`        | Embeds the user question → retrieves top-3 matches from Endee → sends context to Groq LLM.  |

---

## 🗄️ Use of Endee

[**Endee**](https://github.com/endee-io/endee) is a high-performance open-source vector database built in C++ for AI search and retrieval workloads. This project uses Endee as the **vector storage and retrieval engine** in the RAG pipeline.

### Why Endee?

- **Purpose-built for RAG** — optimized for fast nearest-neighbor search at low latency.
- **Simple HTTP API** — no SDK required; plain `requests.post()` calls from Python.
- **Lightweight deployment** — runs locally via Docker on port `8080` with persistent volume storage.
- **Metadata support** — each vector stores a JSON `meta` field containing the original chunk text, enabling easy context reconstruction.

### Endee API Endpoints Used

| Operation       | Method   | Endpoint                                      | Purpose                          |
|-----------------|----------|-----------------------------------------------|----------------------------------|
| Delete Index    | `DELETE` | `/api/v1/index/{name}/delete`                 | Remove stale index before re-run |
| Create Index    | `POST`   | `/api/v1/index/create`                        | Create index with dim & distance |
| Insert Vectors  | `POST`   | `/api/v1/index/{name}/vector/insert`          | Ingest embedded chunks           |
| Search Vectors  | `POST`   | `/api/v1/index/{name}/search`                 | Retrieve top-K nearest vectors   |

### Index Configuration

```json
{
  "index_name": "schemes",
  "dim": 384,
  "space_type": "cosine"
}
```

---

## 📂 File Structure

```
Govt_Scheme_Copilot/
├── create_index.py     # Creates the Endee vector index (384-dim, cosine)
├── ingest.py           # PDF → text → chunks → embeddings → Endee
├── query.py            # Interactive RAG: embed query → search Endee → Groq LLM → answer
├── schemes.pdf         # Source PDF with government scheme data
├── test.ipynb          # Jupyter notebook for PDF extraction prototyping
├── README.md           # This file
└── venv/               # Python virtual environment (not tracked in Git)
```

---

## 🚀 Setup Instructions

### Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose** (to run Endee)
- A **Groq API Key** — get one free at [console.groq.com](https://console.groq.com)

### Step 1 — Start Endee

From the **parent repo root** (`endee/`), launch the Endee vector database:

```bash
docker compose up -d
```

This builds and starts the `endee-oss` container on **port 8080** with persistent volume storage.

Verify it's running:

```bash
curl http://localhost:8080/health
```

### Step 2 — Set Up the Python Environment

```bash
cd Govt_Scheme_Copilot

# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# Install dependencies
pip install requests numpy sentence-transformers PyPDF2 groq
```

### Step 3 — Set Your Groq API Key

```bash
# Linux / macOS
export GROQ_API_KEY="your-groq-api-key-here"

# Windows (PowerShell)
$env:GROQ_API_KEY = "your-groq-api-key-here"
```

### Step 4 — Create the Vector Index

```bash
python create_index.py
```

Expected output:
```
🗑️ Deleting old index...
🆕 Creating new index...
Create Status: 200
```

### Step 5 — Ingest the Schemes PDF

```bash
python ingest.py
```

Expected output:
```
🚀 Starting Pipeline...
📄 Extracted text from N pages
🧩 Total chunks created: N
📦 Prepared N vectors
📡 Status: 200
✅ Pipeline completed successfully!
```

### Step 6 — Ask Questions!

```bash
python query.py
```

```
Ask: What is PM Kisan Yojana?

🔍 Query: What is PM Kisan Yojana?
📏 Embedding dim: 384
📡 Status: 200

💡 Answer: PM Kisan Yojana is a central government scheme that provides ...
```

Type `exit` or `quit` to stop the copilot.
DEMO LINK: https://drive.google.com/file/d/1ijvvQ4gIF61rBF04y2Y2BJokSVAStq8o/view?usp=sharing
---

## 🔧 Configuration

Key parameters can be adjusted in the scripts:

| Parameter      | File       | Default                  | Description                              |
|----------------|------------|--------------------------|------------------------------------------|
| `BASE_URL`     | All        | `http://localhost:8080`  | Endee server address                     |
| `INDEX_NAME`   | All        | `schemes`                | Name of the vector index                 |
| `TOP_K`        | `query.py` | `3`                      | Number of retrieved chunks per query     |
| `model`        | `query.py` | `llama-3.1-8b-instant`   | Groq model for answer generation         |
| `temperature`  | `query.py` | `0.3`                    | LLM creativity (lower = more factual)    |

---

## 📝 License

This project is part of the [Endee](https://github.com/07pavan/endee) repository, licensed under the **Apache License 2.0**.
