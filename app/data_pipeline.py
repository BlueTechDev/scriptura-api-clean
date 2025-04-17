import os
import json
import faiss
import numpy as np
import logging
from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Config
MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 32
INPUT_PATH = "app/data/embedded_data/structured_wels_content.jsonl"
OUTPUT_PATH = "app/data/embedded_data/embedded_data.jsonl"
FAISS_INDEX_PATH = "app/data/embedded_data/faiss_index.idx"

# Setup
os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
logging.basicConfig(level=logging.INFO)

def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def save_jsonl(data, path):
    with open(path, "w", encoding="utf-8") as f:
        for entry in data:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")

def generate_embeddings(model, texts):
    embeddings = []
    for i in tqdm(range(0, len(texts), BATCH_SIZE), desc="Embedding batches"):
        batch = texts[i:i + BATCH_SIZE]
        emb = model.encode(batch, convert_to_numpy=True)
        embeddings.extend(emb)
    return np.array(embeddings, dtype="float32")

def run_pipeline():
    data = load_jsonl(INPUT_PATH)
    texts = [entry["content"] for entry in data if "content" in entry and entry["content"].strip()]

    logging.info(f"📚 Loaded {len(texts)} entries to embed.")

    model = SentenceTransformer(MODEL_NAME)
    embeddings = generate_embeddings(model, texts)

    for i, entry in enumerate(data):
        if i < len(embeddings):
            entry["embedding"] = embeddings[i].tolist()

    save_jsonl(data, OUTPUT_PATH)
    logging.info(f"✅ Saved embedded data to {OUTPUT_PATH}")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, FAISS_INDEX_PATH)
    logging.info(f"✅ FAISS index saved to {FAISS_INDEX_PATH}")

if __name__ == "__main__":
    run_pipeline()
    logging.info("🚀 Data pipeline completed successfully.")
