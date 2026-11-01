# Matskeyrsla 2026-11-01 16:05:47

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
