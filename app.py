import streamlit as st
import pandas as pd
from docx import Document
import io
import chardet

st.set_page_config(page_title="AI Narrative Nexus", layout="wide")

st.title("🧠 AI Narrative Nexus – Dynamic Text Analysis Platform")
st.subheader("Week 1: Data Collection & Input Handling")

st.markdown("""
Upload one or more text files, CSVs, or Word documents — or paste text manually.
The app will display the file information and text preview.
""")

# Function to read text safely
def read_txt(uploaded_file):
    raw = uploaded_file.read()
    detected = chardet.detect(raw)
    encoding = detected['encoding'] or 'utf-8'
    text = raw.decode(encoding, errors='replace')
    return text

def read_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
    except Exception:
        uploaded_file.seek(0)
        raw = uploaded_file.read()
        enc = chardet.detect(raw)['encoding'] or 'utf-8'
        df = pd.read_csv(io.StringIO(raw.decode(enc, errors='replace')))
    return df.to_csv(index=False)

def read_docx(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join([p.text for p in doc.paragraphs])

# User input
uploaded_files = st.file_uploader("📂 Upload files (.txt, .csv, .docx)", type=["txt", "csv", "docx"], accept_multiple_files=True)
pasted_text = st.text_area("✏️ Or paste text manually below (optional):")

if st.button("Process"):
    if not uploaded_files and not pasted_text.strip():
        st.warning("Please upload at least one file or paste some text.")
    else:
        all_texts = []
        for uploaded_file in uploaded_files:
            name = uploaded_file.name
            ext = name.split('.')[-1].lower()
            size = len(uploaded_file.getvalue()) / 1024  # in KB
            
            # Read file
            if ext == "txt":
                text = read_txt(uploaded_file)
            elif ext == "csv":
                text = read_csv(uploaded_file)
            elif ext == "docx":
                text = read_docx(uploaded_file)
            else:
                st.error(f"Unsupported file type: {ext}")
                continue

            st.success(f"✅ Uploaded: {name} ({size:.2f} KB)")
            st.write("**Preview:**")
            st.text(text[:1000])  # show first 1000 chars
            all_texts.append(text)

        if pasted_text.strip():
            st.info("📋 Included pasted text content")
            st.text(pasted_text[:1000])
            all_texts.append(pasted_text)

        if all_texts:
            st.success("🎉 All data sources processed successfully!")
            combined = "\n\n---\n\n".join(all_texts)
            st.session_state['combined_text'] = combined  # save for later weeks
            st.download_button("⬇️ Download combined text", data=combined, file_name="combined_text.txt")
