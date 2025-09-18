import streamlit as st
import pandas as pd
import requests
import os
import atexit
from utils.data_extractor import extract_from_pdf, extract_from_excel, summarize_financials
from utils.logger import logger

# Ollama Local Call
def ask_ollama(prompt, model="gemma:2b"):
    #Send a simple prompt to local Ollama and return the response.
    try:
        url = "http://localhost:11434/api/generate"
        payload = {"model": model, "prompt": prompt, "stream": False}
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        logger.info("Ollama query sent successfully.")
        return data.get("response", "")
    except Exception as e:
        logger.error(f"Ollama query failed: {e}")
        return f"[Error contacting Ollama: {e}]"

#Cleanup on exit
def cleanup_ollama():
    #Stop Ollama model when Streamlit app exits
    try:
        os.system("ollama stop gemma:2b")
        logger.info("Ollama model stopped on exit.")
    except Exception as e:
        logger.error(f"Error stopping Ollama: {e}")

atexit.register(cleanup_ollama)

# Streamlit UI
st.set_page_config(page_title="Financial Document Q&A", layout="wide")
st.title("📊 Financial Document Q&A Assistant")

st.markdown("Upload a **PDF** or **Excel** file containing financial statements, then ask questions about Revenue, Profit, Expenses, etc.")

# File upload
uploaded_file = st.file_uploader("Upload PDF / XLSX", type=["pdf", "xls", "xlsx"])

if uploaded_file is not None:
    st.success(f"✅ Uploaded: **{uploaded_file.name}**")
    logger.info(f"File uploaded: {uploaded_file.name}")

    # Extract
    if uploaded_file.name.lower().endswith(".pdf"):
        full_table = extract_from_pdf(uploaded_file)
    else:
        full_table = extract_from_excel(uploaded_file)

    if not full_table.empty:
        # Summarize financial metrics
        metrics = summarize_financials(full_table)
        st.subheader("📌 Detected Key Metrics")
        if metrics:
            # Convert dict → DataFrame
            metrics_df = pd.DataFrame(metrics).T
            st.dataframe(metrics_df, use_container_width=True)
        else:
            st.info("No standard financial metrics detected.")

        # ---- Q&A Section ----
        st.subheader("💬 Ask Questions about the Document")
        if "history" not in st.session_state:
            st.session_state["history"] = []

        question = st.chat_input("Ask about revenue, profit, expenses...")

        if question:
            context = f"Financial metrics extracted: {metrics}"
            prompt = f"Document context:\n{context}\n\nUser question: {question}\nAssistant:"
            answer = ask_ollama(prompt)

            st.session_state["history"].append({"role": "user", "content": question})
            st.session_state["history"].append({"role": "assistant", "content": answer})
            logger.info(f"Question asked: {question}")
            logger.info(f"Answer received: {answer}")

        # Show chat history
        for msg in st.session_state["history"]:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**Assistant:** {msg['content']}")
    else:
        st.error("❌ Could not extract tables from this document.")
        logger.warning("File uploaded but no tables could be extracted.")
