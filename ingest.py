import requests

CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "hagstofa_tables"

TABLES = [
    {
        "id": "VIS01002",
        "title": "Vísitala neysluverðs (Consumer Price Index and Inflation)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Efnahagur/visitolur/1_vnv/1_vnv/VIS01002.px",
        "keywords": "vísitala neysluverðs verðbólga verðlag cpi consumer price index inflation prices month year núna",
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
    {
        "id": "LAU04000",
        "title": "Launavísitala eftir mánuðum frá 1989 (Wage Index and Annual Wage Growth)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Samfelag/launogtekjur/2_lvt/1_manadartolur/LAU04000.px",
        "keywords": "launavísitala laun launahækkanir wage index wages salary earnings kaupmáttur",
    },
    {
        "id": "VIN00001",
        "title": "Vinnumarkaður og atvinnuleysi (Labour Force and Unemployment)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Samfelag/vinnumarkadur/vinnumarkadsrannsokn/1_manadartolur/VIN00001.px",
        "keywords": "atvinnuleysi atvinnulausir vinnuafl starfandi unemployment jobless labour workforce starf vinnumarkaður",
    },
    {
        "id": "SAM02001",
        "title": "Farþegar um Keflavíkurflugvöll og erlendir ferðamenn (Passengers through Keflavík Airport)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Atvinnuvegir/ferdathjonusta/farthegar/1_farthegar/SAM02001.px",
        "keywords": "ferðamenn ferðamanna ferðamennska farþegar flugvöllur keflavíkurflugvöllur tourists passengers airport flights travel",
    },
    {
        "id": "MAN00101",
        "title": "Mannfjöldi eftir kyni og aldri (Population by sex and age)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Ibuar/mannfjoldi/1_yfirlit/Yfirlit_mannfjolda/MAN00101.px",
        "keywords": "mannfjöldi karlar konur kyn population men women sex",
    },
    {
        "id": "MAN05101",
        "title": "Lifandi fæddir eftir aldri móður (Live births)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Ibuar/Faeddirdanir/Faeddir/faedingar/MAN05101.px",
        "keywords": "fæddir fæðingar börn fæddust births born",
    },
    {
        "id": "MAN43000",
        "title": "Mannfjöldi eftir bakgrunni (Population by background, immigrants)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Ibuar/mannfjoldi/3_bakgrunnur/Uppruni/MAN43000.px",
        "keywords": "innflytjendur bakgrunnur immigrants background",
    },
    {
        "id": "THJ01102",
        "title": "Landsframleiðsla og þjóðartekjur (Gross domestic product)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Efnahagur/thjodhagsreikningar/landsframl/1_landsframleidsla/THJ01102.px",
        "keywords": "landsframleiðsla verg landsframleiðsla þjóðartekjur gdp gross domestic product",
    },
    {
        "id": "SAM01601",
        "title": "Gistinætur á öllum tegundum skráðra gististaða (Overnight stays in registered accommodation)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Atvinnuvegir/ferdathjonusta/Gisting/3_allartegundirgististada/SAM01601.px",
        "keywords": "gistinætur gististaðir gestakomur overnight stays accommodation",
    },
    {
        "id": "KOS07112",
        "title": "Úrslit forsetakjörs eftir frambjóðendum og kjördæmum 1952-1996 (Presidential elections)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Ibuar/kosningar/forsetakosningar/KOS07112.px",
        "keywords": "forsetakjör forsetakosningar atkvæði frambjóðendur presidential election votes",
    },
    {
        "id": "VIN00920",
        "title": "Hlutfall og fjöldi atvinnulausra eftir ársfjórðungum (Unemployment by quarter)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Samfelag/vinnumarkadur/vinnumarkadsrannsokn/2_arsfjordungstolur/VIN00920.px",
        "keywords": "atvinnuleysi ársfjórðungur unemployment quarter",
    },
    {
        "id": "SAM03105",
        "title": "Skrásett ökutæki í árslok (Registered motor vehicles at year end)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Umhverfi/5_samgongur/3_okutaekiogvegir/1_okutaeki/SAM03105.px",
        "keywords": "fólksbílar fólksbifreiðar ökutæki bílar passenger cars vehicles",
    },
    {
        "id": "VIS13000",
        "title": "Byggingarvísitala (Building cost index, base 2021=100)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Efnahagur/visitolur/2_byggingarvisitala/byggingarvisitala/VIS13000.px",
        "keywords": "byggingarvísitala vísitala byggingarkostnaðar building cost index",
    },
    {
        "id": "VIS01106",
        "title": "Vísitala markaðsverðs íbúðarhúsnæðis (Residential property market price index)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Efnahagur/visitolur/1_vnv/3_greiningarvisitolur/VIS01106.px",
        "keywords": "íbúðaverð vísitala íbúðaverðs markaðsverð íbúðarhúsnæðis house price index",
    },
    {
        "id": "SJA09005",
        "title": "Afli íslenskra fiskiskipa eftir fisktegundum (Catch of Icelandic vessels by species)",
        "url": "https://px.hagstofa.is/pxis/api/v1/is/Atvinnuvegir/sjavarutvegur/aflatolur/fiskveidisvaedi/SJA09005.px",
        "keywords": "afli fiskiskip veiði þorskur loðna síld catch fish fishing",
    },
]

TABLES_BY_ID = {t["id"]: t for t in TABLES}


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
