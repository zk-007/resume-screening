import re
import numpy as np
import pandas as pd

# Stopwords handling with fallback
def _get_stopwords():
    try:
        import nltk
        from nltk.corpus import stopwords
        try:
            _ = stopwords.words("english")
        except LookupError:
            import nltk
            nltk.download("stopwords")
        return set(stopwords.words("english"))
    except Exception:
        # minimal fallback
        return set({'a','an','the','and','or','of','to','in','for','on','with','by','at','from','as','is','are','be','this','that','it'})

STOP_WORDS = _get_stopwords()

def clean_text(text: str) -> str:
    if text is None or (isinstance(text, float) and np.isnan(text)):
        return ""
    try:
        from bs4 import BeautifulSoup
        from contractions import fix
    except Exception:
        # Work even if libs missing
        def fix(x): return x
        class BeautifulSoup:
            def __init__(self, t, parser): self.t = t
            def get_text(self): return self.t

    # lowercase
    text = str(text).lower()
    # expand contractions
    text = fix(text)
    # strip HTML
    text = BeautifulSoup(text, "html.parser").get_text()
    # remove urls
    text = re.sub(r"http\S+|www\S+|https\S+", " ", text)
    # remove non-ascii
    text = text.encode("ascii", "ignore").decode("utf-8")
    # keep only letters and spaces
    text = re.sub(r"[^a-z\s]", " ", text)
    # remove stopwords
    tokens = [w for w in text.split() if w not in STOP_WORDS]
    return " ".join(tokens)

def extract_experience_years(text: str):
    if not text:
        return None
    # e.g., "3+ years", "5 years of experience", "2 yrs", "8+yrs"
    import re
    pat = re.compile(r"(\d{1,2})\s*\+?\s*(?:years?|yrs?)", re.IGNORECASE)
    hits = [int(m.group(1)) for m in pat.finditer(text)]
    return max(hits) if hits else None

def load_skills_lexicon(path: str) -> set:
    try:
        with open(path, "r", encoding="utf-8") as f:
            skills = [line.strip().lower() for line in f if line.strip()]
        return set(skills)
    except Exception:
        return set()

def infer_skills(text: str, lexicon: set) -> list:
    if not text or not lexicon:
        return []
    txt = " " + text.lower() + " "
    found = set()
    # match multi-words first (sort by length desc)
    multi = sorted([s for s in lexicon if " " in s], key=lambda x: -len(x))
    single = [s for s in lexicon if " " not in s]
    for phrase in multi:
        if f" {phrase} " in txt:
            found.add(phrase)
    tokens = set(txt.split())
    for s in single:
        if s in tokens:
            found.add(s)
    return sorted(found)

def ensure_columns(df, candidates):
    """Return the first existing column from candidates or None."""
    for c in candidates:
        if c in df.columns:
            return c
    return None