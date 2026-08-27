import streamlit as st
import pandas as pd
import datetime
import os
import json
import base64
from PIL import Image
import io

# ---------------------------------------------------------
# Page Configuration & Soft Lilac Aesthetics
# ---------------------------------------------------------
st.set_page_config(
    page_title="Vanity Sanctuary",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Plus+Jakarta+Sans:wght@300;400;500;600&display=swap');

    /* Dreamy Pastel Background with subtle stars pattern */
    .stApp {
        background-color: #e2d9f3;
        background-image: radial-gradient(rgba(255, 255, 255, 0.8) 2px, transparent 20px), radial-gradient(rgba(255, 255, 255, 0.8) 1.5px, transparent 15px);
        background-size: 80px 80px, 40px 40px;
        background-position: 0 0, 20px 20px;
        color: #382a4b;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Headings - Serif Classic */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif !important;
        color: #2e1f43 !important;
        font-weight: 600 !important;
    }

    /* Header Banner */
    .sanctuary-header {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        padding: 2.5rem 1.5rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(138, 115, 175, 0.12);
    }

    .sanctuary-header h1 {
        font-size: 2.5rem !important;
        margin-bottom: 0.2rem !important;
        letter-spacing: -0.5px;
    }

    .sanctuary-header p {
        color: #8c7aa9;
        font-size: 1.1rem;
        font-family: 'Playfair Display', serif;
        font-style: italic;
        margin: 0;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: rgba(245, 240, 252, 0.7);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.6);
    }

    /* White Aesthetic Cards */
    .vanity-card {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid rgba(255, 255, 255, 1);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 20px rgba(150, 130, 180, 0.08);
    }

    /* Badges */
    .lilac-badge {
        background-color: #ebdffc;
        color: #5d3b8e;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* Metric Display Box */
    .metric-box {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid #e2d3f7;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
    }
    .metric-box .metric-value {
        font-size: 1.6rem;
        font-weight: 600;
        color: #51337a;
        font-family: 'Playfair Display', serif;
    }
    .metric-box .metric-label {
        font-size: 0.72rem;
        color: #7d6b98;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }

    /* Buttons */
    .stButton > button {
        background: #fdfbff;
        color: #4a326d !important;
        border: 1px solid #d4c2ed;
        border-radius: 10px;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 0.88rem;
        font-weight: 500;
        transition: all 0.2s ease;
        width: 100%;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }

    .stButton > button:hover {
        background-color: #5d3b8e;
        color: #ffffff !important;
        border-color: #5d3b8e;
    }

    /* Inputs */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-color: #d8c7f0 !important;
        color: #2e1f43 !important;
        border-radius: 8px !important;
    }

    hr {
        border-color: #dcd0f0 !important;
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

if "settings" not in st.session_state.db:
    st.session_state.db["settings"] = {}
if "stats" not in st.session_state.db:
    st.session_state.db["stats"] = {"finished_lip_products": 0, "penalties": 0}

# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
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
# Header & Navigation
# ---------------------------------------------------------
st.markdown("""
<div class="sanctuary-header">
    <h1>Vanity Sanctuary</h1>
    <p>Minimalist inventory & project pan</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<h3 style='text-align:center; font-size:1.2rem; margin-bottom:1rem;'>Sanctuary</h3>", unsafe_allow_html=True)
nav = st.sidebar.radio(
    "", 
    ["Collection", "Project Pan", "No-Buy Rules", "Analytics", "Add Product"]
)

# ---------------------------------------------------------
# TAB 1: COLLECTION
# ---------------------------------------------------------
if nav == "Collection":
    st.markdown("### Collection overview")
    products = st.session_state.db.get("products", [])

    if not products:
        st.markdown("""
        <div class="vanity-card" style="text-align:center; padding:2rem;">
            <p style="color:#7d6b98; margin:0; font-size:1.05rem;">Your collection is currently empty.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        filter_cat = st.selectbox("Category Filter", ["All Categories"] + CATEGORIES)
        filtered_products = [p for p in products if filter_cat == "All Categories" or p["category"].lower() == filter_cat.lower()]

        st.caption(f"Showing {len(filtered_products)} item(s)")

        for p in reversed(filtered_products):
            days = calculate_days_owned(p["purchase_date"])
            cpu = calculate_cost_per_use(p["price"], p.get("total_uses", 0))

            st.markdown(f"""
            <div class="vanity-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                    <div>
                        <h4 style="margin:0; font-size:1.15rem; color:#2e1f43;">{p['brand']} <span style="font-weight:400; color:#6b538c;">— {p['name']}</span></h4>
                        <span style="font-size:0.85rem; color:#7d6b98;">Shade: {p['shade']}</span>
                    </div>
                    <span class="lilac-badge">{p['category']}</span>
                </div>
            """, unsafe_allow_html=True)

            col_img, col_info = st.columns([1, 2])
            with col_img:
                if p.get("image_b64"):
                    st.markdown(f'<img src="data:image/png;base64,{p["image_b64"]}" style="width:100%; border-radius:8px; border:1px solid #e2d3f7;">', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="width:100%; height:110px; background-color:#f4eefc; border-radius:8px; display:flex; align-items:center; justify-content:center; color:#9c8bba; font-size:0.8rem; border:1px solid #e2d3f7;">NO IMAGE</div>', unsafe_allow_html=True)

            with col_info:
                st.markdown(f"""
                <div style="font-size:0.9rem; line-height:1.6; color:#4a3963;">
                    <strong>Price:</strong> {p['price']:.2f} {p['currency']}<br>
                    <strong>Age:</strong> {days} days owned<br>
                    <strong>Total Uses:</strong> {p.get('total_uses', 0)}<br>
                    <strong>Cost per Use:</strong> {cpu:.2f} {p['currency']}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                is_pan = p.get("in_project_pan", False)
                btn_label = "Remove from Project Pan" if is_pan else "Add to Project Pan ✨"
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

            st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2: PROJECT PAN
# ---------------------------------------------------------
elif nav == "Project Pan":
    st.markdown("### Active Project Pan")
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
                <h4 style="margin:0 0 1rem 0;">{p['brand']} — {p['name']} <span style="color:#7d6b98; font-size:0.9rem;">({p['shade']})</span></h4>
            """, unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f'<div class="metric-box"><div class="metric-value">{days}</div><div class="metric-label">Days Owned</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-box"><div class="metric-value">{total_uses}</div><div class="metric-label">Total Uses</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="metric-box"><div class="metric-value">{cpu:.2f} {p["currency"]}</div><div class="metric-label">Cost / Use</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            col_add, col_btn = st.columns([2, 1])
            with col_add:
                add_uses = st.number_input("Log Usage Today:", min_value=1, max_value=10, value=1, key=f"uses_{p['id']}")
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Log Usage", key=f"btn_{p['id']}"):
                    p["total_uses"] = p.get("total_uses", 0) + add_uses
                    save_data(st.session_state.db)
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3: NO-BUY RULES
# ---------------------------------------------------------
elif nav == "No-Buy Rules":
    st.markdown("### No-Buy & Rules Tracker")
    stats = st.session_state.db.get("stats", {})

    fin_lips = stats.get("finished_lip_products", 0)
    earned_tokens = fin_lips // 5
    lips_needed = 5 - (fin_lips % 5)

    st.markdown("#### The 5-Out = 1-In Rule (Lippies)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-box"><div class="metric-value">{fin_lips}</div><div class="metric-label">Finished Lippies</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-box"><div class="metric-value">{earned_tokens}</div><div class="metric-label">Purchases Allowed</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-box"><div class="metric-value">{lips_needed}</div><div class="metric-label">Left to Next Allowance</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### Sins & Penalty Tracking")
    penalties = stats.get("penalties", 0)
    
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(f'<div class="metric-box" style="border-color:#f3a4b5;"><div class="metric-value" style="color:#c0392b;">{penalties}</div><div class="metric-label">Penalty Points</div></div>', unsafe_allow_html=True)
    with p2:
        status_text = "Clean Streak ✨" if penalties == 0 else "Rules Broken 💔"
        st.markdown(f'<div class="metric-box"><div class="metric-value">{status_text}</div><div class="metric-label">Status</div></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 4: ANALYTICS
# ---------------------------------------------------------
elif nav == "Analytics":
    st.markdown("### Collection Analytics")
    products = st.session_state.db.get("products", [])

    if not products:
        st.info("No data to analyze.")
    else:
        st.markdown("#### Priority Items (Oldest in Collection)")
        sorted_by_age = sorted(products, key=lambda x: calculate_days_owned(x["purchase_date"]), reverse=True)[:4]
        
        cols = st.columns(len(sorted_by_age))
        for idx, p in enumerate(sorted_by_age):
            days = calculate_days_owned(p["purchase_date"])
            with cols[idx]:
                st.markdown(f"""
                <div class="vanity-card" style="padding:1rem;">
                    <span class="lilac-badge">#{idx+1} OLDEST</span>
                    <h5 style="margin:0.5rem 0 0.2rem 0; font-size:0.95rem;">{p['brand']}</h5>
                    <p style="font-size:0.8rem; color:#7d6b98; margin:0;">{p['name']}</p>
                    <p style="color:#5d3b8e; font-weight:600; font-size:0.85rem; margin-top:0.4rem;">{days} days old</p>
                </div>
                """, unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 5: ADD PRODUCT
# ---------------------------------------------------------
elif nav == "Add Product":
    st.markdown("### Add New Product")
    stats = st.session_state.db.get("stats", {})
    fin_lips = stats.get("finished_lip_products", 0)
    earned_tokens = fin_lips // 5

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

        if st.form_submit_button("Add to Sanctuary ✨"):
            if name and brand:
                if category.lower() in LIP_CATEGORIES:
                    if earned_tokens > 0:
                        st.info("Used 1 Lip Credit for this purchase.")
                    else:
                        st.session_state.db["stats"]["penalties"] = st.session_state.db["stats"].get("penalties", 0) + 1
                        st.warning("Penalty recorded: Purchased a lip product without 5 prior finishes.")

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
                st.rerun()
            else:
                st.error("Please enter Name and Brand.")
 
