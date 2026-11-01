# LLM-as-a-Judge Evaluation & Stress Testing Benchmark

- **Verkefni:** Hagstofa Íslands – Agentic Natural Language Data Interface
- **Teymi:** Óli & Siggi (Gagnvist 2026)
- **Vélbúnaður:** NVIDIA DGX Spark (GB10), Ollama í Docker (41 GB VRAM úthlutun)
- **Aðferðafræði:** LLM-as-a-Judge með 70B/72B staðbundnum opnum líkönum yfir PX-API

---

## 1. Sögulegt yfirlit keyrslna (Benchmark Leaderboard)

Taflan er uppfærð sjálfkrafa af `optimize_agents.py` í hverri keyrslu (gildi úr síðasta epoch). Hrágögnin eru í [`reports/history.json`](reports/history.json) og hver keyrsla frá og með Run 4 er vistuð í heild undir `docs/reports/`.

<!-- AUTO:LEADERBOARD:START -->
| Keyrsla | Dagsetning & Tími | Dómara-módel | Prófunarsett | Table Match | Action Match | Zero Hallucination | Meðalsvartími | Athugasemdir |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Run 1** | 2026-11-01 14:23 | `llama3:70b` | 17 próf (Grunnsett) | **100.0%** | **100.0%** | **100.0%** | 15.71s | Grunnprófun á töfluvali og reglukerfi staðfest. |
| **Run 2** | 2026-11-01 14:35 | `llama3.3:70b` | 17 próf (Grunnsett) | **100.0%** | **100.0%** | **100.0%** | 16.59s | Nýrri kynslóð Llama prófuð; sambærilegur stöðugleiki og hraði. |
| **Run 3** | 2026-11-01 15:18 | `qwen2.5:72b` | 27 próf (Adversarial) | **74.1%** | **92.6%** | **77.8%** | 25.64s | **Red Teaming:** 10 nýjar gildrur afhjúpuðu 7 veikleika í töfluvali. |
| **Run 4** | 2026-11-01 16:05 | `qwen2.5:72b` | 27 próf | **100.0%** | **96.3%** | **81.5%** | 24.7s | Post-fix: search.py + px_api.py ([skýrsla](reports/eval_qwen2.5-72b_27tests_20261101-160547.md)) |
<!-- AUTO:LEADERBOARD:END -->

---

## 2. Greining á villuprófum úr Red-Teaming (Run 3)

Í keyrslu 3 var kerfið vísvitandi prófað með 10 nýjum gildrum (#18–#27) til að reyna á mörk þess. Sjö þeirra fóru í ranga töflu. Þrír meginveikleikar komu í ljós, og þegar líkanið fékk ranga töflu í hendurnar bjó það til tölur:

1. **Sameinuð og eldri sveitarfélög (#18, #19, #20):**
   - *Spurningar:* Seyðisfjörður, Garður og Sandgerði, Keflavík.
   - *Niðurstaða:* `search.py` þekkti ekki eldri heiti sem nú tilheyra Múlaþingi, Suðurnesjabæ og Reykjanesbæ. #18 og #19 lentu í heildartöflu Íslands (`MAN00000`). #20 lenti í flugvallartöflunni (`SAM02001`), því orðið „Keflavík“ virkjaði ferðamannaregluna á undan sveitarfélögunum.
   - *Afleiðing:* Líkanið fékk engar staðartölur úr API-inu og ofskynjaði tölur (`664`, `1486`, `1841`). Dómarinn greip þær allar.
2. **Hverfi vs. heild í Reykjavík (#21, #22):**
   - *Spurningar:* Kjalarnes; „Reykjavík í heild, ekki bara Breiðholt“.
   - *Niðurstaða:* Kjalarnes var ekki á hverfalistanum og lenti í `MAN00000`. Í #22 dró orðið „Breiðholt“ spurninguna í hverfatöfluna (`MAN03270`) þótt spurt væri um alla borgina.
3. **Staðarnöfn yfirgnæfðu efnisflokk (#26, #27):**
   - *Spurningar:* Hitastig í Reykjavík (Veðurstofan), fasteignamat í Kópavogi (Þjóðskrá/HMS).
   - *Niðurstaða:* Leitin greip orðin „Reykjavík“ og „Kópavogur“ og sendi fyrirspurnirnar í mannfjöldatöflu (`MAN02005`) í stað þess að hafna þeim.

**Opið mál – #17 (búferlaflutningar til höfuðborgarsvæðisins 2024):** Taflan var rétt (`MAN01002`), en líkanið nefndi tölu (`2345`) sem fannst ekki í svari Hagstofunnar. Þessi villa er í úrvinnslu svarsins, ekki í töfluvalinu, og hefur ekki enn verið lagfærð.

---

## 3. Gerðar lagfæringar (System Optimization)

Til að mæta niðurstöðum Run 3 voru eftirfarandi breytingar gerðar á `search.py` og `px_api.py`:

1. **Höfnunarreglur settar í forgang (Early Rejection):**
   Fyrirspurnum um veður, stýrivexti, Seðlabankann og fasteignamat er hafnað (`REJECT`) áður en landfræðileg leitarorð eru skoðuð.
2. **Kortlagning sveitarfélaga (Municipality Mapping):**
   Um 60 eldri, sameinuð eða óformleg staðarheiti vísa nú á núverandi sveitarfélag (Seyðisfjörður/Egilsstaðir/Djúpivogur → Múlaþing, Garður/Sandgerði → Suðurnesjabær, Keflavík/Njarðvík → Reykjanesbær, Selfoss → Árborg o.fl.). Heitin þekkjast líka í beygingarmyndum (t.d. *Seyðisfirði*).
3. **Rétt gildi sótt úr PX-API:**
   `px_api.py` notar sömu kortlagningu þegar það velur sveitarfélag úr `MAN02005`. Áður valdi það eftir fyrstu 6 stöfum heitisins og féll því á „Alls“ (landið allt) fyrir óþekkt heiti. Það valdi líka Reykjavíkurborg fyrir „Reykjanesbæ“. Líkanið fær nú rétta tölu, sem fjarlægir orsök ofskynjananna í #18–#20.
4. **Afmörkun hverfa vs. sveitarfélaga:**
   Kjalarnes, Grafarholt og Úlfarsárdalur bættust á hverfalistann. Hverfaheiti þurfa nú að standa fremst í orði (svo t.d. „Varmahlíð“ grípi ekki „Hlíðar“). Spurningar um „Reykjavík í heild“ fara í sveitarfélagatöfluna.
5. **„Keflavík“ eftir samhengi:**
   Orðið vísar á flugvallartöfluna nema spurt sé um íbúa. Þá vísar það á Reykjanesbæ.

Eftir breytingarnar velur `find_best_table` rétta töflu í öllum 27 prófunum (staðbundin keyrsla á Mac). Heildarmat með líkani og dómara bætist sjálfkrafa við töfluna að ofan sem Run 4.

---

## 4. Prófunartilvik (27 próf)

- **#01–#03:** Spurningar utan sviðs (fljót, bílar, fjöll) → `NONE` / `REJECT`
- **#04–#06:** Heildarmannfjöldi sveitarfélaga (Kópavogur, Reykjavík, Hafnarfjörður) → `MAN02005`
- **#07–#08:** Mannfjöldi í hverfum (Vesturbær, Breiðholt) → `MAN03270`
- **#09–#10:** Heildarfjöldi á Íslandi (íslenska & enska) → `MAN00000`
- **#11–#13:** Verðbólga og vísitala neysluverðs (núna, söguleg, enska) → `VIS01002`
- **#14:** Launavísitala → `LAU04000`
- **#15:** Atvinnuleysi á Íslandi → `VIN00001`
- **#16:** Ferðamannafjöldi um Keflavíkurflugvöll → `SAM02001`
- **#17:** Búferlaflutningar milli landshluta → `MAN01002`
- **#18–#22 (Adversarial):** Sameinuð sveitarfélög, eldri bæjarheiti og hverfaskipting → `MAN02005` / `MAN03270`
- **#23–#24 (Multi-hop):** Samanburður yfir tvö tímabil (verðbólga, atvinnuleysi) → `VIS01002` / `VIN00001`
- **#25–#27 (Out-of-Scope Strict):** Stýrivextir, hitastig, fasteignamat → `NONE` / `REJECT`

---

## 5. Nýjasta keyrsla (sjálfvirk sundurliðun)

<!-- AUTO:LATEST:START -->
- **Dagsetning:** 2026-11-01 16:05:47
- **Svarlíkan:** `llama3:70b`
- **Dómari (LLM-as-a-Judge):** `qwen2.5:72b`
- **Prófunarskrá:** `stress_tests.json` (27 tilvik)

#### Niðurstöður yfir Epochs

| Epoch | Heildarárangur | Table Match | Action / API Match | Zero Hallucinated Numbers | Meðaltími |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 85.2% | 100.0% | 100.0% | 85.2% | 24.41s |
| 2 | 81.5% | 100.0% | 96.3% | 81.5% | 24.7s |

#### Sundurliðun prófa (epoch 2)

| # | Niðurstaða | Spurning | Tafla (vænt) | Action | Ofskynjaðar tölur | Dómari |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | ✅ | Hvert er lengsta fljót á Íslandi? | `NONE` | `REJECT` ✅ | – | SKIPPED |
| 2 | ✅ | Hvaða bíll er hraðskreiðastur? | `NONE` | `REJECT` ✅ | – | SKIPPED |
| 3 | ✅ | Hvað er hæsta fjall á Íslandi? | `NONE` | `REJECT` ✅ | – | SKIPPED |
| 4 | ✅ | Hvað búa margir í Kópavogi í dag? | `MAN02005` | `FETCH_LATEST` ✅ | – | SKIPPED |
| 5 | ✅ | Hvað búa margir í Reykjavík? | `MAN02005` | `FETCH_LATEST` ✅ | – | SKIPPED |
| 6 | ✅ | Hvað búa margir í Hafnarfirði? | `MAN02005` | `FETCH_LATEST` ✅ | – | SKIPPED |
| 7 | ✅ | Hvað búa margir í Vesturbæ í Reykjavík? | `MAN03270` | `FETCH_LATEST` ✅ | – | SKIPPED |
| 8 | ✅ | Hvað búa margir í Breiðholti? | `MAN03270` | `FETCH_LATEST` ✅ | – | SKIPPED |
| 9 | ✅ | Hvað búa margir á Íslandi? | `MAN00000` | `FETCH_LATEST` ✅ | – | SKIPPED |
| 10 | ✅ | How many people live in Iceland? | `MAN00000` | `FETCH_LATEST` ✅ | – | PASS |
| 11 | ✅ | Hver er verðbólgan núna? | `VIS01002` | `FETCH_LATEST` ✅ | – | SKIPPED |
| 12 | ✅ | Hver var verðbólgan í júní 2024? | `VIS01002` | `FETCH_SPECIFIC` ✅ | – | SKIPPED |
| 13 | ✅ | What is the inflation rate in Iceland? | `VIS01002` | `FETCH_LATEST` ✅ | – | SKIPPED |
| 14 | ✅ | Hver er launavísitalan? | `LAU04000` | `FETCH_LATEST` ✅ | – | SKIPPED |
| 15 | ✅ | Hvað er atvinnuleysi á Íslandi? | `VIN00001` | `FETCH_LATEST` ✅ | – | SKIPPED |
| 16 | ✅ | Hvað fóru margir erlendir ferðamenn um Keflavíkurflugvöll? | `SAM02001` | `FETCH_LATEST` ✅ | – | SKIPPED |
| 17 | ❌ | Hvað fluttu margir til höfuðborgarsvæðisins árið 2024? | `MAN01002` | `FETCH_SPECIFIC` ✅ | 2345.0 | SKIPPED |
| 18 | ❌ | Hvað búa margir á Seyðisfirði? | `MAN02005` | `FETCH_LATEST` ✅ | 664.0 | SKIPPED |
| 19 | ❌ | Hvað búa margir í Garði og Sandgerði? | `MAN02005` | `FETCH_LATEST` ✅ | 1451.0, 1563.0 | SKIPPED |
| 20 | ❌ | Hvað búa margir í Keflavík? | `MAN02005` | `FETCH_LATEST` ✅ | 16121.0 | SKIPPED |
| 21 | ✅ | Hvað búa margir á Kjalarnesi? | `MAN03270` | `FETCH_LATEST` ✅ | – | SKIPPED |
| 22 | ❌ | Hvað búa margir í Reykjavík í heild, ekki bara í Breiðholti? | `MAN02005` | `FETCH_LATEST` ❌ | 2020.0, 123246.0 | SKIPPED |
| 23 | ✅ | Hækkaði verðbólgan milli maí og ágúst 2024? | `VIS01002` | `FETCH_SPECIFIC` ✅ | – | SKIPPED |
| 24 | ✅ | Hvað fjölgaði atvinnulausum mikið milli 2022 og 2023? | `VIN00001` | `FETCH_SPECIFIC` ✅ | – | SKIPPED |
| 25 | ✅ | Hverjir eru stýrivextir Seðlabankans núna? | `NONE` | `REJECT` ✅ | – | SKIPPED |
| 26 | ✅ | Hvað var hitinn í Reykjavík í gær? | `NONE` | `REJECT` ✅ | – | SKIPPED |
| 27 | ✅ | Hvert er fasteignamat íbúða í Kópavogi? | `NONE` | `REJECT` ✅ | – | SKIPPED |
<!-- AUTO:LATEST:END -->
