import streamlit as st
import pandas as pd
import datetime
import os
import json
import base64
from PIL import Image
import io

# ---------------------------------------------------------
# Page Configuration & Cute Gothic Violet Theme Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Project Pan — Gothic Vanity",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Gothic Violet Aesthetics
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700;900&family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');

    .stApp {
        background-color: #0d0814;
        color: #e2d9f3;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cinzel', serif !important;
        color: #d8b4fe !important;
        letter-spacing: 1px;
    }

    .gothic-header {
        background: linear-gradient(135deg, #1f1035 0%, #2e1052 50%, #120722 100%);
        border: 1px solid #6b21a8;
        box-shadow: 0 4px 20px rgba(147, 51, 234, 0.25);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .gothic-header h1 {
        font-size: 2.2rem !important;
        margin: 0 !important;
        text-shadow: 0 0 10px rgba(192, 132, 252, 0.5);
    }

    .gothic-header p {
        color: #a855f7;
        font-style: italic;
        margin-top: 0.5rem;
        font-size: 0.95rem;
    }

    [data-testid="stSidebar"] {
        background-color: #12091f;
        border-right: 1px solid #3b0764;
    }

    .vanity-card {
        background-color: #1a0f2e;
        border: 1px solid #4c1d95;
        border-radius: 14px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
    }

    .gothic-badge {
        background-color: #3b0764;
        color: #f3e8ff;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        border: 1px solid #7e22ce;
        display: inline-block;
        font-weight: 600;
    }

    .metric-box {
        background-color: #24123e;
        border: 1px solid #5b21b6;
        padding: 0.75rem;
        border-radius: 10px;
        text-align: center;
    }
    .metric-box .metric-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #c084fc;
        font-family: 'Cinzel', serif;
    }
    .metric-box .metric-label {
        font-size: 0.75rem;
        color: #a855f7;
        text-transform: uppercase;
    }

    .stButton > button {
        background: linear-gradient(135deg, #6b21a8 0%, #3b0764 100%);
        color: #f3e8ff;
        border: 1px solid #a855f7;
        border-radius: 8px;
        font-family: 'Cinzel', serif;
        font-weight: 600;
        width: 100%;
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
            return {"products": []}
    return {"products": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

if "db" not in st.session_state:
    st.session_state.db = load_data()

# ---------------------------------------------------------
# Helper Calculations
# ---------------------------------------------------------
def calculate_days_owned(purchase_date_str):
    try:
        p_date = datetime.datetime.strptime(purchase_date_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        days = (today - p_date).days
        return max(days, 0)
    except Exception:
        return 0

def calculate_cost_per_use(price, total_uses):
    if total_uses <= 0:
        return price
    return price / total_uses

def calculate_pan_projection(capacity, daily_uses, unit):
    if daily_uses <= 0:
        return "N/A"
    
    estimated_use_per_application = 0.08 if unit in ["ml", "g"] else 1
    total_est_applications = capacity / estimated_use_per_application if capacity > 0 else 200
    
    days_to_finish = total_est_applications / daily_uses
    months = days_to_finish / 30.4
    
    if months < 1:
        return f"~{int(days_to_finish)} days"
    elif months < 12:
        return f"~{round(months, 1)} months"
    else:
        years = months / 12
        return f"~{round(years, 1)} years"

def image_to_base64(uploaded_file):
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        image.thumbnail((400, 400))
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    return None

# ---------------------------------------------------------
# Header Banner & Sidebar Navigation
# ---------------------------------------------------------
st.markdown("""
<div class="gothic-header">
    <h1>🔮 Gothic Vanity & Project Pan 🔮</h1>
    <p>Track your beauty treasures, log uses, and finish your potions.</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<h2 style='text-align:center;'>🕸️ Sanctuary 🕸️</h2>", unsafe_allow_html=True)
nav = st.sidebar.radio(
    "Navigation", 
    ["✨ Full Collection", "🧪 Project Pan Sanctuary", "➕ Add New Potion"]
)

# ---------------------------------------------------------
# TAB 1: FULL COLLECTION
# ---------------------------------------------------------
if nav == "✨ Full Collection":
    st.markdown("### 🖤 Full Vanity Collection")
    products = st.session_state.db.get("products", [])

    if not products:
        st.info("Your vanity is empty. Click on '➕ Add New Potion' in the sidebar!")
    else:
        filter_cat = st.selectbox("Filter Category:", ["All Categories"] + CATEGORIES)
        filtered_products = products
        if filter_cat != "All Categories":
            filtered_products = [p for p in filtered_products if p["category"].lower() == filter_cat.lower()]

        st.markdown(f"**Showing `{len(filtered_products)}` potion(s)**")

        for p in reversed(filtered_products):
            days = calculate_days_owned(p["purchase_date"])
            cpu = calculate_cost_per_use(p["price"], p.get("total_uses", 0))

            st.markdown(f"""
            <div class="vanity-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h3 style="margin:0;">{p['brand']} — {p['name']}</h3>
                        <p style="margin:2px 0; color:#c084fc;">Shade: {p['shade']}</p>
                    </div>
                    <span class="gothic-badge">{p['category'].upper()}</span>
                </div>
            """, unsafe_allow_html=True)

            col_img, col_info = st.columns([1, 1.8])
            with col_img:
                if p.get("image_b64"):
                    st.markdown(f'<img src="data:image/png;base64,{p["image_b64"]}" style="width:100%; border-radius:10px; border:1px solid #6b21a8;">', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="width:100%; aspect-ratio:1; background-color:#2a1745; border-radius:10px; display:flex; align-items:center; justify-content:center;"><span style="font-size:2rem;">🔮</span></div>', unsafe_allow_html=True)

            with col_info:
                st.markdown(f"""
                **Price:** `{p['price']:.2f} {p['currency']}`  
                **Age:** `{days}` days owned  
                **Total Uses:** `{p.get('total_uses', 0)}`  
                **Cost per Use:** `{cpu:.2f} {p['currency']}`  
                **Size:** `{p.get('capacity', 'N/A')} {p.get('unit', '')}`
                """, unsafe_allow_html=True)

            is_pan = p.get("in_project_pan", False)
            btn_label = "Remove from Pan" if is_pan else "Add to Project Pan 🧪"
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button(btn_label, key=f"pan_toggle_{p['id']}"):
                    p["in_project_pan"] = not is_pan
                    save_data(st.session_state.db)
                    st.rerun()
            with c2:
                if st.button("🗑️ Delete Potion", key=f"del_{p['id']}"):
                    st.session_state.db["products"] = [item for item in st.session_state.db["products"] if item["id"] != p["id"]]
                    save_data(st.session_state.db)
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 2: PROJECT PAN SANCTUARY
# ---------------------------------------------------------
elif nav == "🧪 Project Pan Sanctuary":
    st.markdown("### 🧪 Active Project Pan Items")
    products = [p for p in st.session_state.db.get("products", []) if p.get("in_project_pan", False)]

    if not products:
        st.info("No items in Project Pan! Go to '✨ Full Collection' to select products to pan.")
    else:
        for p in products:
            days = calculate_days_owned(p["purchase_date"])
            total_uses = p.get("total_uses", 0)
            cpu = calculate_cost_per_use(p["price"], total_uses)
            daily_uses = p.get("daily_uses", 1.0)
            projection = calculate_pan_projection(p.get("capacity", 0), daily_uses, p.get("unit", "g"))

            st.markdown(f"""
            <div class="vanity-card">
                <h3 style="margin:0;">{p['brand']} — {p['name']} ({p['shade']})</h3>
            """, unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)
            with m1:
                st.markdown(f'<div class="metric-box"><div class="metric-value">{days} d</div><div class="metric-label">Days Owned</div></div>', unsafe_allow_html=True)
            with m2:
                st.markdown(f'<div class="metric-box"><div class="metric-value">{total_uses}</div><div class="metric-label">Total Uses</div></div>', unsafe_allow_html=True)
            with m3:
                st.markdown(f'<div class="metric-box"><div class="metric-value">{cpu:.2f} {p["currency"]}</div><div class="metric-label">Cost / Use</div></div>', unsafe_allow_html=True)

            st.markdown(f"⏳ **Est. Time to Finish:** `{projection}` (at `{daily_uses}` uses/day)")

            st.markdown("#### 📝 Log Today's Usage")
            col_add, col_btn = st.columns([2, 1])
            with col_add:
                add_uses = st.number_input("Add uses today:", min_value=1, max_value=10, value=1, key=f"uses_{p['id']}")
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("➕ Log Uses", key=f"btn_{p['id']}"):
                    p["total_uses"] = p.get("total_uses", 0) + add_uses
                    save_data(st.session_state.db)
                    st.success("Logged!")
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TAB 3: ADD NEW POTION
# ---------------------------------------------------------
elif nav == "➕ Add New Potion":
    st.markdown("### 🔮 Add a New Potion")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Product Name *")
        brand = st.text_input("Brand *")
        shade = st.text_input("Shade / Color")
        category = st.selectbox("Category *", CATEGORIES)
        
        c1, c2 = st.columns(2)
        with c1:
            price = st.number_input("Price *", min_value=0.0, value=20.0)
            currency = st.selectbox("Currency *", ["PLN", "GBP"])
            purchase_date = st.date_input("Purchase Date *", datetime.date.today())
        with c2:
            capacity = st.number_input("Capacity / Size", min_value=0.0, value=30.0)
            unit = st.selectbox("Unit", ["ml", "g", "items"])
            daily_uses = st.number_input("Target Daily Uses", min_value=0.1, value=1.0)

        in_pan = st.checkbox("Add directly to Project Pan?", value=True)
        uploaded_img = st.file_uploader("Upload Photo", type=["jpg", "jpeg", "png"])

        if st.form_submit_button("✨ Add to Vanity"):
            if name and brand:
                img_b64 = image_to_base64(uploaded_img) if uploaded_img else None
                new_item = {
                    "id": str(datetime.datetime.now().timestamp()),
                    "name": name, "brand": brand, "shade": shade if shade else "N/A",
                    "category": category, "price": float(price), "currency": currency,
                    "purchase_date": str(purchase_date), "capacity": float(capacity),
                    "unit": unit, "daily_uses": float(daily_uses), "total_uses": 0,
                    "in_project_pan": in_pan, "image_b64": img_b64
                }
                st.session_state.db["products"].append(new_item)
                save_data(st.session_state.db)
                st.success(f"Added '{brand} - {name}'!")
            else:
                st.error("Fill in Name & Brand!")
