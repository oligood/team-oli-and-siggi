"""
visuals/interactive_quiz.py - Gagnvirkt Tölfræðipróf: Hversu vel þekkir þú Ísland?

20 vandaðar spurningar byggðar beint á opinberum töflum Hagstofu Íslands,
með rómverskum lárviðarverðlaunum, útskýringum og tilvísunum í gagnatöflur.
"""

from typing import Dict, List, Optional

QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "Hvert er stærsta sveitarfélag Íslands að flatarmáli?",
        "options": ["Þingeyjarsveit", "Sveitarfélagið Hornafjörður", "Múlaþing", "Sveitarfélagið Skagafjörður"],
        "correct": "Þingeyjarsveit",
        "explanation": "Þingeyjarsveit er stærsta sveitarfélag landsins eftir sameiningu við Skútustaðahrepp árið 2022 (yfir 12.021 km²).",
        "table": "MAN02005",
    },
    {
        "id": 2,
        "question": "Á hvaða ári fór mannfjöldi Íslands í fyrsta sinn yfir 100.000 manns?",
        "options": ["1918", "1930", "1944", "1950"],
        "correct": "1930",
        "explanation": "Árið 1930 náði mannfjöldi Íslands 108.861 manns, sama ár og Alþingishátíðin mikla var haldin á Þingvöllum.",
        "table": "MAN00000",
    },
    {
        "id": 3,
        "question": "Hvað búa um það bil margir í Reykjavík samkvæmt nýjustu tölum ársins 2026?",
        "options": ["115.000", "125.000", "139.800", "165.000"],
        "correct": "139.800",
        "explanation": "Samkvæmt töflu MAN02005 búa 139.804 í Reykjavíkurborg þann 1. janúar 2026.",
        "table": "MAN02005",
    },
    {
        "id": 4,
        "question": "Hvaða ár var fyrsta heildstæða manntal sögunnar tekið á Íslandi?",
        "options": ["1703", "1783", "1801", "1901"],
        "correct": "1703",
        "explanation": "Manntalið 1703 var unnið af Árna Magnússyni og Páli Vídalín og var fyrsta heildstæða manntal sinnar tegundar í heiminum (50.358 íbúar).",
        "table": "MAN00000",
    },
    {
        "id": 5,
        "question": "Hvert er næstfjölmennasta sveitarfélag Íslands á eftir Reykjavík?",
        "options": ["Hafnarfjörður", "Kópavogur", "Akureyri", "Reykjanesbær"],
        "correct": "Kópavogur",
        "explanation": "Kópavogsbær er næstfjölmennasta sveitarfélagið með rúmlega 40.280 íbúa árið 2026.",
        "table": "MAN02005",
    },
    {
        "id": 6,
        "question": "Hvert er fjölmennasta hverfi Reykjavíkurborgar samkvæmt hverfaskiptingu Hagstofunnar?",
        "options": ["Vesturbær", "Miðborg", "Breiðholt", "Laugardalur"],
        "correct": "Breiðholt",
        "explanation": "Breiðholt er fjölmennasta hverfið með yfir 21.800 íbúa (tafla MAN03270).",
        "table": "MAN03270",
    },
    {
        "id": 7,
        "question": "Í hvaða mánuði hófst hið sögufræga Heimaeyjargos í Vestmannaeyjum?",
        "options": ["Janúar 1973", "Mars 1974", "Júní 1970", "Október 1975"],
        "correct": "Janúar 1973",
        "explanation": "Heimaeyjargosið hófst að næturlagi þann 23. janúar 1973.",
        "table": "SOG10107",
    },
    {
        "id": 8,
        "question": "Hvert var hæsta ársmeðaltal skráðs atvinnuleysis á Íslandi í kjölfar bankahrunsins?",
        "options": ["4.5%", "6.2%", "8.1%", "12.4%"],
        "correct": "8.1%",
        "explanation": "Árið 2010 náði skráð atvinnuleysi á Íslandi 8.1% samkvæmt töflu VIN00001.",
        "table": "VIN00001",
    },
    {
        "id": 9,
        "question": "Hvað fluttu margir erlendir ferðamenn um Keflavíkurflugvöll á toppárinu 2018?",
        "options": ["Um 1.2 milljón", "Um 1.8 milljón", "Um 2.3 milljónir", "Yfir 3.5 milljónir"],
        "correct": "Um 2.3 milljónir",
        "explanation": "Árið 2018 fóru 2.344 þúsund erlendir ferðamenn um völlinn samkvæmt töflu SAM02001.",
        "table": "SAM02001",
    },
    {
        "id": 10,
        "question": "Hvaða ár var nýja íslenska krónan tekin upp (þar sem 100 gamlar krónur jöfnuðust á við 1 nýja)?",
        "options": ["1970", "1981", "1990", "1994"],
        "correct": "1981",
        "explanation": "Myntbreytingin fór fram 1. janúar 1981 vegna hinnar miklu óðaverðbólgu á áttunda áratugnum.",
        "table": "VIS01002",
    },
    {
        "id": 11,
        "question": "Hvert er fámennasta sveitarfélag á Íslandi samkvæmt skráningu árið 2026?",
        "options": ["Árneshreppur", "Tjörneshreppur", "Skorradalshreppur", "Kaldrananeshreppur"],
        "correct": "Árneshreppur",
        "explanation": "Árneshreppur á Ströndum telur aðeins um 45-50 íbúa og er fámennasta sveitarfélag landsins.",
        "table": "MAN02005",
    },
    {
        "id": 12,
        "question": "Hversu mikið lækkaði mannfjöldi Íslands í Móðuharðindunum (1783–1786)?",
        "options": ["Um 2.000 manns", "Um 5.000 manns", "Um 10.000 manns", "Um 25.000 manns"],
        "correct": "Um 10.000 manns",
        "explanation": "Mannfjöldi fór úr um 48.000 niður í 38.363 árið 1786 vegna hungursneyðar af völdum Skaftárelda.",
        "table": "MAN00000",
    },
    {
        "id": 13,
        "question": "Hvaða landshluti hefur vaxið hraðast hlutfallslega á síðustu 20 árum?",
        "options": ["Vestfirðir", "Suðurnes", "Austurland", "Norðurland vestra"],
        "correct": "Suðurnes",
        "explanation": "Suðurnes hafa tvöfaldast í íbúafjölda frá árinu 2000 (úr 16.400 í yfir 32.100).",
        "table": "MAN01002",
    },
    {
        "id": 14,
        "question": "Hverjar eru lífslíkur íslenskra kvenna við fæðingu árið 2026 samkvæmt Hagstofunni?",
        "options": ["78.5 ár", "81.2 ár", "85.1 ár", "89.4 ár"],
        "correct": "85.1 ár",
        "explanation": "Lífslíkur kvenna eru um 85.1 ár samanborið við 82.4 ár hjá körlum.",
        "table": "MAN05101",
    },
    {
        "id": 15,
        "question": "Hvaða ár sameinuðust Sandgerðisbær og Sveitarfélagið Garður í Suðurnesjabæ?",
        "options": ["2010", "2014", "2018", "2022"],
        "correct": "2018",
        "explanation": "Suðurnesjabær varð til við sameiningu þeirra árið 2018.",
        "table": "MAN02005",
    },
    {
        "id": 16,
        "question": "Hvaða ár var Þjóðarsáttarsamningurinn gerður sem stöðvaði óðaverðbólgu á Íslandi?",
        "options": ["1985", "1990", "1998", "2001"],
        "correct": "1990",
        "explanation": "Þjóðarsáttin var undirrituð í febrúar 1990 og náði verðbólgu niður í einstafa tölu.",
        "table": "VIS01002",
    },
    {
        "id": 17,
        "question": "Hvaða ár náði heildarfjöldi íbúa á Íslandi 300.000 manns?",
        "options": ["1999", "2006", "2012", "2016"],
        "correct": "2006",
        "explanation": "Íbúafjöldi fór yfir 300.000 manns snemma árs 2006.",
        "table": "MAN00000",
    },
    {
        "id": 18,
        "question": "Hvað búa um það bil margir í Akureyrarbæ árið 2026?",
        "options": ["14.500", "17.800", "20.450", "26.000"],
        "correct": "20.450",
        "explanation": "Akureyrarbær telur um 20.450 íbúa og er fjölmennasta sveitarfélag utan höfuðborgarsvæðisins.",
        "table": "MAN02005",
    },
    {
        "id": 19,
        "question": "Hvert er elsta verstöð á Vestfjörðum sem er enn sjálfstætt sveitarfélag?",
        "options": ["Bolungarvík", "Flateyri", "Súðavík", "Suðureyri"],
        "correct": "Bolungarvík",
        "explanation": "Bolungarvíkurkaupstaður hefur haldið sjálfstæði sínu sem öflugt útgerðarsveitarfélag.",
        "table": "MAN02005",
    },
    {
        "id": 20,
        "question": "Hvaða ár tók Seðlabanki Íslands upp formlegt verðbólgumarkmið (2.5%)?",
        "options": ["1994", "2001", "2008", "2015"],
        "correct": "2001",
        "explanation": "Þann 27. mars 2001 var gengi krónunnar gefið frjálst og tekið upp 2.5% verðbólgumarkmið.",
        "table": "VIS01002",
    },
]


def evaluate_quiz_answers(user_answers: Dict[int, str]) -> Dict:
    """Metur svör notandans og skilar stigatölu ásamt rómverskri einkunn."""
    total = len(QUIZ_QUESTIONS)
    correct_count = 0
    feedback = []

    for q in QUIZ_QUESTIONS:
        qid = q["id"]
        chosen = user_answers.get(qid)
        is_corr = (chosen == q["correct"])
        if is_corr:
            correct_count += 1
        feedback.append({
            "id": qid,
            "question": q["question"],
            "chosen": chosen,
            "correct": q["correct"],
            "is_correct": is_corr,
            "explanation": q["explanation"],
            "table": q["table"],
        })

    score_pct = (correct_count / total) * 100.0

    if score_pct == 100.0:
        roman_rank = "IMPERATOR STATISTICAE (Keisari Hagtölvanna)"
        title_desc = "Fullkomið skor! Þú þekkir Ísland eins og lófann á þér."
    elif score_pct >= 80.0:
        roman_rank = "CONSUL ET SENATOR (Öldungaráðsmaður)"
        title_desc = "Framúrskarandi þekking á opinberum hagtölum."
    elif score_pct >= 60.0:
        roman_rank = "TRIBUNUS PLEBIS (Málsvari Lýðsins)"
        title_desc = "Góð þekking á meginhagstærðum og sögu landsins."
    elif score_pct >= 40.0:
        roman_rank = "LEGIONARIUS (Liðsmaður í hernum)"
        title_desc = "Þú þekkir undirstöðuatriðin en getur kafað dýpra í töflurnar."
    else:
        roman_rank = "TIRO (Nýliði í Hagfræði)"
        title_desc = "Mælt er með að skoða töflurnar í töflusafninu betur!"

    return {
        "score": correct_count,
        "total": total,
        "score_pct": score_pct,
        "roman_rank": roman_rank,
        "title_desc": title_desc,
        "details": feedback,
    }
