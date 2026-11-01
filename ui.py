import os
import time
import html
import requests
import streamlit as st
from backend import answer_question

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/query")

st.set_page_config(
    page_title="Gagnasvarari — Hagstofa Íslands",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Lora:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<style>
    :root {
        --primary-color: #C5A059;
    }

    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stHeader"],
    footer {
        display: none !important;
    }

    html, body {
        margin: 0 !important;
        padding: 0 !important;
        background-color: #1A2E40 !important;
    }

    .stApp,
    .stApp > .main,
    [data-testid="stAppViewContainer"] {
        background-color: #1A2E40 !important;
        font-family: 'Lora', Georgia, 'Times New Roman', serif;
    }

    .block-container,
    .stMainBlockContainer {
        padding-top: 0 !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        padding-bottom: 6rem !important;
        max-width: 820px !important;
        background-color: transparent !important;
    }

    .page-header {
        background: linear-gradient(160deg, #1e3347 0%, #0f1f2e 100%);
        padding: 4rem 2rem 3rem 2rem;
        text-align: center;
        border-bottom: 3px solid #C5A059;
        width: 100vw;
        position: relative;
        left: 50%;
        margin-left: -50vw;
        margin-top: 0;
        box-sizing: border-box;
    }

    .institution-label {
        font-family: 'Cinzel', serif;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.35em;
        text-transform: uppercase;
        color: #C5A059;
        margin-bottom: 0.9rem;
    }

    .main-title {
        font-family: 'Cinzel', serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: #F5F4F0;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        line-height: 1.15;
        margin-bottom: 0.8rem;
    }

    .header-rule {
        width: 60px;
        height: 1px;
        background: #C5A059;
        margin: 0.9rem auto;
        opacity: 0.7;
    }

    .sub-title {
        font-family: 'Lora', serif;
        font-size: 0.92rem;
        color: #8fa5bc;
        font-style: italic;
    }

    .divider-ornament {
        text-align: center;
        color: #C5A059;
        font-family: 'Cinzel', serif;
        font-size: 0.85rem;
        letter-spacing: 0.6em;
        margin: 1.8rem 0 1.2rem 0;
        opacity: 0.65;
    }

    .chat-msg {
        background: #FFFFFF;
        border: 1px solid #DDD8D0;
        border-radius: 2px;
        box-shadow: 0 1px 4px rgba(26,46,64,0.06);
        padding: 1rem 1.25rem;
        margin-bottom: 0.85rem;
    }

    .chat-msg-label {
        font-family: 'Cinzel', serif;
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #C5A059;
        margin-bottom: 0.45rem;
        border-bottom: 1px solid #EDE8E1;
        padding-bottom: 0.35rem;
    }

    .chat-msg-body {
        font-family: 'Lora', Georgia, serif;
        font-size: 0.97rem;
        line-height: 1.8;
        color: #1A2530;
    }

    .chat-msg.user {
        border-left: 3px solid #1A2E40;
    }

    .chat-msg.assistant {
        border-left: 3px solid #C5A059;
    }

    [data-testid="stBottom"],
    [data-testid="stBottom"] > div {
        background-color: #1A2E40 !important;
        border-top: 1px solid #C5A059 !important;
    }

    [data-testid="stChatInput"] > div {
        background: #0f1f2e !important;
        border: 1.5px solid #C5A059 !important;
        border-radius: 2px !important;
        box-shadow: none !important;
    }

    [data-testid="stChatInput"] > div:focus-within {
        border-color: #F5F4F0 !important;
        box-shadow: none !important;
        outline: none !important;
    }

    [data-testid="stChatInput"] textarea {
        font-family: 'Lora', Georgia, serif !important;
        font-size: 0.97rem !important;
        background: transparent !important;
        color: #F5F4F0 !important;
        caret-color: #C5A059 !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }

    [data-testid="stChatInput"] button {
        background: #1A2E40 !important;
        border-radius: 2px !important;
        border: none !important;
        color: #C5A059 !important;
    }

    [data-testid="stExpander"] {
        background: #EDE8E1 !important;
        border: 1.5px solid #C5A059 !important;
        border-radius: 2px !important;
        box-shadow: none !important;
        outline: none !important;
    }

    [data-testid="stExpander"] summary {
        background: #EDE8E1 !important;
        outline: none !important;
        box-shadow: none !important;
        color: #1A2E40 !important;
    }

    [data-testid="stExpander"] summary p {
        font-family: 'Cinzel', serif !important;
        font-size: 0.73rem !important;
        letter-spacing: 0.18em !important;
        text-transform: uppercase !important;
        color: #1A2E40 !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }

    [data-testid="stExpanderDetails"] {
        background: #FAF8F5 !important;
        border-top: 1px solid #DDD8D0 !important;
    }

    [data-testid="stExpanderDetails"] p,
    [data-testid="stExpanderDetails"] span,
    [data-testid="stExpanderDetails"] label,
    [data-testid="stExpanderDetails"] .stMarkdown p {
        color: #1A2530 !important;
        font-family: 'Lora', Georgia, serif !important;
        font-size: 0.93rem !important;
    }

    .stButton > button {
        font-family: 'Cinzel', serif !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        background: #EDE8E1 !important;
        color: #1A2E40 !important;
        border: 1.5px solid #1A2E40 !important;
        border-radius: 2px !important;
        padding: 0.4rem 1.4rem !important;
        box-shadow: none !important;
    }

    .stButton > button:hover {
        background: #1A2E40 !important;
        color: #C5A059 !important;
        border-color: #1A2E40 !important;
    }

    .stButton > button:focus {
        box-shadow: none !important;
        outline: none !important;
    }

    code, pre {
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
        background: #E4E0D8 !important;
        border-radius: 2px !important;
        color: #1A2530 !important;
        border: none !important;
    }

    .stSpinner > div {
        border-top-color: #C5A059 !important;
    }

    hr {
        border: none !important;
        border-top: 1px solid rgba(197,160,89,0.35) !important;
        margin: 1.5rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="page-header">
    <div class="institution-label">Hagstofa Íslands &nbsp;&middot;&nbsp; Statistics Iceland</div>
    <div class="main-title">Gagnasvarari</div>
    <div class="header-rule"></div>
    <div class="sub-title">Opinbert spjallviðmót fyrir tölfræðilegar fyrirspurnir</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="divider-ornament">&#10022;&nbsp;&nbsp;&nbsp;&#10022;&nbsp;&nbsp;&nbsp;&#10022;</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_admin_debug" not in st.session_state:
    st.session_state.last_admin_debug = None


def render_message(role: str, content: str):
    label = "Spurning" if role == "user" else "Svar"
    css_class = "user" if role == "user" else "assistant"
    safe = html.escape(content).replace("\n", "<br>")
    st.markdown(f"""
<div class="chat-msg {css_class}">
    <div class="chat-msg-label">{label}</div>
    <div class="chat-msg-body">{safe}</div>
</div>
""", unsafe_allow_html=True)


for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])

prompt = st.chat_input("Sláðu inn fyrirspurn um hagtölur...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_message("user", prompt)

    with st.spinner("Sæki gögn..."):
        t0 = time.time()
        try:
            response = requests.post(
                BACKEND_URL,
                json={"query": prompt, "prompt": prompt},
                timeout=60,
            )
            if response.status_code == 200:
                res_data = response.json()
            else:
                res_data = answer_question(prompt)
        except Exception:
            res_data = answer_question(prompt)

        latency = time.time() - t0
        answer_text = res_data.get("answer", "Engin svör bárust.")

        raw_px = res_data.get("raw_px", res_data.get("query_used", {}))
        model_prompt = res_data.get("model_prompt", f"Query: {prompt}")

        st.session_state.last_admin_debug = {
            "table": res_data.get("table", res_data.get("table_id", "N/A")),
            "action": res_data.get("action", "N/A"),
            "latency": latency,
            "prompt": model_prompt,
            "raw_px": raw_px if raw_px else None,
        }

    st.session_state.messages.append({"role": "assistant", "content": answer_text})
    render_message("assistant", answer_text)
    st.rerun()

st.markdown("---")

with st.expander("Tæknilegar upplýsingar / Kerfisrýni", expanded=False):
    if st.session_state.last_admin_debug:
        dbg = st.session_state.last_admin_debug
        st.markdown(f"**Valin tafla:** `{dbg.get('table', 'Engin')}`")
        st.markdown(f"**Aðgerð:** `{dbg.get('action', 'N/A')}`")
        st.markdown(f"**Vinnslutími:** `{dbg.get('latency', 0):.2f} sek`")
        if dbg.get("prompt"):
            st.markdown("**Prompt:**")
            st.code(dbg["prompt"], language="text")
        if dbg.get("raw_px"):
            st.markdown("**Hrá gögn frá Hagstofu:**")
            st.json(dbg["raw_px"])
    else:
        st.caption("Engin fyrirspurn hefur verið send á núverandi setu.")

    if st.button("Hreinsa spjallferil"):
        st.session_state.messages = []
        st.session_state.last_admin_debug = None
        st.rerun()
