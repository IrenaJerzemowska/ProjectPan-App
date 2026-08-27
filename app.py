import streamlit as st
import pandas as pd
import datetime
import os
import json
import base64
from PIL import Image
import io

# ---------------------------------------------------------
# Page Configuration & Clean Aesthetic Theme
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

    /* Background Theme */
    .stApp {
        background-color: #d8cde9 !important;
        color: #382a4b;
        font-family: 'Lora', serif;
    }

    /* Container Width */
    .main .block-container {
        max-width: 440px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Header */
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
        letter-spacing: -0.5px;
    }

    .sanctuary-header p {
        color: #b5a4c9;
        font-size: 1.25rem;
        font-family: 'Lora', serif;
        font-style: italic;
        margin-top: 0.4rem;
        margin-bottom: 0;
        font-weight: 400;
    }

    /* Layout Spacing */
    div[data-testid="stHorizontalBlock"] {
        gap: 14px !important;
        margin-bottom: 14px !important;
    }

    div[data-testid="column"] {
        position: relative !important;
    }

    /* Square Tiles */
    .custom-tile {
        background-color: #ffffff;
        border: 1px solid #e2d8ee;
        border-radius: 4px;
        width: 100%;
        aspect-ratio: 1 / 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center; /* Centered content vertically */
        gap: 1rem; /* Balanced space between title & emoji */
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(100, 80, 130, 0.06);
        box-sizing: border-box;
    }

    .custom-tile-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.35rem;
        font-weight: 700;
        color: #554a60;
        text-align: center;
        line-height: 1.25;
        margin: 0;
    }

    /* Floating Animation for Whimsical Feel */
    @keyframes floatEmoji {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-4px) rotate(3deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    .custom-tile-icon {
        font-size: 3.5rem; /* Larger emoji size */
        line-height: 1;
        margin: 0;
        display: inline-block;
        animation: floatEmoji 3.5s ease-in-out infinite;
        filter: drop-shadow(0px 2px 4px rgba(100, 80, 130, 0.15));
    }

    /* Staggered animation timings for each emoji */
    .icon-bat { animation-delay: 0s; }
    .icon-moon { animation-delay: 0.8s; }
    .icon-flower { animation-delay: 1.6s; }
    .icon-cat { animation-delay: 2.4s; }

    /* Overlay Click Handler */
    .overlay-button > button {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
        z-index: 10 !important;
        cursor: pointer !important;
    }

    /* Quote Banner */
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
        letter-spacing: 0.2px;
    }

    /* Inner Pages */
    .vanity-card {
        background: #ffffff;
        border-radius: 4px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 3px 10px rgba(130, 110, 160, 0.05);
    }

    .metric-box {
        background: #f7f3fd;
        border: 1px solid #dcd0f0;
        padding: 0.8rem;
        border-radius: 4px;
        text-align: center;
    }
    .metric-box .metric-value {
        font-size: 1.4rem;
        font-weight: 600;
        color: #4a3468;
        font-family: 'Playfair Display', serif;
    }
    .metric-box .metric-label {
        font-size: 0.7rem;
        color: #8c7aa9;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 2px;
    }

    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        border-color: #cbbad9 !important;
        color: #382a4b !important;
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

def image_to_base64(uploaded_file):
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image.thumbnail((400, 400))
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    return None

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown("""
<div class="sanctuary-header">
    <h1>Vanity Sanctuary</h1>
    <p>Minimalist inventory & project pan</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PAGE 1: HOME
# ---------------------------------------------------------
if st.session_state.current_page == "Home":

    # Row 1
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="custom-tile">
            <div class="custom-tile-title">Your<br>Collection</div>
            <div class="custom-tile-icon icon-bat">🦇</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="overlay-button">', unsafe_allow_html=True)
        if st.button("Your Collection", key="btn_coll"):
            st.session_state.current_page = "Collection"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="custom-tile">
            <div class="custom-tile-title">Project<br>Pan</div>
            <div class="custom-tile-icon icon-moon">🌕</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="overlay-button">', unsafe_allow_html=True)
        if st.button("Project Pan", key="btn_pan"):
            st.session_state.current_page = "Project Pan"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Row 2
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
        <div class="custom-tile">
            <div class="custom-tile-title">No - Buy<br>& Rewards</div>
            <div class="custom-tile-icon icon-flower">🌸</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="overlay-button">', unsafe_allow_html=True)
        if st.button("No - Buy & Rewards", key="btn_nobuy"):
            st.session_state.current_page = "No-Buy Rules"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="custom-tile">
            <div class="custom-tile-title">Beauty<br>stats</div>
            <div class="custom-tile-icon icon-cat">🐈‍⬛</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="overlay-button">', unsafe_allow_html=True)
        if st.button("Beauty stats", key="btn_stats"):
            st.session_state.current_page = "Analytics"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Bottom Quote Frame
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

    # --- COLLECTION ---
    if st.session_state.current_page == "Collection":
        st.markdown("### Your Collection")
        
        if st.button("+ Add New Product to Collection"):
            st.session_state.current_page = "Add Product"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        products = st.session_state.db.get("products", [])

        if not products:
            st.markdown("""
            <div class="vanity-card" style="text-align:center; padding:2rem;">
                <p style="color:#8c7aa9; margin:0;">Your collection is currently empty.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            filter_cat = st.selectbox("Category Filter", ["All Categories"] + CATEGORIES)
            filtered_products = [p for p in products if filter_cat == "All Categories" or p["category"].lower() == filter_cat.lower()]

            for p in reversed(filtered_products):
                days = calculate_days_owned(p["purchase_date"])
                cpu = calculate_cost_per_use(p["price"], p.get("total_uses", 0))

                st.markdown(f"""
                <div class="vanity-card">
                    <h4 style="margin:0 0 0.4rem 0; font-family:'Playfair Display', serif;">{p['brand']} — <span style="font-weight:400;">{p['name']}</span></h4>
                    <p style="margin:0 0 0.8rem 0; color:#8c7aa9; font-size:0.88rem;">Category: {p['category']} | Shade: {p['shade']}</p>
                    <p style="margin:0; font-size:0.9rem;"><strong>Price:</strong> {p['price']:.2f} {p['currency']} | <strong>Age:</strong> {days} days | <strong>Uses:</strong> {p.get('total_uses', 0)} | <strong>CPU:</strong> {cpu:.2f} {p['currency']}</p>
                </div>
                """, unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    is_pan = p.get("in_project_pan", False)
                    btn_label = "Remove from Pan" if is_pan else "Add to Project Pan ✨"
                    if st.button(btn_label, key=f"pan_{p['id']}"):
                        p["in_project_pan"] = not is_pan
                        save_data(st.session_state.db)
                        st.rerun()
                with c2:
                    if st.button("Mark as Finished 🎉", key=f"fin_{p['id']}"):
                        if p["category"].lower() in LIP_CATEGORIES:
                            st.session_state.db["stats"]["finished_lip_products"] = st.session_state.db["stats"].get("finished_lip_products", 0) + 1
                        st.session_state.db["products"] = [item for item in st.session_state.db["products"] if item["id"] != p["id"]]
                        save_data(st.session_state.db)
                        st.rerun()

    # --- PROJECT PAN ---
    elif st.session_state.current_page == "Project Pan":
        st.markdown("### Project Pan")
        products = [p for p in st.session_state.db.get("products", []) if p.get("in_project_pan", False)]

        if not products:
            st.info("No active items in Project Pan.")
        else:
            for p in products:
                days = calculate_days_owned(p["purchase_date"])
                total_uses = p.get("total_uses", 0)
                cpu = calculate_cost_per_use(p["price"], total_uses)

                st.markdown(f"""
                <div class="vanity-card">
                    <h4 style="margin:0 0 1rem 0; font-family:'Playfair Display', serif;">{p['brand']} — {p['name']} ({p['shade']})</h4>
                """, unsafe_allow_html=True)

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(f'<div class="metric-box"><div class="metric-value">{days}</div><div class="metric-label">Days Owned</div></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="metric-box"><div class="metric-value">{total_uses}</div><div class="metric-label">Uses</div></div>', unsafe_allow_html=True)
                with m3:
                    st.markdown(f'<div class="metric-box"><div class="metric-value">{cpu:.2f} {p["currency"]}</div><div class="metric-label">Cost / Use</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                col_add, col_btn = st.columns([2, 1])
                with col_add:
                    add_uses = st.number_input("Log Uses:", min_value=1, max_value=10, value=1, key=f"uses_{p['id']}")
                with col_btn:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Log Usage", key=f"btn_{p['id']}"):
                        p["total_uses"] = p.get("total_uses", 0) + add_uses
                        save_data(st.session_state.db)
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

    # --- NO-BUY RULES ---
    elif st.session_state.current_page == "No-Buy Rules":
        st.markdown("### No - Buy & Rewards")
        stats = st.session_state.db.get("stats", {})

        fin_lips = stats.get("finished_lip_products", 0)
        earned_tokens = fin_lips // 5
        lips_needed = 5 - (fin_lips % 5)

        st.markdown("#### 5-Out = 1-In Rule (Lip Products)")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-box"><div class="metric-value">{fin_lips}</div><div class="metric-label">Finished</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-box"><div class="metric-value">{earned_tokens}</div><div class="metric-label">Allowed</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-box"><div class="metric-value">{lips_needed}</div><div class="metric-label">To Next</div></div>', unsafe_allow_html=True)

    # --- BEAUTY STATS ---
    elif st.session_state.current_page == "Analytics":
        st.markdown("### Beauty Stats")
        products = st.session_state.db.get("products", [])

        if not products:
            st.info("No data available.")
        else:
            st.markdown("#### Oldest Products in Collection")
            sorted_by_age = sorted(products, key=lambda x: calculate_days_owned(x["purchase_date"]), reverse=True)[:3]
            for p in sorted_by_age:
                days = calculate_days_owned(p["purchase_date"])
                st.markdown(f"""
                <div class="vanity-card">
                    <h5 style="margin:0; font-family:'Playfair Display', serif;">{p['brand']} — {p['name']}</h5>
                    <p style="margin:4px 0 0 0; color:#635770; font-size:0.85rem;">Owned for {days} days</p>
                </div>
                """, unsafe_allow_html=True)

    # --- ADD PRODUCT ---
    elif st.session_state.current_page == "Add Product":
        st.markdown("### Add Product")
        with st.form("add_form", clear_on_submit=True):
            name = st.text_input("Product Name *")
            brand = st.text_input("Brand *")
            shade = st.text_input("Shade")
            category = st.selectbox("Category *", CATEGORIES)
            
            c1, c2 = st.columns(2)
            with c1:
                price = st.number_input("Price *", min_value=0.0, value=15.0)
                currency = st.selectbox("Currency *", ["GBP", "PLN", "EUR", "USD"])
                purchase_date = st.date_input("Purchase Date *", datetime.date.today())
            with c2:
                capacity = st.number_input("Capacity", min_value=0.0, value=10.0)
                unit = st.selectbox("Unit", ["ml", "g", "items"])

            in_pan = st.checkbox("Add to Project Pan immediately", value=True)
            uploaded_img = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

            if st.form_submit_button("Save to Collection ✨"):
                if name and brand:
                    img_b64 = image_to_base64(uploaded_img) if uploaded_img else None
                    new_item = {
                        "id": str(datetime.datetime.now().timestamp()),
                        "name": name, "brand": brand, "shade": shade if shade else "N/A",
                        "category": category, "price": float(price), "currency": currency,
                        "purchase_date": str(purchase_date), "capacity": float(capacity),
                        "unit": unit, "total_uses": 0, "in_project_pan": in_pan, "image_b64": img_b64
                    }
                    st.session_state.db["products"].append(new_item)
                    save_data(st.session_state.db)
                    st.success(f"Added {brand} - {name}")
                    st.session_state.current_page = "Collection"
                    st.rerun()
                else:
                    st.error("Please fill in Name and Brand.")
