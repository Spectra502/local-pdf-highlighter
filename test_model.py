from sentence_transformers import SentenceTransformer
import time

t0 = time.time()
print("Loading model...")
model = SentenceTransformer("google/embeddinggemma-2", device="cpu", truncate_dim=256)
t1 = time.time()
print(f"Model loaded in {t1-t0:.2f}s")

texts = ["Hello world", "This is a test"]
embeddings = model.encode(texts, normalize_embeddings=True)
print(embeddings.shape)
