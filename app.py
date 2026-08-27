import streamlit as st
import pandas as pd
import datetime
import os
import json
import base64
from PIL import Image
import io

# ---------------------------------------------------------
# Page Configuration & Global Styles
# ---------------------------------------------------------
st.set_page_config(
    page_title="Vanity Sanctuary",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');

    .stApp {
        background-color: #d8cde9 !important;
        font-family: 'Lora', serif;
    }

    .main .block-container {
        max-width: 440px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .sanctuary-header {
        background: #ffffff;
        border-radius: 4px;
        padding: 2.2rem 1rem 1.8rem 1rem;
        text-align: center;
        margin-bottom: 18px;
        box-shadow: 0 4px 15px rgba(120, 100, 150, 0.04);
    }

    .sanctuary-header h1 {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.4rem !important;
        color: #3a3342 !important;
        margin: 0 !important;
        font-weight: 700 !important;
    }

    .sanctuary-header p {
        color: #b5a4c9;
        font-size: 1.25rem;
        font-style: italic;
        margin-top: 0.4rem;
        margin-bottom: 0;
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 14px !important;
        margin-bottom: 14px !important;
    }

    /* Ukrywamy domyślny wygląd i marginesy przycisków wewnątrz kolumn */
    div[data-testid="column"] .stButton {
        width: 100%;
        margin: 0;
    }

    /* Wymuszamy idealny kwadrat z dużym padingiem dla przycisku */
    div[data-testid="column"] button {
        background-color: #ffffff !important;
        border: 1px solid #e2d8ee !important;
        border-radius: 6px !important;
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        height: auto !important;
        min-height: 0 !important;
        padding: 1rem 0.5rem !important;
        box-shadow: 0 4px 12px rgba(100, 80, 130, 0.06) !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        align-items: center !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }

    div[data-testid="column"] button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 18px rgba(100, 80, 130, 0.12) !important;
        background-color: #ffffff !important;
    }

    /* Wygląd nagłówka w kwadracie */
    .tile-title {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        color: #554a60 !important;
        line-height: 1.2 !important;
        text-align: center !important;
        margin-top: 0.4rem !important;
    }

    /* DUŻA EMOTKA W ŚRODKU */
    .tile-icon {
        font-size: 3.8rem !important;
        line-height: 1 !important;
        margin-bottom: 0.4rem !important;
        display: block !important;
    }

    .quote-card {
        background: #ffffff;
        border: 2px solid #3a3342 !important;
        border-radius: 2px;
        padding: 2.2rem 1.5rem;
        text-align: center;
        margin-top: 6px;
    }

    .quote-card p {
        font-family: 'Lora', serif;
        color: #5c5366;
        font-size: 1.35rem;
        margin: 0;
        line-height: 1.4;
    }

    .vanity-card {
        background: #ffffff;
        border-radius: 4px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 3px 10px rgba(130, 110, 160, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Data Storage & State Initialization
# ---------------------------------------------------------
DATA_FILE = "vanity_data.json"

CATEGORIES = [
    "foundation", "concealer", "powder", "contour", "blush", 
    "highlighter", "eyeshadow palette", "lip gloss", "lipstick", 
    "eyeliner", "mascara", "lip liner", "lip mask", 
    "setting spray", "brow gel", "brow pen"
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"products": [], "settings": {}, "stats": {"finished_lip_products": 0, "penalties": 0}}
    return {"products": [], "settings": {}, "stats": {"finished_lip_products": 0, "penalties": 0}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

if "db" not in st.session_state:
    st.session_state.db = load_data()

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# ---------------------------------------------------------
# Header Block
# ---------------------------------------------------------
st.markdown("""
<div class="sanctuary-header">
    <h1>Vanity Sanctuary</h1>
    <p>Minimalist inventory & project pan</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HOME PAGE (IDEALNE KWADRATOWE KAFELKI Z DUŻYMI EMOTKAMI)
# ---------------------------------------------------------
if st.session_state.current_page == "Home":

    # Pomocnicza funkcja generująca html wewnątrz st.button
    def render_tile(title_html, emoji):
        return f'<span class="tile-title">{title_html}</span><span class="tile-icon">{emoji}</span>'

    # Rząd 1
    col1, col2 = st.columns(2)
    with col1:
        if st.button(render_tile("Your<br>Collection", "🦇"), key="btn_coll"):
            st.session_state.current_page = "Collection"
            st.rerun()

    with col2:
        if st.button(render_tile("Project<br>Pan", "🌕"), key="btn_pan"):
            st.session_state.current_page = "Project Pan"
            st.rerun()

    # Rząd 2
    col3, col4 = st.columns(2)
    with col3:
        if st.button(render_tile("No - Buy<br>& Rewards", "🌸"), key="btn_nobuy"):
            st.session_state.current_page = "No-Buy Rules"
            st.rerun()

    with col4:
        if st.button(render_tile("Beauty<br>stats", "🐈‍⬛"), key="btn_stats"):
            st.session_state.current_page = "Analytics"
            st.rerun()

    # Quote Box
    st.markdown("""
    <div class="quote-card">
        <p>Use what you love.<br>Finish what you start.</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# INNER PAGES
# ---------------------------------------------------------
else:
    if st.button("← Back to Menu"):
        st.session_state.current_page = "Home"
        st.rerun()

    st.markdown("---")

    if st.session_state.current_page == "Collection":
        st.markdown("### Your Collection")
        if st.button("+ Add New Product to Collection"):
            st.session_state.current_page = "Add Product"
            st.rerun()

    elif st.session_state.current_page == "Project Pan":
        st.markdown("### Project Pan")

    elif st.session_state.current_page == "No-Buy Rules":
        st.markdown("### No - Buy & Rewards")

    elif st.session_state.current_page == "Analytics":
        st.markdown("### Beauty Stats")

    elif st.session_state.current_page == "Add Product":
        st.markdown("### Add Product")
