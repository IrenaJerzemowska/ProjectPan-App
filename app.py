import streamlit as st
import pandas as pd
import datetime
import os
import json

# ---------------------------------------------------------
# Page Configuration & Navigation
# ---------------------------------------------------------
st.set_page_config(
    page_title="Vanity Sanctuary",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Obsługa nawigacji po kliknięciu w kwadrat
query_params = st.query_params
if "page" in query_params:
    st.session_state.current_page = query_params["page"]
    st.query_params.clear()
    st.rerun()

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# ---------------------------------------------------------
# Global Styles (Tło i Ramki)
# ---------------------------------------------------------
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

    .quote-card {
        background: #ffffff;
        border: 2px solid #3a3342 !important;
        border-radius: 2px;
        padding: 2.2rem 1.5rem;
        text-align: center;
        margin-top: 18px;
    }

    .quote-card p {
        font-family: 'Lora', serif;
        color: #5c5366;
        font-size: 1.35rem;
        margin: 0;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

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
# HOME PAGE (DUŻE, DUŻE KWADRATY I DUŻE EMOTKI)
# ---------------------------------------------------------
if st.session_state.current_page == "Home":

    # Czysty HTML/CSS komponentu kafelków
    grid_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&display=swap');

        body {
            margin: 0;
            padding: 0;
            background-color: transparent;
            font-family: 'Playfair Display', serif;
        }

        .grid-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            width: 100%;
        }

        .tile-card {
            background-color: #ffffff;
            border: 1px solid #e2d8ee;
            border-radius: 4px;
            height: 180px; /* Sztywna duża wysokość */
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            padding: 22px 10px 18px 10px;
            box-sizing: border-box;
            text-decoration: none;
            box-shadow: 0 4px 12px rgba(100, 80, 130, 0.06);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            cursor: pointer;
        }

        .tile-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 18px rgba(100, 80, 130, 0.12);
            border-color: #cbbba6;
        }

        .tile-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #554a60;
            line-height: 1.2;
            text-align: center;
            margin: 0;
        }

        .tile-emoji {
            font-size: 4rem; /* DUŻA EMOTKA */
            line-height: 1;
            margin-bottom: 2px;
        }
    </style>
    </head>
    <body>

    <div class="grid-container">
        <a class="tile-card" href="?page=Collection" target="_top">
            <div class="tile-title">Your<br>Collection</div>
            <div class="tile-emoji">🦇</div>
        </a>
        <a class="tile-card" href="?page=Project Pan" target="_top">
            <div class="tile-title">Project<br>Pan</div>
            <div class="tile-emoji">🌕</div>
        </a>
        <a class="tile-card" href="?page=No-Buy Rules" target="_top">
            <div class="tile-title">No - Buy<br>& Rewards</div>
            <div class="tile-emoji">🌸</div>
        </a>
        <a class="tile-card" href="?page=Analytics" target="_top">
            <div class="tile-title">Beauty<br>stats</div>
            <div class="tile-emoji">🐈‍⬛</div>
        </a>
    </div>

    </body>
    </html>
    """

    st.components.v1.html(grid_html, height=385)

    # Dolny cytat
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

    elif st.session_state.current_page == "Project Pan":
        st.markdown("### Project Pan")

    elif st.session_state.current_page == "No-Buy Rules":
        st.markdown("### No - Buy & Rewards")

    elif st.session_state.current_page == "Analytics":
        st.markdown("### Beauty Stats")
