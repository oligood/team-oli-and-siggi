import os
import unicodedata
from ingest import CHROMA_DIR, COLLECTION_NAME, TABLES

_model = None
_collection = None


def normalize(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", str(text))
    flat = "".join([c for c in nfkd if not unicodedata.combining(c)]).lower()
    for k, v in {"þ": "th", "æ": "ae", "ö": "o", "ð": "d"}.items():
        flat = flat.replace(k, v)
    return flat


def _get_collection():
    global _model, _collection
    if _collection is None and os.path.exists(CHROMA_DIR):
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer

            client = chromadb.PersistentClient(path=CHROMA_DIR)
            _collection = client.get_collection(name=COLLECTION_NAME)
            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _collection = None
    return _collection, _model


def find_best_table(question: str) -> dict:
    q = normalize(question)

    # Direct topic checks for unambiguous terms
    if any(w in q for w in ["visitala", "neysluverd", "verdbolg", "cpi", "inflation", "price index"]):
        return TABLES[0]

    if any(w in q for w in ["flutt", "buferla", "migration", "moved", "landshlut", "landsfjord"]):
        return TABLES[2]

    if any(w in q for w in ["hverfi", "vesturba", "midborg", "hlid", "laugardal", "breidholt", "grafarvog", "arba", "haaleit", "district", "neighborhood"]):
        return TABLES[4]

    if any(w in q for w in [
        "sveitarfel", "reykjavik", "kopavog", "hafnarfjord", "hafnarfird", "akureyr",
        "gardaba", "mosfellsba", "reykjanesba", "keflavik", "selfoss", "akranes",
        "vestmannaey", "borgarbyggd", "grindavik", "husavik", "municipality",
    ]):
        return TABLES[3]

    if any(w in q for w in ["mannfjold", "ibua", "population", "inhabitants", "how many people", "hve margir bua"]):
        return TABLES[1]

    # Vector search in ChromaDB
    collection, model = _get_collection()
    if collection is not None and model is not None:
        try:
            emb = model.encode([question]).tolist()
            results = collection.query(query_embeddings=emb, n_results=1)
            metas = results.get("metadatas", [[]])[0]
            if metas:
                return metas[0]
        except Exception:
            pass

    return TABLES[1]


if __name__ == "__main__":
    test_questions = [
        "Hver var verðbólgan í júní 2024?",
        "Hvað búa margir í Kópavogi?",
        "Hvað fluttu margir til höfuðborgarsvæðisins árið 2024?",
        "Hvað búa margir í Vesturbæ í Reykjavík?",
        "Hver er mannfjöldi á Íslandi?",
    ]
    for tq in test_questions:
        match = find_best_table(tq)
        print(f"Q: {tq}\n -> {match['id']} ({match['title']})")
