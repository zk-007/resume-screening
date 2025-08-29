<<<<<<< HEAD
# Elevvo_Pathways
Collection of NLP projects developed during my internship.
=======
# Task 8 — Resume Screening Using NLP (Embeddings)

This app adapts your notebook logic into a Streamlit front‑end. It uses **Sentence Transformers** (semantic embeddings) + **cosine similarity** to match resumes and job descriptions, and provides **lightweight explanations** (skills overlap + experience regex).

## Features
- Upload **resume files** (PDF/DOCX/TXT/RTF/Excel/PPTX) or a **resume dataset (CSV/Excel)**.
- Upload **job dataset (CSV/Excel)** or paste a **job description**.
- Preprocess text (lowercase, contractions, HTML removal, stopwords, etc.).
- Compute embeddings with `all-MiniLM-L6-v2` and cosine similarity.
- Show **top-k matches** with bar charts.
- Extract **skills** (lexicon-based) and **experience years** (regex) as justifications.
- Download results as CSV.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Data expectations
### Resume dataset (CSV/Excel)
- Expected column name: `Resume_str` (or `resume_text` as fallback).

### Job dataset (CSV/Excel)
- Expected columns: `job_id`, `title`, `Job Description` (or `description` as fallback).

## Deploy to Streamlit Community Cloud
1. Push this folder to a public GitHub repo.
2. Go to https://share.streamlit.io and select your repo.
3. Set **App file**: `streamlit_app.py`.
4. Deploy.

## Notes
- The Sentence Transformer model will download on first run (`all-MiniLM-L6-v2`).
- NLTK stopwords will download on first run; the app also includes a tiny fallback list.
- `skills_lexicon.txt` is a lightweight skills list. Extend it as needed.

**License:** MIT
>>>>>>> 61bdbb5 (Initial commit - Resume Screening Embeddings Streamlit Project)
