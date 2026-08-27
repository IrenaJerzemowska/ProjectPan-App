import streamlit as st
import pandas as pd
import datetime
import os
import json
import base64
from PIL import Image
import io

# ---------------------------------------------------------
# Page Configuration & Pure CSS Styling
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

    /* Tło całej aplikacji */
    .stApp {
        background-color: #d8cde9 !important;
        font-family: 'Lora', serif;
    }

    /* Szerokość centralnego kontenera */
    .main .block-container {
        max-width: 440px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Górny Nagłówek */
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

    /* Odstępy w siatce */
    div[data-testid="stHorizontalBlock"] {
        gap: 14px !important;
        margin-bottom: 14px !important;
    }

    /* WYMUSZENIE WIELKICH DUŻYCH KWADRATÓW DLA ZWYKŁYCH BUTTONÓW */
    div[data-testid="column"] button {
        background-color: #ffffff !important;
        border: 1px solid #e2d8ee !important;
        border-radius: 4px !important;
        width: 100% !important;
        height: 180px !important; /* Sztywna wysokość tworzy z nich duże kwadraty */
        min-height: 180px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
        box-shadow: 0 4px 12px rgba(100, 80, 130, 0.06) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
        padding: 15px 5px !important;
        margin: 0 !important;
    }

    div[data-testid="column"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(100, 80, 130, 0.12) !important;
        background-color: #ffffff !important;
    }

    /* Tekst nagłówka wewnątrz kafelka */
    .tile-text {
        font-family: 'Playfair Display', serif !important;
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        line-height: 1.25 !important;
        color: #554a60 !important;
        text-align: center !important;
        margin-bottom: 0.8rem !important;
        display: block !important;
    }

    /* DUŻA EMOTKA W ŚRODKU KAFELKA */
    .tile-emoji {
        font-size: 3.5rem !important;
        line-height: 1 !important;
        display: block !important;
    }

    /* Dolna karta z cytatem */
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

    /* Inner Pages */
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

LIP_CATEGORIES = ["lip gloss", "lipstick", "lip liner", "lip mask"]

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

def calculate_days_owned(purchase_date_str):
    try:
        p_date = datetime.datetime.strptime(purchase_date_str, "%Y-%m-%d").date()
        return max((datetime.date.today() - p_date).days, 0)
    except Exception:
        return 0

def calculate_cost_per_use(price, total_uses):
    return price if total_uses <= 0 else price / total_uses

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
# HOME PAGE (DUŻE, CZYSTE KWADRATOWE KAFELKI)
# ---------------------------------------------------------
if st.session_state.current_page == "Home":

    # Row 1
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Your\nCollection\n\n🦇", key="btn_coll"):
            st.session_state.current_page = "Collection"
            st.rerun()

    with col2:
        if st.button("Project\nPan\n\n🌕", key="btn_pan"):
            st.session_state.current_page = "Project Pan"
            st.rerun()

    # Row 2
    col3, col4 = st.columns(2)
    with col3:
        if st.button("No - Buy\n& Rewards\n\n🌸", key="btn_nobuy"):
            st.session_state.current_page = "No-Buy Rules"
            st.rerun()

    with col4:
        if st.button("Beauty\nstats\n\n🐈‍⬛", key="btn_stats"):
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

        products = st.session_state.db.get("products", [])
        if not products:
            st.info("Your collection is currently empty.")
        else:
            filter_cat = st.selectbox("Category Filter", ["All Categories"] + CATEGORIES)
            filtered_products = [p for p in products if filter_cat == "All Categories" or p["category"].lower() == filter_cat.lower()]

            for p in reversed(filtered_products):
                days = calculate_days_owned(p["purchase_date"])
                st.markdown(f"""
                <div class="vanity-card">
                    <h4>{p['brand']} — {p['name']}</h4>
                    <p>Category: {p['category']} | Shade: {p['shade']}</p>
                    <p>Price: {p['price']:.2f} {p['currency']} | Days: {days}</p>
                </div>
                """, unsafe_allow_html=True)

    elif st.session_state.current_page == "Project Pan":
        st.markdown("### Project Pan")
        products = [p for p in st.session_state.db.get("products", []) if p.get("in_project_pan", False)]
        if not products:
            st.info("No active items in Project Pan.")
        else:
            for p in products:
                st.write(f"**{p['brand']} - {p['name']}**")

    elif st.session_state.current_page == "No-Buy Rules":
        st.markdown("### No - Buy & Rewards")
        stats = st.session_state.db.get("stats", {})
        st.write(f"Finished lip items: {stats.get('finished_lip_products', 0)}")

    elif st.session_state.current_page == "Analytics":
        st.markdown("### Beauty Stats")
        st.write("Statistics overview.")

    elif st.session_state.current_page == "Add Product":
        st.markdown("### Add Product")
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("Product Name *")
            brand = st.text_input("Brand *")
            shade = st.text_input("Shade")
            category = st.selectbox("Category *", CATEGORIES)
            price = st.number_input("Price *", min_value=0.0, value=15.0)
            currency = st.selectbox("Currency *", ["GBP", "PLN", "EUR", "USD"])
            purchase_date = st.date_input("Purchase Date *", datetime.date.today())
            in_pan = st.checkbox("Add to Project Pan immediately", value=True)

            if st.form_submit_button("Save to Collection ✨"):
                if name and brand:
                    new_item = {
                        "id": str(datetime.datetime.now().timestamp()),
                        "name": name, "brand": brand, "shade": shade if shade else "N/A",
                        "category": category, "price": float(price), "currency": currency,
                        "purchase_date": str(purchase_date), "total_uses": 0, "in_project_pan": in_pan
                    }
                    st.session_state.db["products"].append(new_item)
                    save_data(st.session_state.db)
                    st.session_state.current_page = "Collection"
                    st.rerun()
