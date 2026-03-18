import requests

BASE_URL = "http://localhost:8080"
INDEX_NAME = "schemes"

# Create URL
create_url = f"{BASE_URL}/api/v1/index/create"
delete_url = f"{BASE_URL}/api/v1/index/{INDEX_NAME}/delete"

payload = {
    "index_name": INDEX_NAME,
    "dim": 384,
    "space_type": "cosine"
}

# -----------------------------
# STEP 1: Delete old index
# -----------------------------
print("🗑️ Deleting old index...")
del_res = requests.delete(delete_url)
print("Delete Status:", del_res.status_code)

# -----------------------------
# STEP 2: Create new index
# -----------------------------
print("🆕 Creating new index...")
res = requests.post(create_url, json=payload)
print("Create Status:", res.status_code)
print("Response:", res.text)