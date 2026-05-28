# utils.py
# Pure utility functions — no Streamlit dependency

import re
import os
import hashlib
from collections import Counter
from io import BytesIO

import numpy as np
import pandas as pd

# Optional heavy deps
try:
    import jieba
    import jieba.analyse
    _HAS_JIEBA = True
except ImportError:
    _HAS_JIEBA = False

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import docx
except ImportError:
    docx = None


# ---------------------------------------------------------------------------
#  Deterministic helpers
# ---------------------------------------------------------------------------

def deterministic_uniform(key: str, low: float = 0.0, high: float = 1.0) -> float:
    """SHA-256 based deterministic pseudo-random value in [low, high)."""
    h = hashlib.sha256(key.encode()).hexdigest()
    v = int(h[:12], 16) / (16 ** 12)
    return low + (high - low) * v


def deterministic_uniform_array(keys, low: float = 0.0, high: float = 1.0) -> np.ndarray:
    """Vectorised version for a sequence of string keys."""
    return np.array([deterministic_uniform(k, low, high) for k in keys])


# ---------------------------------------------------------------------------
#  File I/O
# ---------------------------------------------------------------------------

_MAX_TEXT_LEN = 60_000  # chars


def read_any_text(item) -> str:
    """Read text from an uploaded file-like object **or** a local path.

    Supports: PDF (via PyMuPDF), DOCX (via python-docx), TXT/MD/HTML.
    Returns empty string on unsupported formats or errors.
    """
    text = ""
    try:
        if hasattr(item, "read"):
            data = item.read()
            item.seek(0)
            name = getattr(item, "name", "").lower()
        else:
            name = os.path.basename(item).lower()
            with open(item, "rb") as f:
                data = f.read()

        if name.endswith(".pdf") and fitz:
            doc = fitz.open(stream=data, filetype="pdf")
            parts = [page.get_text("text") for page in doc]
            doc.close()
            text = " ".join(parts)
        elif name.endswith(".docx") and docx:
            doc_obj = docx.Document(BytesIO(data))
            text = " ".join(p.text for p in doc_obj.paragraphs)
        elif name.endswith((".txt", ".md", ".html")):
            text = data.decode("utf-8", errors="ignore")
        else:
            return ""

        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > _MAX_TEXT_LEN:
            text = text[:_MAX_TEXT_LEN]
    except Exception as e:
        print(f"[WhiteHole] read_any_text failed: {e}")
        return ""

    return text


def scan_paper_directory(root_dir: str, max_files: int = 15_000) -> list[str]:
    """Recursively scan *root_dir* for paper files."""
    if not os.path.isdir(root_dir):
        return []
    exts = (".pdf", ".docx", ".txt", ".md")
    results: list[str] = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fn in filenames:
            if fn.lower().endswith(exts):
                results.append(os.path.join(dirpath, fn))
                if len(results) >= max_files:
                    return results
    return results


# ---------------------------------------------------------------------------
#  Time extraction
# ---------------------------------------------------------------------------

def extract_time_decimal(name: str, text: str = "") -> float:
    """Extract a year from *name* (or *text*) and add a fractional offset."""
    match = re.search(r'(19\d{2}|20\d{2})', name)
    if match:
        year = int(match.group(1))
    else:
        years = re.findall(r'\b(19\d{2}|20\d{2})\b', text)
        if years:
            year = int(Counter(years).most_common(1)[0][0])
        else:
            year = 2024
    return year + deterministic_uniform(name, 0.0, 0.99)


# ---------------------------------------------------------------------------
#  Keyword extraction
# ---------------------------------------------------------------------------

_ENGLISH_STOPWORDS = frozenset({
    "this", "that", "with", "from", "which", "their", "these", "those",
    "have", "been", "were", "also", "such", "than", "more", "some",
    "into", "over", "only", "other", "about", "between", "through",
    "after", "before", "most", "each", "both", "under", "where",
    "when", "there", "what", "will", "would", "could", "should",
    "does", "done", "just", "very", "much", "many", "well", "even",
    "still", "however", "using", "based", "used", "paper", "study",
    "results", "method", "methods", "approach", "proposed", "data",
    "model", "models", "system", "systems", "time", "different",
    "first", "show", "shown", "figure", "table", "section",
})


def _is_chinese(all_text: str) -> bool:
    ratio = len(re.findall(r'[\u4e00-\u9fff]', all_text)) / max(len(all_text), 1)
    return ratio > 0.3


def _extract_tags_single(text: str, is_chn: bool, top_n: int):
    """Return list of (word, weight) for a single document."""
    if is_chn and _HAS_JIEBA:
        return jieba.analyse.extract_tags(text, topK=top_n * 2, withWeight=True)
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    words = [w for w in words if w not in _ENGLISH_STOPWORDS]
    counter = Counter(words)
    total = sum(counter.values()) or 1
    return [(w, count / total * 10) for w, count in counter.most_common(top_n * 2)]


def extract_keywords_enhanced(texts: list[str], top_n: int = 40,
                               custom_stopwords: list[str] | None = None) -> list[dict]:
    """Enhanced keyword extraction with weight, sensitivity, and cluster."""
    if not texts:
        return []

    custom_sw = set(custom_stopwords or [])
    all_text = " ".join(texts)
    is_chn = _is_chinese(all_text)

    paper_tags: list[list[tuple[str, float]]] = []
    global_counter: Counter = Counter()

    for text in texts:
        tags = _extract_tags_single(text, is_chn, top_n)
        tags = [(w, wt) for w, wt in tags if len(w) > 1 and w not in custom_sw]
        paper_tags.append(tags)
        for w, wt in tags:
            global_counter[w] += wt

    global_top = global_counter.most_common(top_n)
    global_words = [w for w, _ in global_top]

    sensitivities: list[float] = []
    for w in global_words:
        weights = [wt for tag_list in paper_tags for word, wt in tag_list if word == w]
        sensitivities.append(float(np.var(weights)) if len(weights) > 1 else 0.0)

    clusters: list[int]
    if len(global_words) >= 5:
        try:
            from sklearn.cluster import KMeans
            arr = np.array([wt for _, wt in global_top]).reshape(-1, 1)
            km = KMeans(n_clusters=min(3, len(global_words)), n_init=10, random_state=42)
            clusters = km.fit_predict(arr).flatten().tolist()
        except ImportError:
            clusters = [0] * len(global_words)
    else:
        clusters = [0] * len(global_words)

    return [
        {"kw": w, "score": float(wt), "sensitivity": s, "cluster": c}
        for (w, wt), s, c in zip(global_top, sensitivities, clusters)
    ]


def extract_keywords_with_sensitivity(texts: list[str], top_n: int = 30,
                                       custom_stopwords: list[str] | None = None):
    """Return (keywords_list, sensitivities_list) for Oreo mode."""
    if not texts:
        return [], []

    custom_sw = set(custom_stopwords or [])
    all_text = " ".join(texts)
    is_chn = _is_chinese(all_text)

    paper_dicts: list[dict[str, float]] = []
    for text in texts:
        tags = _extract_tags_single(text, is_chn, top_n)
        paper_dicts.append({w: wt for w, wt in tags if len(w) > 1 and w not in custom_sw})

    global_counter: Counter = Counter()
    for d in paper_dicts:
        for w, wt in d.items():
            global_counter[w] += wt
    top_words = global_counter.most_common(top_n)

    keywords, sensitivities = [], []
    for w, _ in top_words:
        weights = [pd_dict.get(w, 0.0) for pd_dict in paper_dicts]
        s = float(np.var(weights)) if len(weights) > 1 else 0.0
        sensitivities.append(s)
        keywords.append({"kw": w, "score": global_counter[w] / len(texts), "sensitivity": s})

    return keywords, sensitivities
