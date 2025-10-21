import streamlit as st
import pandas as pd
from docx import Document
import io, re, chardet, string, html
from bs4 import BeautifulSoup
from langdetect import detect
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
import spacy
from collections import Counter
import matplotlib.pyplot as plt

# --- Setup ---
st.set_page_config(page_title="AI Narrative Nexus", layout="centered")
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nlp = spacy.load('en_core_web_sm')

# --- File reading helpers ---
def read_txt(uploaded_file):
    raw = uploaded_file.read()
    enc = chardet.detect(raw)['encoding'] or 'utf-8'
    return raw.decode(enc, errors='replace')

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

# --- NEW: Clean raw HTML and decode ---
def clean_html(text):
    soup = BeautifulSoup(text, "html.parser")
    cleaned = soup.get_text(separator=" ")
    decoded = html.unescape(cleaned)
    return decoded

# --- Text Cleaning and Normalization ---
def clean_text(text):
    text = clean_html(text)  # remove HTML & decode
    text = re.sub(r"http\S+", "", text)            # remove URLs
    text = re.sub(r'[^A-Za-z\s]', ' ', text)       # keep only letters
    text = re.sub(r'\s+', ' ', text)               # normalize spaces
    return text.lower().strip()

def remove_stopwords(tokens):
    stop_words = set(stopwords.words('english'))
    return [t for t in tokens if t not in stop_words and len(t) > 2]

def stem_tokens(tokens):
    stemmer = PorterStemmer()
    return [stemmer.stem(t) for t in tokens]

def lemmatize_tokens(tokens):
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(t) for t in tokens]

def process_text(text, mode='lemmatize'):
    try:
        lang = detect(text)
        if lang != 'en':
            st.warning("⚠️ Skipped non-English text detected.")
            return []
    except:
        pass

    cleaned = clean_text(text)
    tokens = word_tokenize(cleaned)
    tokens = remove_stopwords(tokens)
    if mode == 'stem':
        tokens = stem_tokens(tokens)
    else:
        tokens = lemmatize_tokens(tokens)
    return tokens

def show_word_frequency(tokens, top_n=15):
    if not tokens:
        return
    freq = Counter(tokens)
    common = freq.most_common(top_n)
    words, counts = zip(*common)
    fig, ax = plt.subplots()
    ax.bar(words, counts)
    ax.set_xticklabels(words, rotation=45, ha='right')
    ax.set_title("Top Word Frequencies")
    st.pyplot(fig)

# --- Streamlit UI ---
st.title("🧠 AI Narrative Nexus - Text analysis")
st.markdown("Now with HTML removal, emoji cleaning, and English filtering!")

uploaded_files = st.file_uploader("📂 Upload files (.txt, .csv, .docx)", type=["txt", "csv", "docx"], accept_multiple_files=True)
pasted_text = st.text_area("✏️ Or paste text manually (optional):")

mode = st.radio("Choose normalization technique:", ["Lemmatization", "Stemming"])

if st.button("Run Preprocessing"):
    all_texts = []
    for uploaded_file in uploaded_files:
        ext = uploaded_file.name.split('.')[-1].lower()
        if ext == 'txt':
            text = read_txt(uploaded_file)
        elif ext == 'csv':
            text = read_csv(uploaded_file)
        elif ext == 'docx':
            text = read_docx(uploaded_file)
        else:
            st.warning(f"Unsupported file: {uploaded_file.name}")
            continue
        all_texts.append(text)
        st.success(f"Loaded file: {uploaded_file.name}")

    if pasted_text.strip():
        all_texts.append(pasted_text)
        st.info("Included pasted text.")

    if not all_texts:
        st.warning("No text provided.")
    else:
        combined_text = "\n".join(all_texts)
        st.subheader("Original Text Sample (Before Cleaning):")
        st.write(combined_text[:1000])

        # --- Process ---
        norm_mode = 'stem' if mode == 'Stemming' else 'lemmatize'
        tokens = process_text(combined_text, mode=norm_mode)
        st.success(f"Processed {len(tokens)} tokens successfully!")

        st.subheader("Cleaned & Tokenized Sample:")
        st.write(" ".join(tokens[:100]))

        # --- Visualization ---
        st.subheader("📊 Word Frequency Chart")
        show_word_frequency(tokens, top_n=15)

        # --- Token download ---
        joined_tokens = " ".join(tokens)
        st.download_button("⬇️ Download Cleaned Text", joined_tokens, file_name="cleaned_text.txt")
