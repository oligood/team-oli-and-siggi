"""
visuals/statistical_glossary_encyclopedia.py - Tölfræðialfræði Hagstofu Íslands

Alfræðirit yfir öll helstu hugtök, reiknireglur og aðferðafræði sem notuð eru
í opinberri hagtölugerð á Íslandi og innan Evrópska hagskýrslukerfisins (Eurostat).
"""

from typing import Dict, List, Optional

STATISTICAL_ENCYCLOPEDIA = [
    {
        "term": "Vísitala neysluverðs (VNV)",
        "latin": "INDEX PRETIORUM CONSUMPTORUM",
        "category": "Efnahagsmál",
        "formula": "VNV = (Summa(Verð_t * Magn_0) / Summa(Verð_0 * Magn_0)) * 100",
        "definition": (
            "Mælikvarði á verðbreytingar á vörum og þjónustu sem almenningur kaupir til einkaneyslu. "
            "Grunnur vísitölunnar er byggður á reglulegri rannsókn á útgjöldum heimilanna. "
            "Á Íslandi er vísitalan reiknuð í miðjum hverjum mánuði af Hagstofunni og er grundvöllur verðtryggingar."
        ),
        "source_table": "VIS01002",
        "notes": "Grunnur var síðast uppfærður árið 1988 í 100 stig.",
    },
    {
        "term": "12 mánaða verðbólga",
        "latin": "INFLATIO ANNUA",
        "category": "Efnahagsmál",
        "formula": "Verðbólga = ((VNV_t - VNV_{t-12}) / VNV_{t-12}) * 100",
        "definition": (
            "Hlutfallsleg breyting á vísitölu neysluverðs á tólf mánaða tímabili. "
            "Ef vísitalan hækkar úr 595.6 í 630.3 stig á einu ári er verðbólgan 5.83%. "
            "Seðlabanki Íslands hefur það lögbundna hlutverk að halda verðbólgu sem næst 2.5% markmiði."
        ),
        "source_table": "VIS01002",
        "notes": "Hæst fór verðbólga á Íslandi yfir 100% á árinu 1983.",
    },
    {
        "term": "Kjarnverðbólga (Core Inflation)",
        "latin": "INFLATIO CENTRALIS",
        "category": "Efnahagsmál",
        "formula": "VNV án sveiflukenndra liða (grænmeti, eldsneyti, opinber þjónusta)",
        "definition": (
            "Verðbólga þar sem dregnir eru frá liðir sem sveiflast mjög hratt eða ráðast af tímabundnum áföllum, "
            "t.d. búvörur, bensín og opinberlega verðlögð þjónusta. "
            "Gefur skýrari mynd af undirliggjandi verðbólguþrýstingi í hagkerfinu."
        ),
        "source_table": "VIS01002",
        "notes": "Hagstofan birtir vísitölur kjarnverðbólgu 1, 2, 3 og 4.",
    },
    {
        "term": "Frjósemi (Total Fertility Rate)",
        "latin": "FECUNDITAS TOTALIS",
        "category": "Lýðfræði",
        "formula": "Summa aldursbundinnar fæðingartíðni kvenna á aldrinum 15–49 ára",
        "definition": (
            "Sá meðalfjöldi barna sem kona myndi eignast á ævinni miðað við ríkjandi fæðingartíðni. "
            "Til að mannfjöldi haldist í jafnvægi til lengri tíma án aðflutnings þarf frjósemi að vera um 2.1 barn á hverja konu. "
            "Á Íslandi hefur frjósemi lækkað úr yfir 4.0 árið 1960 niður í um 1.55 árið 2026."
        ),
        "source_table": "MAN05101",
        "notes": "Lækkandi frjósemi er eitt helsta einkenni þróaðra ríkja í dag.",
    },
    {
        "term": "Lífslíkur við fæðingu",
        "latin": "EXSPECTATIO VITAE AD NATALEM",
        "category": "Lýðfræði",
        "formula": "Meðalaldur út frá dánarlíkum hvers aldursárs samkvæmt dánartöflu",
        "definition": (
            "Fjöldi ára sem nýfætt barn má vænta þess að lifa ef dánartíðni ársins helst óbreytt alla ævi þess. "
            "Íslendingar hafa lengi verið meðal langlífustu þjóða heims. "
            "Árið 2026 eru lífslíkur kvenna 85.1 ár en karla 82.4 ár."
        ),
        "source_table": "MAN05101",
        "notes": "Árið 1850 voru lífslíkur aðeins 32-38 ár vegna mikils ungbarnadauða.",
    },
    {
        "term": "Framfærsluhlutfall (Dependency Ratio)",
        "latin": "PROPORTIO SUBSISTENTIAE",
        "category": "Lýðfræði",
        "formula": "((Íbúar 0-14 ára + Íbúar 65 ára og eldri) / Íbúar 15-64 ára) * 100",
        "definition": (
            "Hlutfall þeirra sem eru utan hefðbundins vinnualdurs (börn og eldri borgarar) "
            "miðað við fjölda fólks á vinnufærum aldri (15–64 ára). "
            "Hækkandi framfærsluhlutfall endurspeglar öldrun þjóðarinnar og eykur kröfur á lífeyris- og heilbrigðiskerfi."
        ),
        "source_table": "MAN00000",
        "notes": "Hlutfallið hefur farið hækkandi á Íslandi samhliða auknum lífslíkum.",
    },
    {
        "term": "Skráð atvinnuleysi",
        "latin": "PROPORTIO VACATIONIS",
        "category": "Vinnumarkaður",
        "formula": "(Skráðir atvinnulausir / Áætlaður mannafli á vinnumarkaði) * 100",
        "definition": (
            "Hlutfall þeirra sem eru skráðir án atvinnu hjá Vinnumálastofnun og eru í virkri atvinnuleit. "
            "Hagstofan mælir einnig atvinnuleysi samkvæmt samræmdum stöðlum Alþjóðavinnumálastofnunarinnar (ILO) "
            "með mánaðarlegum vinnumarkaðsrannsóknum (VMR)."
        ),
        "source_table": "VIN00001",
        "notes": "Skráð atvinnuleysi sveiflast að jafnaði milli 3% og 4% á Íslandi í góðæri.",
    },
    {
        "term": "Kaupmáttur launa",
        "latin": "VIS EMPTIONIS MERCEDUM",
        "category": "Vinnumarkaður",
        "formula": "(Launavísitala / Vísitala neysluverðs) * 100",
        "definition": (
            "Mælikvarði á hversu mikið magn af vörum og þjónustu er hægt að kaupa fyrir launin. "
            "Ef laun hækka um 7% en verðbólga er 5% eykst kaupmáttur um rúmlega 1.9%. "
            "Kaupmáttur launa hefur vaxið umtalsvert á Íslandi frá aldamótum."
        ),
        "source_table": "LAU04000",
        "notes": "Tafla LAU04000 mælir reglulegar launagreiðslur í öllum atvinnugreinum.",
    },
    {
        "term": "Búferlaflutningar (Net Migration)",
        "latin": "MIGRATIO NETTA",
        "category": "Lýðfræði",
        "formula": "Aðfluttir umfram brottflutta = Aðfluttir - Brottfluttir",
        "definition": (
            "Mismunur á fjölda þeirra sem flytja til tiltekins svæðis eða lands og þeirra sem flytja þaðan burt. "
            "Innanlandsflutningar skýra að miklu leyti mikinn vöxt á höfuðborgarsvæðinu og Suðurnesjum "
            "á kostnað dreifbýlli landshluta."
        ),
        "source_table": "MAN01002",
        "notes": "Tafla MAN01002 sýnir flutninga milli allra 8 landshluta eftir kyni og aldri.",
    },
    {
        "term": "Lágtekjumörk (At-risk-of-poverty threshold)",
        "latin": "LIMES PAUPERTATIS",
        "category": "Samfélag",
        "formula": "60% af miðgildi ráðstöfunartekna á neyslueiningu",
        "definition": (
            "Samkvæmt evrópskum stöðlum (EU-SILC) teljast þeir sem hafa ráðstöfunartekjur undir 60% af miðgildi vera undir lágtekjumörkum. "
            "Ísland er að jafnaði með eitt lægsta hlutfall fólks undir lágtekjumörkum í Evrópu (um 8–10%)."
        ),
        "source_table": "SAM01001",
        "notes": "Mælikvarðinn er afstæður og endurspeglar tekjudreifingu frekar en algjöra fátækt.",
    },
    {
        "term": "Gini-stuðull (Gini Coefficient)",
        "latin": "COEFFICIENTS GINI",
        "category": "Samfélag",
        "formula": "Gildi á bilinu 0 (fullkominn jöfnuður) til 100 (fullkominn ójöfnuður)",
        "definition": (
            "Alþjóðlegur mælikvarði á tekjudreifingu og ójöfnuð. "
            "Ef allir í samfélaginu hafa nákvæmlega sömu tekjur er stuðullinn 0; ef einn aðili hefur allar tekjur er hann 100. "
            "Á Íslandi mælist Gini-stuðullinn að jafnaði á bilinu 22 til 25, sem telst mjög mikill tekjujöfnuður á heimsvísu."
        ),
        "source_table": "SAM01001",
        "notes": "Ísland, Noregur og Danmörk hafa lægstu Gini-stuðla heims.",
    },
    {
        "term": "Landsframleiðsla (VLF / GDP)",
        "latin": "PRODUCTUS DOMESTICUS BRUTTUS",
        "category": "Efnahagsmál",
        "formula": "VLF = Einkaneysla + Samneysla + Fjárfesting + (Útflutningur - Innflutningur)",
        "definition": (
            "Heildarverðmæti allrar vöru og þjónustu sem framleidd er í landinu á tilteknu tímabili. "
            "Breyting á vergri landsframleiðslu á föstu verðlagi milli ára mælir hagvöxt. "
            "Á Íslandi eru sjávarútvegur, orkufrekur iðnaður og ferðaþjónusta meginundirstöður útflutningstekna."
        ),
        "source_table": "THJ01101",
        "notes": "Tafla THJ01101 birtir landsframleiðslu ársfjórðungslega og árlega.",
    },
    {
        "term": "PxWeb API Gagnastaðallinn",
        "latin": "NORMA TRANSMISSIONIS PXWEB",
        "category": "Tölvugögn",
        "formula": "HTTP POST query með JSON síum á PX endpoints",
        "definition": (
            "Sérhæfður gagnagrunnsstaðall hannaður af norrænum hagstofum (Statistics Sweden, Statistics Iceland o.fl.) "
            "fyrir margvíð fylki (multidimensional statistical cubes). "
            "Kerfið styður JSON-stat, CSV og beinar JSON-fyrirspurnir."
        ),
        "source_table": "PX-API",
        "notes": "Gagnasvararinn okkar tengist beint við þetta API á slóðinni https://px.hagstofa.is/pxis/api/v1/is/",
    },
]


def search_encyclopedia(query: str = "", category: Optional[str] = None) -> List[Dict]:
    """Leitar í alfræðiritinu eftir hugtökum eða flokkum."""
    results = STATISTICAL_ENCYCLOPEDIA
    if category and category != "Allir flokkar":
        results = [e for e in results if e["category"] == category]

    if query.strip():
        ql = query.lower().strip()
        results = [
            e for e in results
            if ql in e["term"].lower() or ql in e["definition"].lower() or ql in e["latin"].lower()
        ]
    return results


def render_encyclopedia_card_html(entry: Dict) -> str:
    """Býr til ítarlegt rómverskt alfræðispjald."""
    return f"""
<div style="background-color: #FAF8F5; border: 1px solid #C5A059; border-left: 4px solid #8B6914;
            border-radius: 2px; padding: 1.4rem; margin-bottom: 1.1rem; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
    <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 0.3rem;">
        <span style="font-family: 'Cinzel', serif; font-size: 0.72rem; font-weight: 700; color: #8B6914; letter-spacing: 0.15em;">
            {entry['latin']} &middot; {entry['category']}
        </span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #5A4A32;">
            {entry['source_table']}
        </span>
    </div>
    <div style="font-family: 'Cinzel', Georgia, serif; font-size: 1.25rem; font-weight: 700; color: #1A2E40; margin-bottom: 0.5rem;">
        {entry['term']}
    </div>
    <div style="background: #EAE3D6; border-radius: 2px; padding: 0.5rem 0.8rem; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: #1A2530; margin-bottom: 0.8rem;">
        <b>Formúla:</b> {entry['formula']}
    </div>
    <div style="font-family: 'Lora', serif; font-size: 0.98rem; line-height: 1.7; color: #1A2530; margin-bottom: 0.6rem;">
        {entry['definition']}
    </div>
    <div style="font-family: 'Lora', serif; font-size: 0.85rem; font-style: italic; color: #6C7A89;">
        {entry['notes']}
    </div>
</div>
"""
