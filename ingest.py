import requests

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "hagstofa_tables"

TABLES = [
    {
        "id": "VIS01002",
        "title": "Vísitala neysluverðs (Consumer Price Index and Inflation)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Efnahagur/visitolur/1_vnv/1_vnv/VIS01002.px",
        "keywords": "vísitala neysluverðs verðbólga verðlag cpi consumer price index inflation prices month year",
    },
    {
        "id": "MAN00000",
        "title": "Lykiltölur mannfjöldans 1703-2026 (Key Population Figures of Iceland)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Ibuar/mannfjoldi/1_yfirlit/Yfirlit_mannfjolda/MAN00000.px",
        "keywords": "mannfjöldi íbúar landsmenn population iceland total inhabitants fjölgun fæddir dánir",
    },
    {
        "id": "MAN01002",
        "title": "Búferlaflutningar milli landsvæða eftir kyni og aldri (Internal Migration Between Regions)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Ibuar/buferlaflutningar/buferlaflinnanlands/buferlaflinnanlands/MAN01002.px",
        "keywords": "búferlaflutningar flutningar fluttu aðfluttir brottfluttir landshlutar svæði migration moved regions",
    },
    {
        "id": "MAN02005",
        "title": "Mannfjöldi eftir kyni, aldri og sveitarfélögum (Population by Municipality, Sex and Age)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Ibuar/mannfjoldi/2_byggdir/sveitarfelog/MAN02005.px",
        "keywords": "sveitarfélög sveitarfélag bæjarfélög reykjavík kópavogur hafnarfjörður akureyri garðabær mosfellsbær keflavík reykjanesbær selfoss akranes vestmannaeyjar íbúafjöldi municipality town city population",
    },
    {
        "id": "MAN03270",
        "title": "Mannfjöldi eftir hverfum í Reykjavík, kyni og aldri (Population in Reykjavík by Districts)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Ibuar/mannfjoldi/2_byggdir/Byggdakjarnarhverfi/MAN03270.px",
        "keywords": "hverfi í reykjavík vesturbær miðborg hlíðar laugardalur háaleiti bústaðir breiðholt árbær grafarvogur kjalarness grafarholt úlfarsárdalur districts neighborhoods reykjavik",
    },
]


def fetch_table_metadata(table: dict) -> str:
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(table["url"], headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            title = data.get("title", table["title"])
            vars_text = []
            for v in data.get("variables", []):
                v_name = v.get("text", v.get("code", ""))
                sample_vals = ", ".join(v.get("valueTexts", [])[:15])
                vars_text.append(f"{v_name}: {sample_vals}")
            variables_str = " | ".join(vars_text)
            return f"Table {table['id']}: {title}. Keywords: {table['keywords']}. Variables: {variables_str}"
    except Exception as e:
        print(f"Could not fetch live metadata for {table['id']}: {e}")

    return f"Table {table['id']}: {table['title']}. Keywords: {table['keywords']}"


def run_ingestion():
    import chromadb
    from sentence_transformers import SentenceTransformer

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    documents = []
    ids = []
    metadatas = []

    for table in TABLES:
        print(f"Fetching metadata for {table['id']}...")
        doc_text = fetch_table_metadata(table)
        documents.append(doc_text)
        ids.append(table["id"])
        metadatas.append({
            "id": table["id"],
            "title": table["title"],
            "url": table["url"],
            "keywords": table["keywords"],
        })

    print("Generating embeddings...")
    embeddings = model.encode(documents).tolist()

    collection.upsert(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids,
    )
    print(f"Stored {len(ids)} tables in {CHROMA_DIR}.")


if __name__ == "__main__":
    run_ingestion()
