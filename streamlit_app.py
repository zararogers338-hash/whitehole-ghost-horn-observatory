# streamlit_app.py
# Generates the Streamlit app code string for the desktop launcher.
# Can also be run directly:  streamlit run streamlit_app.py

STREAMLIT_CODE = r'''
import streamlit as st
import pandas as pd
import numpy as np
import os

from constants import (
    APP_TITLE, MODE_IDS, AB_MODES, STOPWORD_MODES, HIGHLIGHT_MODES,
    CAO_SUBMODE_IDS, T, get_mode_display_names, get_cao_display_names,
    get_caption,
)
from utils import (
    read_any_text, scan_paper_directory, extract_time_decimal,
    extract_keywords_enhanced, extract_keywords_with_sensitivity,
)
from plot_functions import (
    build_single_horn, build_dual_horn, build_delta_horn,
    build_starfield_horn, build_chessboard, build_cao_analysis,
    build_keyword_terrain, build_wrinkle_cloud,
    build_postal_mobius_x_interaction, build_single_oreo, generate_report_pdf,
)

# ───────────────────────────────────────────────────────────────────────────
#  Language state
# ───────────────────────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "en"
L = st.session_state.lang          # shorthand used below

# ───────────────────────────────────────────────────────────────────────────
#  Page config & global CSS
# ───────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title=APP_TITLE, layout="wide",
                   initial_sidebar_state="expanded", menu_items=None)

st.markdown("""
<style>
.stApp { background: #06060e; color: #d4d4d8; }
h1, h2, h3, h4 { color: #00FF7F !important; }
h1 { text-shadow: 0 0 18px rgba(0,255,127,.35); font-size: 1.6rem !important; }
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080814 0%, #0a0a18 100%);
    border-right: 1px solid rgba(0,255,127,.25);
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { font-size: 1rem !important; }
.stButton > button {
    background: linear-gradient(135deg, #00FF7F 0%, #00cc66 100%);
    color: #050510; border: none; font-weight: 700;
    border-radius: 6px; transition: all .2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #00cc66 0%, #009950 100%);
    color: #fff; box-shadow: 0 0 12px rgba(0,255,127,.3);
}
div[data-testid="stRadio"] label { padding: 4px 8px; border-radius: 4px; transition: background .15s; }
div[data-testid="stRadio"] label:hover { background: rgba(0,255,127,.08); }
.stSlider [data-baseweb="slider"] [role="slider"] { background: #00FF7F !important; }
[data-testid="stHeader"], [data-testid="stToolbar"] { display: none; }
[data-testid="stMetricValue"] { color: #00FF7F !important; font-weight: 800; }
.stCaption, .stMarkdown small { color: #888 !important; }
hr { border-color: rgba(0,255,127,.15) !important; }
.stTextInput input, .stSelectbox [data-baseweb="select"] {
    background: #111 !important; color: #d4d4d8 !important;
    border-color: rgba(0,255,127,.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────────────────
#  Sidebar
# ───────────────────────────────────────────────────────────────────────────
# Defaults (safe scope — always defined before main area uses them)
mode_id = MODE_IDS[0]
a_name = b_name = "None"
custom_stopwords: list[str] = []
highlight_year = None
cao_sub_id = CAO_SUBMODE_IDS[0]
names: list[str] = []
time_range = None          # FIX: always defined

with st.sidebar:
    # ── Language toggle ──
    if st.button(T("lang_toggle", L), key="lang_btn"):
        st.session_state.lang = "zh" if L == "en" else "en"
        st.rerun()
    L = st.session_state.lang  # refresh after potential switch

    st.markdown(f"## {T('sidebar_title', L)}")

    # ── File upload ──
    st.markdown(f"#### {T('upload_header', L)}")
    uploaded_files = st.file_uploader(
        T("upload_header", L), type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True, key="file_uploader",
        label_visibility="collapsed",
    )

    # ── Folder scan ──
    with st.expander(T("scan_folder", L), expanded=False):
        folder_path = st.text_input(T("folder_path", L), key="folder_path",
                                    placeholder="/path/to/papers")
        if st.button(T("scan_btn", L)):
            if folder_path and os.path.isdir(folder_path):
                with st.spinner("…"):
                    scanned = scan_paper_directory(folder_path)
                    st.session_state.scanned_files = scanned
                    st.success(T("scan_found", L, n=len(scanned)))
            else:
                st.error(T("invalid_folder", L))

    scanned_files = st.session_state.get("scanned_files", [])
    all_items = (uploaded_files or []) + scanned_files

    st.metric(T("loaded_papers", L), len(all_items))
    st.markdown("---")

    # ── Clear cache ──
    if st.button(T("clear_cache", L)):
        for k in ["cached_df", "cached_keywords", "scanned_files", "cached_sw_hash"]:
            st.session_state.pop(k, None)
        st.rerun()

    # ── Mode selection (only when data loaded) ──
    if all_items:
        st.markdown("---")
        st.markdown(T("mode_header", L))
        mode_display = get_mode_display_names(L)
        mode_idx = st.radio(T("mode_header", L), range(len(MODE_IDS)),
                            format_func=lambda i: mode_display[i],
                            key="mode_radio", label_visibility="collapsed")
        mode_id = MODE_IDS[mode_idx]

        # Time sliders
        sample_times = []
        for item in all_items:
            name = getattr(item, "name",
                           os.path.basename(item) if isinstance(item, str) else str(item))
            names.append(name)
            text = read_any_text(item)
            sample_times.append(extract_time_decimal(name, text))

        if sample_times:
            t_lo, t_hi = min(sample_times), max(sample_times)
            time_range = st.slider(T("time_range", L), t_lo, t_hi + 1.0,
                                   (t_lo, t_hi + 1.0), step=0.1)

            if mode_id in HIGHLIGHT_MODES:
                highlight_year = st.slider(T("highlight_year", L), t_lo, t_hi + 1.0,
                                           (t_lo + t_hi) / 2, step=0.1)

        # A/B group selection
        if mode_id in AB_MODES:
            st.markdown("---")
            st.markdown(T("group_selection", L))
            c1, c2 = st.columns(2)
            with c1:
                a_name = st.selectbox("A", [T("none", L)] + names, key="sel_a")
                if a_name == T("none", L):
                    a_name = "None"
            with c2:
                b_name = st.selectbox("B", [T("none", L)] + names, key="sel_b")
                if b_name == T("none", L):
                    b_name = "None"

        # Stopwords
        if mode_id in STOPWORD_MODES:
            sw = st.text_input(T("stopwords_label", L), "")
            custom_stopwords = [w.strip() for w in sw.split(",") if w.strip()]

        # Cao sub-mode
        if mode_id == "cao":
            cao_display = get_cao_display_names(L)
            cao_idx = st.selectbox(T("chart_type", L), range(len(CAO_SUBMODE_IDS)),
                                   format_func=lambda i: cao_display[i], key="cao_sub")
            cao_sub_id = CAO_SUBMODE_IDS[cao_idx]

        st.checkbox(T("perm_labels", L), value=False, key="perm_labels")

# ───────────────────────────────────────────────────────────────────────────
#  Main area — title
# ───────────────────────────────────────────────────────────────────────────
st.markdown(f"# {T('sidebar_title', L)}")

if not all_items:
    st.info(T("no_data_hint", L))
    st.caption(T("footer", L))
    st.stop()

# ───────────────────────────────────────────────────────────────────────────
#  Data processing & caching (invalidate when stopwords change)
# ───────────────────────────────────────────────────────────────────────────
sw_hash = hash(tuple(custom_stopwords))
cache_valid = (
    "cached_df" in st.session_state
    and "cached_keywords" in st.session_state
    and st.session_state.get("cached_sw_hash") == sw_hash
)

if cache_valid:
    df = st.session_state.cached_df
    keywords_data = st.session_state.cached_keywords
else:
    progress = st.progress(0)
    status = st.empty()
    status.info(T("parsing", L))

    data, texts, errors = [], [], 0
    for i, item in enumerate(all_items):
        try:
            name = getattr(item, "name",
                           os.path.basename(item) if isinstance(item, str) else str(item))
            text = read_any_text(item)
            t_val = extract_time_decimal(name, text)

            # Time-range filter
            if time_range is not None and (t_val < time_range[0] or t_val > time_range[1]):
                continue

            size = getattr(item, "size", None)
            if size is None and isinstance(item, str):
                try:
                    size = os.path.getsize(item)
                except Exception:
                    size = 100_000
            mass = max(0.5, min((size or 100_000) / 200_000, 10.0))
            data.append({"name": name, "time": t_val, "mass": mass, "text": text})
            texts.append(text)
        except Exception:
            errors += 1
        progress.progress((i + 1) / len(all_items))

    df = pd.DataFrame(data)
    keywords_data = extract_keywords_enhanced(texts, top_n=40,
                                              custom_stopwords=custom_stopwords)
    st.session_state.cached_df = df
    st.session_state.cached_keywords = keywords_data
    st.session_state.cached_sw_hash = sw_hash
    progress.empty()
    status.empty()
    if errors:
        st.warning(T("parse_fail", L, n=errors))

# ───────────────────────────────────────────────────────────────────────────
#  Render selected mode
# ───────────────────────────────────────────────────────────────────────────
if df.empty:
    st.warning(T("no_data_range", L))
    st.caption(T("footer", L))
    st.stop()

caption = get_caption(mode_id, L)
if caption:
    st.caption(caption)

cfg = {"displayModeBar": False}

try:

    if mode_id == "single_horn":
        fig = build_single_horn(df, highlight_year)
        st.plotly_chart(fig, use_container_width=True, config=cfg)

    elif mode_id == "dual_horn":
        fig = build_dual_horn(df, a_name, b_name)
        st.plotly_chart(fig, use_container_width=True, config=cfg)

    elif mode_id == "delta_horn":
        fig = build_delta_horn(df, a_name, b_name)
        st.plotly_chart(fig, use_container_width=True, config=cfg)

    elif mode_id == "starfield":
        fig = build_starfield_horn(df, keywords_data, highlight_year)
        st.plotly_chart(fig, use_container_width=True, config=cfg)

    elif mode_id == "chessboard":
        fig = build_chessboard(df, keywords_data)
        st.plotly_chart(fig, use_container_width=True, config=cfg)

    elif mode_id == "cao":
        fig = build_cao_analysis(keywords_data, cao_sub_id)
        st.plotly_chart(fig, use_container_width=True, config=cfg)

    elif mode_id == "keyword_terrain":
        fig = build_keyword_terrain(df, keywords_data)
        st.plotly_chart(fig, use_container_width=True, config=cfg)

    elif mode_id == "wrinkle_cloud":
        fig = build_wrinkle_cloud(df, keywords_data)
        st.plotly_chart(fig, use_container_width=True, config=cfg)

    elif mode_id == "postal":
        fig = build_postal_mobius_x_interaction(df.copy(), pd.DataFrame(), keywords_data, [])
        st.plotly_chart(fig, use_container_width=True, config=cfg)

    elif mode_id == "postal_mobius":
        df_a = df.copy() if a_name == "None" else df[df["name"] == a_name].copy()
        df_b = pd.DataFrame() if b_name == "None" else df[df["name"] == b_name].copy()
        kw_a = keywords_data if a_name == "None" else extract_keywords_enhanced(
            df_a["text"].tolist(), custom_stopwords=custom_stopwords)
        kw_b = [] if b_name == "None" else extract_keywords_enhanced(
            df_b["text"].tolist(), custom_stopwords=custom_stopwords)
        fig = build_postal_mobius_x_interaction(df_a, df_b, kw_a, kw_b)
        st.plotly_chart(fig, use_container_width=True, config=cfg)

    elif mode_id == "oreo":
        params = {
            "top_n": 30, "wrinkle_strength": 2.2, "layer_spacing": 1.0,
            "z_compression": 0.05, "fiber_count": 3,
            "fiber_color_mode": "yellow_fixed", "color_scheme": "Plasma_r",
        }

        if a_name != "None" and b_name != "None":
            df_a = df[df["name"] == a_name].copy()
            df_b = df[df["name"] == b_name].copy()
            kw_a, sens_a = extract_keywords_with_sensitivity(df_a["text"].tolist(), top_n=40)
            kw_b, sens_b = extract_keywords_with_sensitivity(df_b["text"].tolist(), top_n=40)
        else:
            df_a = df.copy()
            df_b = pd.DataFrame()
            kw_a, sens_a = extract_keywords_with_sensitivity(df["text"].tolist(), top_n=40)
            kw_b, sens_b = kw_a, sens_a

        if not df_b.empty:
            col1, col2 = st.columns(2)
            with col1:
                fig_a = build_single_oreo(df_a, kw_a, sens_a, params, "A")
                st.plotly_chart(fig_a, use_container_width=True)
            with col2:
                fig_b = build_single_oreo(df_b, kw_b, sens_b, params, "B")
                st.plotly_chart(fig_b, use_container_width=True)
        else:
            fig_a = build_single_oreo(df_a, kw_a, sens_a, params, "A")
            st.plotly_chart(fig_a, use_container_width=True)
            fig_b = None

        # FIX: generate PDF into session_state so download_button persists
        if st.button(T("generate_pdf", L)):
            try:
                pdf_data = generate_report_pdf(fig_a, fig_b, df_a, df_b, kw_a, kw_b)
                st.session_state["oreo_pdf"] = pdf_data
            except Exception as e:
                st.error(T("pdf_fail", L, e=e))

        if "oreo_pdf" in st.session_state:
            st.download_button(
                T("download_pdf", L),
                data=st.session_state["oreo_pdf"],
                file_name="oreo_observation_report.pdf",
                mime="application/pdf",
            )

        st.caption(T("oreo_done", L))

except Exception as _render_err:
    import traceback
    st.error(f"Rendering error: {_render_err}")
    st.code(traceback.format_exc())

# ───────────────────────────────────────────────────────────────────────────
st.caption(T("footer", L))
'''


def get_streamlit_code() -> str:
    return STREAMLIT_CODE


if __name__ == "__main__":
    exec(STREAMLIT_CODE)
