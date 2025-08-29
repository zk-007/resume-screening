import os
import io
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.text_extract import READERS, read_pdf, read_docx, read_rtf, read_txt, read_excel, read_pptx
from src.nlp_pipeline import clean_text, extract_experience_years, load_skills_lexicon, infer_skills, ensure_columns

st.set_page_config(page_title="Resume Screening (Embeddings)", page_icon="🧠", layout="wide")
st.title("🧠 Resume Screening Using NLP (Embeddings)")
st.caption("Sentence Transformers + cosine similarity • Skills + Experience extraction")

@st.cache_resource(show_spinner=False)
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_data(show_spinner=False)
def embed_texts(model_name, texts):
    model = SentenceTransformer(model_name)
    return model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

skills_path = os.path.join(os.path.dirname(__file__), "..", "data", "skills_lexicon.txt")
SKILLS = load_skills_lexicon(skills_path)

st.sidebar.header("Mode")
mode = st.sidebar.radio("Select workflow", ["Match my resume → job dataset", "Screen many resumes → one job"], index=0)

top_k = st.sidebar.slider("Top matches to show", 3, 10, 5)

st.sidebar.markdown("---")
st.sidebar.write("**File types supported:** PDF, DOCX, TXT, RTF, Excel, PPTX (for resumes).")
st.sidebar.write("Jobs file: CSV/Excel with `job_id`, `title`, and `Job Description` (or `description`).")

def get_file_text(uploaded):
    """
    Read text from uploaded file-like object.
    Resets pointer to start before/after reading to avoid file-pointer issues.
    """
    if not uploaded:
        return ""
    # ensure pointer at start
    try:
        uploaded.seek(0)
    except Exception:
        pass

    suffix = os.path.splitext(uploaded.name)[1].lower()
    reader = READERS.get(suffix)
    if reader:
        try:
            # Some readers expect a file-like object; some expect bytes. We pass the uploaded object.
            text = reader(uploaded)
            # reset pointer again (Streamlit may reuse object)
            try:
                uploaded.seek(0)
            except Exception:
                pass
            return text or ""
        except Exception as e:
            # fallback: try reading bytes and passing BytesIO
            try:
                uploaded.seek(0)
                data = uploaded.read()
                uploaded.seek(0)
                return reader(io.BytesIO(data)) or ""
            except Exception:
                return ""
    return ""

# ---------- MODE A: one resume → job dataset ----------
if mode == "Match my resume → job dataset":
    with st.sidebar:
        st.subheader("Upload")
        resume_file = st.file_uploader("Resume file", type=[ext[1:] for ext in READERS.keys()], accept_multiple_files=False)
        jobs_file = st.file_uploader("Jobs dataset (CSV/Excel)", type=["csv","xlsx","xls"], accept_multiple_files=False)

    col1, col2 = st.columns([1,1])
    with col1:
        st.subheader("Resume Preview")
        resume_raw = get_file_text(resume_file)
        if resume_raw:
            # show a preview
            st.text(resume_raw[:1200] + ("..." if len(resume_raw) > 1200 else ""))
            # helpful diagnostic for debugging extraction problems
            st.caption(f"Extracted characters: {len(resume_raw)}")
            if len(resume_raw) < 200:
                st.warning("Resume extraction returned a small amount of text. If your PDF has complex formatting, or extraction failed, consider using a text-based PDF/DOCX or check that required libraries (pdfplumber/PyPDF2) are installed.")
        else:
            st.info("Upload a resume to preview its extracted text.")

    jobs_df = None
    if jobs_file is not None:
        try:
            if jobs_file.name.lower().endswith(".csv"):
                jobs_df = pd.read_csv(jobs_file)
            else:
                jobs_df = pd.read_excel(jobs_file)
        except Exception as e:
            st.error(f"Could not read jobs file: {e}")

    with col2:
        st.subheader("Top Job Matches")

        # add an explicit Run button so user controls when matching executes
        run_match = st.button("Run Matching")

        if run_match:
            # run only when clicked
            if not resume_raw:
                st.error("No resume text found. Make sure you've uploaded a readable PDF/DOCX/TXT file.")
            elif jobs_df is None or jobs_df.empty:
                st.error("No jobs dataset uploaded or file is empty.")
            else:
                job_desc_col = ensure_columns(jobs_df, ["Job Description", "description"])
                title_col = ensure_columns(jobs_df, ["title", "job_title", "job"])
                id_col = ensure_columns(jobs_df, ["job_id","id"])

                if not job_desc_col:
                    st.warning("Jobs file must include a 'Job Description' or 'description' column. Available columns: " + ", ".join(jobs_df.columns.astype(str).tolist()))
                else:
                    # preprocess
                    resume_clean = clean_text(resume_raw)
                    job_descs = jobs_df[job_desc_col].astype(str).fillna("").apply(clean_text).tolist()

                    # embeddings
                    model_name = "all-MiniLM-L6-v2"
                    texts = [resume_clean] + job_descs
                    try:
                        embs = embed_texts(model_name, texts)
                    except Exception as e:
                        st.error(f"Embedding failed: {e}")
                        embs = None

                    if embs is not None:
                        resume_emb = embs[0:1]
                        job_embs = embs[1:]
                        sims = cosine_similarity(resume_emb, job_embs).flatten()

                        out = jobs_df.copy()
                        out["match_score"] = sims
                        out = out.sort_values("match_score", ascending=False).head(top_k).reset_index(drop=True)

                        # show results (handle missing title/id gracefully)
                        display_cols = [c for c in [id_col, title_col, "match_score", job_desc_col] if c]
                        st.dataframe(out[display_cols], use_container_width=True)

                        # chart
                        chart_index = title_col if title_col else job_desc_col
                        chart_df = out[[chart_index, "match_score"]].set_index(chart_index)
                        st.bar_chart(chart_df)

                        # Justifications for top rows
                        with st.expander("Why these jobs? (skills & experience)"):
                            jd_text = " ".join(out[job_desc_col].astype(str).tolist())
                            resume_skills = infer_skills(resume_raw, SKILLS)
                            job_skills = infer_skills(jd_text, SKILLS)
                            overlap = sorted(set(resume_skills).intersection(set(job_skills)))
                            exp_years = extract_experience_years(resume_raw)
                            st.write({
                                "resume_skills": resume_skills[:30],
                                "job_skills": job_skills[:30],
                                "overlap_skills": overlap[:30],
                                "resume_experience_years": exp_years
                            })

                        # download
                        st.download_button("Download results (CSV)", out.to_csv(index=False).encode("utf-8"), file_name="resume_to_jobs_matches.csv", mime="text/csv")
        else:
            st.info("Upload both a resume and a jobs dataset, then press **Run Matching** to compute results.")

# ---------- MODE B: many resumes → one job ----------
else:
    with st.sidebar:
        st.subheader("Upload")
        resumes_dataset = st.file_uploader("Resumes dataset (CSV/Excel)", type=["csv","xlsx","xls"], accept_multiple_files=False)
        job_text_input = st.text_area("Paste job description here", height=200, placeholder="Paste the JD text...")

    # read resumes dataset
    resumes_df = None
    if resumes_dataset is not None:
        try:
            if resumes_dataset.name.lower().endswith(".csv"):
                resumes_df = pd.read_csv(resumes_dataset)
            else:
                resumes_df = pd.read_excel(resumes_dataset)
        except Exception as e:
            st.error(f"Could not read resumes dataset: {e}")

    st.subheader("Top Resume Matches")
    if resumes_df is not None and job_text_input.strip():
        resume_col = ensure_columns(resumes_df, ["Resume_str", "resume_text"])
        if not resume_col:
            st.warning("Resumes dataset must include a 'Resume_str' or 'resume_text' column.")
        else:
            # preprocess
            resumes_clean = resumes_df[resume_col].astype(str).fillna("").apply(clean_text).tolist()
            job_clean = clean_text(job_text_input)

            # embeddings
            model_name = "all-MiniLM-L6-v2"
            texts = [job_clean] + resumes_clean
            embs = embed_texts(model_name, texts)
            job_emb = embs[0:1]
            resume_embs = embs[1:]
            sims = cosine_similarity(job_emb, resume_embs).flatten()

            out = resumes_df.copy()
            out["match_score"] = sims
            out = out.sort_values("match_score", ascending=False).head(top_k).reset_index(drop=True)

            st.dataframe(out[[resume_col, "match_score"] + [c for c in out.columns if c not in [resume_col,"match_score"]]][:top_k], use_container_width=True)

            chart_df = out[[resume_col, "match_score"]].set_index(resume_col)
            st.bar_chart(chart_df)

            # justifications for the top resume
            with st.expander("Why these resumes? (skills & experience)"):
                resumes_text_concat = " ".join(out[resume_col].astype(str).tolist())
                jd_skills = infer_skills(job_text_input, SKILLS)
                resumes_skills = infer_skills(resumes_text_concat, SKILLS)
                overlap = sorted(set(jd_skills).intersection(set(resumes_skills)))
                exp_years = [extract_experience_years(t) for t in out[resume_col].astype(str).tolist()]
                st.write({
                    "job_skills": jd_skills[:30],
                    "resumes_skills_sample": resumes_skills[:30],
                    "overlap_skills": overlap[:30],
                    "top_resume_experience_years": exp_years[:top_k]
                })

            st.download_button("Download results (CSV)", out.to_csv(index=False).encode("utf-8"), file_name="resumes_to_job_matches.csv", mime="text/csv")
    else:
        st.info("Upload a resume dataset and paste a job description to compute matches.")
