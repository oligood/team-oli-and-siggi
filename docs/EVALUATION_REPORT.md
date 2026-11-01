# LLM-as-a-Judge Evaluation & Stress Testing Report

- **Dagsetning:** 2026-11-01 12:04:46
- **Prófunarskrá:** `stress_tests.json` (17 tilvik)

## Niðurstöður yfir Epochs

| Epoch | Table Match | Action / API Match | Zero Hallucinated Numbers | Meðaltími |
| :--- | :--- | :--- | :--- | :--- |
| 1 | 100.0% | 100.0% | 100.0% | 0.1s |
| 2 | 100.0% | 100.0% | 100.0% | 0.09s |


### Prófunartilvik og hegðun

- **Spurning:** Hvert er lengsta fljót á Íslandi? | **Tafla:** `NONE` | **Action:** `REJECT`
- **Spurning:** Hvaða bíll er hraðskreiðastur? | **Tafla:** `NONE` | **Action:** `REJECT`
- **Spurning:** Hvað er hæsta fjall á Íslandi? | **Tafla:** `NONE` | **Action:** `REJECT`
- **Spurning:** Hvað búa margir í Kópavogi í dag? | **Tafla:** `MAN02005` | **Action:** `FETCH_LATEST`
- **Spurning:** Hvað búa margir í Reykjavík? | **Tafla:** `MAN02005` | **Action:** `FETCH_LATEST`
- **Spurning:** Hvað búa margir í Hafnarfirði? | **Tafla:** `MAN02005` | **Action:** `FETCH_LATEST`
- **Spurning:** Hvað búa margir í Vesturbæ í Reykjavík? | **Tafla:** `MAN03270` | **Action:** `FETCH_LATEST`
- **Spurning:** Hvað búa margir í Breiðholti? | **Tafla:** `MAN03270` | **Action:** `FETCH_LATEST`
- **Spurning:** Hvað búa margir á Íslandi? | **Tafla:** `MAN00000` | **Action:** `FETCH_LATEST`
- **Spurning:** How many people live in Iceland? | **Tafla:** `MAN00000` | **Action:** `FETCH_LATEST`
- **Spurning:** Hver er verðbólgan núna? | **Tafla:** `VIS01002` | **Action:** `FETCH_LATEST`
- **Spurning:** Hver var verðbólgan í júní 2024? | **Tafla:** `VIS01002` | **Action:** `FETCH_SPECIFIC`
- **Spurning:** What is the inflation rate in Iceland? | **Tafla:** `VIS01002` | **Action:** `FETCH_LATEST`
- **Spurning:** Hver er launavísitalan? | **Tafla:** `LAU04000` | **Action:** `FETCH_LATEST`
- **Spurning:** Hvað er atvinnuleysi á Íslandi? | **Tafla:** `VIN00001` | **Action:** `FETCH_LATEST`
- **Spurning:** Hvað fóru margir erlendir ferðamenn um Keflavíkurflugvöll? | **Tafla:** `SAM02001` | **Action:** `FETCH_LATEST`
- **Spurning:** Hvað fluttu margir til höfuðborgarsvæðisins árið 2024? | **Tafla:** `MAN01002` | **Action:** `FETCH_SPECIFIC`
