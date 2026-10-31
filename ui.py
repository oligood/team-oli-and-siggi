import os
import requests
import streamlit as st
from backend import answer_question

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/query")

st.set_page_config(page_title="Hagstofa AI", layout="centered")
st.title("Hagstofa Íslands – Spjallmenni")
st.caption("Leitar í lýsigögnum (ChromaDB) og sækir rauntímagögn beint úr PX-Web API Hagstofunnar.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("details"):
            with st.expander("Uppruni og gögn frá Hagstofu"):
                st.write(f"**Tafla:** {msg['details'].get('table_id')} – {msg['details'].get('title')}")
                st.write(f"**Slóð:** {msg['details'].get('source_url')}")
                for fact in msg["details"].get("facts", []):
                    st.code(fact)


def get_response(prompt: str) -> dict:
    try:
        res = requests.post(BACKEND_URL, json={"prompt": prompt}, timeout=60)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return answer_question(prompt)


prompt = st.chat_input("Spyrðu um mannfjölda, sveitarfélög, búferlaflutninga eða verðbólgu...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Sæki gögn frá Hagstofu Íslands..."):
            result = get_response(prompt)
            answer_text = result.get("answer", "Engin niðurstaða fannst.")
            st.markdown(answer_text)

            details = None
            if result.get("ok"):
                details = {
                    "table_id": result.get("table_id"),
                    "title": result.get("title"),
                    "source_url": result.get("source_url"),
                    "facts": result.get("facts", []),
                }
                with st.expander("Uppruni og gögn frá Hagstofu"):
                    st.write(f"**Tafla:** {details['table_id']} – {details['title']}")
                    st.write(f"**Slóð:** {details['source_url']}")
                    for fact in details["facts"]:
                        st.code(fact)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer_text,
        "details": details,
    })
