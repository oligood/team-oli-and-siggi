import os
import re
import unicodedata
from ingest import CHROMA_DIR, COLLECTION_NAME, TABLES

_model = None
_collection = None

# Spurningar sem heyra undir aðrar stofnanir (Veðurstofan, Seðlabankinn, HMS/Þjóðskrá).
# Athugað fyrst, svo bæjarheiti í spurningunni dragi hana ekki í mannfjöldatöflu.
OUT_OF_SCOPE_PATTERNS = [
    r"\bvedur", r"\bvedri", r"\bhiti\b", r"\bhitinn\b", r"\bhitastig", r"\brign", r"\bsnjo",
    r"\bstyrivext", r"\bstyrivaxt", r"\bvextir\b", r"\bvexti\b", r"\bsedlabank",
    r"\bfasteignamat", r"\bfasteignaverd", r"\bibudaverd",
    r"\bweather\b", r"\btemperature\b", r"\binterest rate", r"\bcentral bank", r"\bproperty value", r"\bhouse price",
]

# Gömul, sameinuð eða óformleg staðarheiti -> sveitarfélag eins og það heitir í MAN02005.
# Lyklar eru regex á normaliseraðan texta; \b fremst svo t.d. "vogar" grípi ekki "Kópavogur".
MUNICIPALITY_ALIASES = {
    r"\bseydis(fj|fir)": "Múlaþing", r"\begilsstad": "Múlaþing", r"\bdjupavog": "Múlaþing",
    r"\bdjupivog": "Múlaþing", r"\bborgar(fj|fir)\w* eystr": "Múlaþing", r"\bfljotsdalsherad": "Múlaþing",
    r"\bmulathing": "Múlaþing",
    r"\bsandgerd": "Suðurnesjabær", r"\bgard(ur|i|s)\b": "Suðurnesjabær", r"\bsudurnesjab": "Suðurnesjabær",
    r"\bkeflavik(?!urflugv)": "Reykjanesbær", r"\bnjardvik": "Reykjanesbær", r"\breykjanesb": "Reykjanesbær",
    r"\bgrindavik": "Grindavíkurbær", r"\bvog(ar|um)\b": "Sveitarfélagið Vogar",
    r"\bkopavog": "Kópavogsbær", r"\bhafnar(fj|fir)": "Hafnarfjarðarkaupstaður",
    r"\bgardab": "Garðabær", r"\bmosfellsb": "Mosfellsbær", r"\bseltjarnarnes": "Seltjarnarnesbær",
    r"\bakranes": "Akraneskaupstaður", r"\bborgarnes": "Borgarbyggð", r"\bborgarbyggd": "Borgarbyggð",
    r"\bstykkisholm": "Sveitarfélagið Stykkishólmur", r"\bolafsvik": "Snæfellsbær", r"\bhellissand": "Snæfellsbær",
    r"\bisa(fj|fir)": "Ísafjarðarbær", r"\bflateyr": "Ísafjarðarbær", r"\bthingeyr": "Ísafjarðarbær", r"\bsudureyr": "Ísafjarðarbær",
    r"\bpatreks(fj|fir)": "Vesturbyggð", r"\bbildudal": "Vesturbyggð", r"\btalkna(fj|fir)": "Vesturbyggð",
    r"\bblonduos": "Húnabyggð", r"\bsaudarkrok": "Skagafjörður", r"\bsiglu(fj|fir)": "Fjallabyggð", r"\bolafs(fj|fir)": "Fjallabyggð",
    r"\bakureyr": "Akureyrarbær", r"\bdalvik": "Dalvíkurbyggð",
    r"\bhusavik": "Norðurþing", r"\braufarhofn": "Norðurþing", r"\bkopasker": "Norðurþing",
    r"\breydar(fj|fir)": "Fjarðabyggð", r"\beski(fj|fir)": "Fjarðabyggð", r"\bneskaupstad": "Fjarðabyggð",
    r"\bfaskruds(fj|fir)": "Fjarðabyggð", r"\bstodvar(fj|fir)": "Fjarðabyggð", r"\bbreiddalsvik": "Fjarðabyggð",
    r"\bhorna(fj|fir)": "Sveitarfélagið Hornafjörður", r"\bvestmannaey": "Vestmannaeyjabær",
    r"\bselfoss": "Sveitarfélagið Árborg", r"\beyrarbakk": "Sveitarfélagið Árborg", r"\bstokkseyr": "Sveitarfélagið Árborg",
    r"\bhveragerd": "Hveragerðisbær", r"\bthorlakshofn": "Sveitarfélagið Ölfus",
    r"\bhvolsvoll": "Rangárþing eystra", r"\bhella\b": "Rangárþing ytra",
}

# "Reykjavík í heild, ekki bara Breiðholt" á að fara í sveitarfélagatöfluna, ekki hverfatöfluna
REYKJAVIK_WHOLE_PATTERNS = [r"\bi heild\b", r"\bekki bara\b", r"\bekki adeins\b", r"\ballri reykjavik", r"\breykjavik alls\b"]

POPULATION_WORDS = ["bua", "ibua", "mannfjold", "population", "inhabitants", "live in"]


# Lyklar sem eru heiti sveitarfélagsins sjálfs. Allir aðrir lyklar eru bæir eða eldri sveitarfélög
# sem eru aðeins hluti af stærra sveitarfélagi, og Hagstofan birtir ekki sér tölur fyrir þá í MAN02005.
CURRENT_MUNICIPALITY_PATTERNS = {
    r"\bmulathing", r"\bsudurnesjab", r"\breykjanesb", r"\bgrindavik", r"\bvog(ar|um)\b", r"\bkopavog",
    r"\bhafnar(fj|fir)", r"\bgardab", r"\bmosfellsb", r"\bseltjarnarnes", r"\bakranes", r"\bborgarbyggd",
    r"\bisa(fj|fir)", r"\bakureyr", r"\bdalvik", r"\bhorna(fj|fir)", r"\bvestmannaey", r"\bhveragerd",
}


def resolve_municipality(normalized_question: str) -> str | None:
    """Skilar heiti sveitarfélags í MAN02005 ef spurningin nefnir þekkt (gamalt eða nýtt) staðarheiti."""
    for pattern, name in MUNICIPALITY_ALIASES.items():
        if re.search(pattern, normalized_question):
            return name
    return None


def is_part_of_larger_municipality(normalized_question: str) -> bool:
    """True ef spurt er um bæ eða eldra sveitarfélag (t.d. Seyðisfjörð) sem tölur eru ekki birtar sér fyrir."""
    for pattern in MUNICIPALITY_ALIASES:
        if re.search(pattern, normalized_question):
            return pattern not in CURRENT_MUNICIPALITY_PATTERNS
    return False


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

    # 0. Out of scope (weather, interest rates, property valuation) - reject before place names are seen
    if any(re.search(p, q) for p in OUT_OF_SCOPE_PATTERNS):
        return None

    # 1. Wage Index (check before generic 'visitala')
    if any(w in q for w in ["launavisital", "laun", "wage", "salary", "earnings", "kaupmatt"]):
        return TABLES[5]

    # 2. Inflation and Consumer Price Index (VIS01002)
    if any(w in q for w in ["visitala", "neysluverd", "verdbolg", "cpi", "inflation", "price index"]):
        return TABLES[0]

    # 3. Unemployment & Labor Market (VIN00001)
    if any(w in q for w in ["atvinnuleys", "atvinnulaus", "unemployment", "jobless", "vinnuafl", "vinnumarkad"]):
        return TABLES[6]

    # 4. Tourism and Passengers (SAM02001)
    # Plain "Keflavík" in a population question means the town (Reykjanesbær), not the airport
    asks_population = any(w in q for w in POPULATION_WORDS)
    if any(w in q for w in ["ferdamenn", "ferdamann", "fartheg", "keflavikurflugv", "flugvoll", "tourist", "passenger", "airport"]):
        return TABLES[7]
    if "keflavik" in q and not asks_population:
        return TABLES[7]

    # 5. Internal Migration (MAN01002)
    if any(w in q for w in ["flutt", "buferla", "migration", "moved", "landshlut", "landsfjord"]):
        return TABLES[2]

    # 6a. Reykjavík as a whole, explicitly not one district (MAN02005)
    if "reykjavik" in q and any(re.search(p, q) for p in REYKJAVIK_WHOLE_PATTERNS):
        return TABLES[3]

    # 6b. Old, merged or informal place names (Seyðisfjörður -> Múlaþing, Garður -> Suðurnesjabær, ...)
    if resolve_municipality(q):
        return TABLES[3]

    # 6c. Reykjavík Districts (MAN03270) - word-start match so e.g. "Varmahlíð" doesn't hit "hlid"
    district_words = [
        "hverfi", "vesturba", "midborg", "hlid", "laugardal", "breidholt", "grafarvog", "grafarholt",
        "ulfarsardal", "kjalarnes", "arba", "haaleit", "bustad", "district", "neighborhood",
    ]
    if any(re.search(r"\b" + w, q) for w in district_words):
        return TABLES[4]

    # 7. Municipalities (MAN02005)
    if any(w in q for w in [
        "sveitarfel", "reykjavik", "kopavog", "hafnarfjord", "hafnarfird", "akureyr",
        "gardaba", "mosfellsba", "reykjanesba", "keflavikurb", "selfoss", "akranes",
        "vestmannaey", "borgarbyggd", "grindavik", "husavik", "municipality", "kaupstad",
    ]):
        return TABLES[3]

    # 8. Total Population of Iceland (MAN00000)
    if any(w in q for w in [
        "mannfjold", "ibua", "population", "inhabitants", "landsmenn",
        "how many people", "bua margir", "margir bua", "hve margir", "hvad bua"
    ]):
        return TABLES[1]

    # Vector search in ChromaDB (if available)
    collection, model = _get_collection()
    if collection is not None and model is not None:
        try:
            emb = model.encode([question]).tolist()
            results = collection.query(query_embeddings=emb, n_results=1)
            metas = results.get("metadatas", [[]])[0]
            dists = results.get("distances", [[]])[0]
            # Only accept high-confidence vector matches
            if metas and (not dists or dists[0] < 1.2):
                return metas[0]
        except Exception:
            pass

    # No match found - do NOT hallucinate population table
    return None


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
