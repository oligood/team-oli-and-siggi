# Hagstofa AI - Blönduð Leið (Hybrid RAG + API)

Markmið: Smíða snjalla leitarvél fyrir hagtölur sem skilar nákvæmum, gagnreyndum svörum.

Hönnun (Architecture):
1. Málskilningur & Leit (RAG): Notandi spyr spurningar. RAG leitar í staðbundnum vektorgagnagrunni (með lýsigögnum Hagstofunnar) til að finna rétt töfluheiti (t.d. VIS01002) og breytur.
2. Gagnasókn (Direct PX-API): Kerfið býr til JSON-fyrirspurn fyrir PX-Web API Hagstofunnar og sækir rauntímagögn beint í gagnagrunninn.
3. Svar myndað: LLM tekur API-niðurstöðuna og orðar hana á mannamáli ásamt tilvísun í upprunatöflu.

Tæknistafla:
- Viðmót: Streamlit (Python)
- Bakendi: FastAPI / Python
- LLM / RAG: Ollama / Hugging Face (keyrt á NVIDIA DGX Spark).
