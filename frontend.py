import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/summarize"

st.set_page_config(page_title="Multilingual Summarizer", layout="wide")
st.title("🌍 Multilingual Document & Text Summarizer")

st.write("Upload a document (PDF, DOCX, TXT) or enter text below to generate a summary.")

option = st.radio("Choose input type:", ("Upload File", "Enter Text"))

summary_length = st.selectbox("Summary Length:", ["short", "medium", "long"])

if option == "Upload File":
    uploaded_file = st.file_uploader("Upload your file", type=["pdf", "docx", "txt"])
    if uploaded_file is not None:
        if st.button("Summarize File"):
            files = {"file": uploaded_file.getvalue()}
            data = {"length": summary_length}
            response = requests.post(API_URL, files={"file": (uploaded_file.name, uploaded_file.getvalue())}, data=data)
            if response.status_code == 200:
                result = response.json()
                st.subheader("📌 Summary")
                st.write(result.get("summary", "Error: No summary generated."))
            else:
                st.error("Error in summarization request.")
else:
    text_input = st.text_area("Enter text here:")
    if st.button("Summarize Text"):
        if text_input.strip():
            data = {"text": text_input, "length": summary_length}
            response = requests.post(API_URL, data=data)
            if response.status_code == 200:
                result = response.json()
                st.subheader("📌 Summary")
                st.write(result.get("summary", "Error: No summary generated."))
            else:
                st.error("Error in summarization request.")
