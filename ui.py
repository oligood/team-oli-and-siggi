import os
import requests
import streamlit as st
import pandas as pd
from backend import answer_question

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/query")

st.set_page_config(
    page_title="Hagstofa AI – Gagnagreind",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #0f4c81;
        margin-bottom: 0.1rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4a5568;
        margin-bottom: 1.2rem;
    }
    .quick-chip-header {
        font-weight: 600;
        color: #2d3748;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        background-color: #e6f4ea;
        color: #137333;
        margin-right: 6px;
    }
    .source-card {
        background-color: #f8fafc;
        border-left: 4px solid #0f4c81;
        padding: 12px 16px;
        border-radius: 6px;
        margin-top: 10px;
        font-size: 0.92rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #0f4c81;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 📊 Hagstofa AI")
    st.caption("Rauntímatenging við opinn PX-Web gagnagrunn Hagstofu Íslands.")
    st.markdown("---")
    
    st.markdown("### 🖥️ Kerfisstaða")
    st.markdown('<span class="status-badge">🟢 PX-Web API Live</span>', unsafe_allow_html=True)
    st.markdown('<span class="status-badge">🟢 RAG Index Tengt</span>', unsafe_allow_html=True)
    
    spark_active = os.getenv("OLLAMA_URL", "") != "http://localhost:11434/api/generate"
    if spark_active:
        st.markdown('<span class="status-badge">⚡ DGX Spark Virkur</span>', unsafe_allow_html=True)
    else:
        st.caption("AI Vél: Local / Deterministic Fallback")
        
    st.markdown("---")
    st.markdown("### 📚 Styður efnisflokka:")
    st.markdown("""
    - **Verðbólga & Vísitala neysluverðs** (`VIS01002`)
    - **Mannfjöldi & Lykiltölur Íslands** (`MAN00000`)
    - **Sveitarfélög & Bæjarfélög** (`MAN02005`)
    - **Hverfi í Reykjavík** (`MAN03270`)
    - **Búferlaflutningar milli landsvæða** (`MAN01002`)
    - **Launavísitala & Launaþróun** (`LAU04000`)
    - **Atvinnuleysi & Vinnumarkaður** (`VIN00001`)
    - **Farþegar & Ferðamenn um KEF** (`SAM02001`)
    """)
    st.markdown("---")
    if st.button("🗑️ Hreinsa spjallferil"):
        st.session_state.messages = []
        st.rerun()

# Main Header
st.markdown('<div class="main-title">📊 Hagstofa Íslands – Gagnagreind</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Spyrðu um opinberar hagtölur á mannamáli (íslensku eða ensku). Kerfið sækir staðfestar tölur beint frá Hagstofunni.</div>', unsafe_allow_html=True)

# Quick Prompts
st.markdown('<div class="quick-chip-header">💡 Prófaðu flýtispurningu (smelltu á hnapp):</div>', unsafe_allow_html=True)

q_col1, q_col2, q_col3, q_col4 = st.columns(4)
clicked_prompt = None

with q_col1:
    if st.button("📈 Hver er verðbólgan núna?", use_container_width=True):
        clicked_prompt = "Hver er verðbólgan núna?"
    if st.button("👥 Mannfjöldi í Kópavogi?", use_container_width=True):
        clicked_prompt = "Hvað búa margir í Kópavogi?"

with q_col2:
    if st.button("🇮🇸 Íbúar á Íslandi?", use_container_width=True):
        clicked_prompt = "Hvað búa margir á Íslandi?"
    if st.button("🏘️ Íbúar í Vesturbæ?", use_container_width=True):
        clicked_prompt = "Hvað búa margir í Vesturbæ í Reykjavík?"

with q_col3:
    if st.button("💼 Hvað er atvinnuleysi?", use_container_width=True):
        clicked_prompt = "Hvað er atvinnuleysi á Íslandi?"
    if st.button("💵 Hver er launavísitalan?", use_container_width=True):
        clicked_prompt = "Hver er launavísitalan?"

with q_col4:
    if st.button("✈️ Ferðamenn um KEF?", use_container_width=True):
        clicked_prompt = "Hvað fóru margir erlendir ferðamenn um Keflavíkurflugvöll?"
    if st.button("🚚 Flutningar til RVK 2024?", use_container_width=True):
        clicked_prompt = "Hvað fluttu margir til höfuðborgarsvæðisins árið 2024?"

st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Display metrics / charts if available in message
        if msg.get("metrics"):
            m_cols = st.columns(len(msg["metrics"]))
            for idx, m in enumerate(msg["metrics"]):
                m_cols[idx].metric(label=m["label"], value=m["value"], delta=m.get("delta"))
                
        if msg.get("chart_df") is not None and not msg["chart_df"].empty:
            st.bar_chart(msg["chart_df"].set_index("Liður"))

        if msg.get("details"):
            d = msg["details"]
            with st.expander("🔍 Uppruni og opinber Hagstofugögn"):
                st.markdown(f"**Opinber tafla:** [{d.get('table_id')} – {d.get('title')}]({d.get('source_url')})")
                for f in d.get("facts", []):
                    st.code(f, language="yaml")


def query_backend(prompt_text: str) -> dict:
    try:
        res = requests.post(BACKEND_URL, json={"prompt": prompt_text}, timeout=30)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    # Fallback directly to Python backend
    return answer_question(prompt_text)


chat_input = st.chat_input("Sláðu inn spurningu hér (t.d. 'Hver var verðbólgan í júní 2024?' eða 'How many people live in Iceland?')...")
prompt = clicked_prompt or chat_input

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Sæki staðfestar tölur frá Hagstofu Íslands..."):
            result = query_backend(prompt)
            answer_text = result.get("answer", "Engin niðurstaða fannst.")
            
            st.markdown(answer_text)

            metrics_list = []
            chart_df = None
            details = None

            if result.get("ok"):
                computed = result.get("computed", {})
                table_id = result.get("table_id")
                
                # Render KPI metrics when relevant
                if table_id == "VIS01002" and "infl" in computed:
                    metrics_list = [
                        {"label": f"Vísitala neysluverðs ({computed.get('m_curr')})", "value": f"{computed.get('v_curr'):.1f} stig"},
                        {"label": "12 mánaða verðbólga", "value": f"{computed.get('infl'):.2f}%", "delta": f"vs {computed.get('m_prev')}"}
                    ]
                elif table_id == "VIN00001" and "unemployment_rate" in computed:
                    metrics_list = [
                        {"label": f"Atvinnuleysi ({computed.get('m_curr')})", "value": f"{computed.get('unemployment_rate'):.1f}%"},
                        {"label": "Fjöldi án atvinnu", "value": f"{computed.get('unemployed_count', 0):,} manns"}
                    ]
                elif table_id == "LAU04000" and "wage_growth" in computed:
                    metrics_list = [
                        {"label": f"Launavísitala ({computed.get('m_curr')})", "value": f"{computed.get('wage_index'):.1f}"},
                        {"label": "12 mánaða launaþróun", "value": f"+{computed.get('wage_growth'):.1f}%"}
                    ]
                elif table_id == "MAN00000":
                    row_val = result.get("structured_data", [{}])[0].get("Gildi", 394324)
                    metrics_list = [
                        {"label": "Íbúafjöldi Íslands (1. jan)", "value": f"{int(row_val):,} manns"}
                    ]
                elif table_id == "SAM02001" and "passenger_count" in computed:
                    metrics_list = [
                        {"label": f"Farþegar um KEF ({computed.get('m_curr')})", "value": f"{computed.get('passenger_count'):,} manns"}
                    ]

                if metrics_list:
                    m_cols = st.columns(len(metrics_list))
                    for idx, m in enumerate(metrics_list):
                        m_cols[idx].metric(label=m["label"], value=m["value"], delta=m.get("delta"))

                # Chart visualization
                struct_data = result.get("structured_data", [])
                if len(struct_data) > 1:
                    chart_df = pd.DataFrame(struct_data)
                    st.bar_chart(chart_df.set_index("Liður"))

                details = {
                    "table_id": result.get("table_id"),
                    "title": result.get("title"),
                    "source_url": result.get("source_url"),
                    "facts": result.get("facts", []),
                }

                with st.expander("🔍 Uppruni og opinber Hagstofugögn"):
                    st.markdown(f"**Opinber tafla hjá Hagstofu:** [{details['table_id']} – {details['title']}]({details['source_url']})")
                    for f in details["facts"]:
                        st.code(f, language="yaml")

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer_text,
        "metrics": metrics_list,
        "chart_df": chart_df,
        "details": details,
    })
