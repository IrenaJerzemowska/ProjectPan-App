import streamlit as st
import pandas as pd
import datetime
import os
import json
import base64
from PIL import Image
import io
import random

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

    .stApp {
        background-color: #d8cde9 !important;
        color: #382a4b;
        font-family: 'Lora', serif;
    }

    .block-container {
        max-width: 480px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .sanctuary-header {
        background: #ffffff;
        border-radius: 6px;
        padding: 1.8rem 1rem 1.4rem 1rem;
        text-align: center;
        margin-bottom: 16px;
        box-shadow: 0 4px 15px rgba(120, 100, 150, 0.04);
    }

    .sanctuary-header h1 {
        font-family: 'Playfair Display', serif !important;
        font-size: 2.2rem !important;
        color: #3a3342 !important;
        margin: 0 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    .sanctuary-header p {
        color: #b5a4c9;
        font-size: 1.15rem;
        font-family: 'Playfair Display', serif;
        font-style: italic;
        margin-top: 0.3rem;
        margin-bottom: 0;
        font-weight: 400;
    }

    .quote-card {
        background: #ffffff;
        border: 1px solid #e2d8ee;
        border-radius: 6px;
        padding: 2.2rem 1rem;
        text-align: center;
        margin-top: 12px;
        box-shadow: 0 4px 12px rgba(100, 80, 130, 0.04);
    }

    .quote-card p {
        font-family: 'Lora', serif;
        color: #5c5366;
        font-size: 1.25rem;
        margin: 0;
        line-height: 1.45;
        letter-spacing: 0.2px;
    }

    .vanity-card {
        background: #ffffff;
        border-radius: 6px;
        border: 1px solid #e9e2f4;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 3px 10px rgba(130, 110, 160, 0.04);
    }

    .metric-box {
        background: #f7f3fd;
        border: 1px solid #dcd0f0;
        padding: 0.8rem;
        border-radius: 6px;
        text-align: center;
    }
    .metric-box .metric-value {
        font-size: 1.3rem;
        font-weight: 600;
        color: #4a3468;
        font-family: 'Playfair Display', serif;
    }
    .metric-box .metric-label {
        font-size: 0.65rem;
        color: #8c7aa9;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 2px;
    }

    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div, div[data-baseweb="base-input"] {
        background-color: #ffffff !important;
        border-color: #dcd0f0 !important;
        border-radius: 6px !important;
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
    "eyeliner", "mascara", "lip liner", "lip mask", "lip balm",
    "setting spray", "brow gel", "brow pen"
]

LIP_CATEGORIES = ["lip gloss", "lipstick", "lip liner", "lip mask", "lip balm"]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "products" not in data: data["products"] = []
                if "wishlist" not in data: data["wishlist"] = []
                if "empties" not in data: data["empties"] = []
                if "stats" not in data: 
                    data["stats"] = {"finished_lip_products": 0, "no_buy_start_date": str(datetime.date.today()), "xp": 0, "rewards_redeemed": 0}
                if "no_buy_start_date" not in data["stats"]: data["stats"]["no_buy_start_date"] = str(datetime.date.today())
                if "xp" not in data["stats"]: data["stats"]["xp"] = 0
                if "finished_lip_products" not in data["stats"]: data["stats"]["finished_lip_products"] = 0
                if "rewards_redeemed" not in data["stats"]: data["stats"]["rewards_redeemed"] = 0
                return data
        except Exception:
            return {"products": [], "wishlist": [], "empties": [], "stats": {"finished_lip_products": 0, "no_buy_start_date": str(datetime.date.today()), "xp": 0, "rewards_redeemed": 0}}
    return {"products": [], "wishlist": [], "empties": [], "stats": {"finished_lip_products": 0, "no_buy_start_date": str(datetime.date.today()), "xp": 0, "rewards_redeemed": 0}}

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

def get_pan_level(xp):
    if xp < 50: return "Novice Panner 🌱", 50
    elif xp < 150: return "Consistent Enthusiast 🌿", 150
    elif xp < 300: return "Expert Finisher 🌸", 300
    else: return "Master of the Pan 👑", 500

def estimate_pan_completion(category, daily_uses):
    if daily_uses <= 0: return None, None, 0
    cat = category.lower()
    
    if "lipstick" in cat: days_needed_base = 730 
    elif "liquid lipstick" in cat: days_needed_base = 270 
    elif "lip gloss" in cat: days_needed_base = 135 
    elif "lip balm" in cat: days_needed_base = 90    
    elif "lip mask" in cat: days_needed_base = 225 
    elif "foundation" in cat: days_needed_base = 150 
    elif "concealer" in cat: days_needed_base = 225 
    elif "powder" in cat: days_needed_base = 300 
    elif "setting spray" in cat: days_needed_base = 120 
    elif "contour" in cat: days_needed_base = 300 
    elif "blush" in cat: days_needed_base = 365 
    elif "highlighter" in cat: days_needed_base = 540 
    elif "eyeshadow palette" in cat: days_needed_base = 1095 
    elif "mascara" in cat: days_needed_base = 120 
    elif "eyeliner" in cat: days_needed_base = 210 
    elif "brow pen" in cat: days_needed_base = 120 
    elif "brow gel" in cat: days_needed_base = 150 
    else: days_needed_base = 250

    days_needed = int(days_needed_base / daily_uses)
    completion_date = datetime.date.today() + datetime.timedelta(days=max(days_needed, 1))
    return days_needed, completion_date, days_needed_base

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
# PAGE ROUTING
# ---------------------------------------------------------
if st.session_state.current_page == "Home":
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Your\nCollection\n\n🦇", key="btn_coll", use_container_width=True):
            st.session_state.current_page = "Collection"
            st.rerun()
    with col2:
        if st.button("Project\nPan\n\n🌕", key="btn_pan", use_container_width=True):
            st.session_state.current_page = "Project Pan"
            st.rerun()

    col3, col4 = st.columns(2)
    with col3:
        if st.button("Wishlist\n\n✨", key="btn_wishlist", use_container_width=True):
            st.session_state.current_page = "Wishlist"
            st.rerun()
    with col4:
        if st.button("No - Buy\n& Rewards\n\n🌸", key="btn_nobuy", use_container_width=True):
            st.session_state.current_page = "No-Buy Rules"
            st.rerun()

    if st.button("Beauty Stats 🐈‍⬛", key="btn_stats", use_container_width=True):
        st.session_state.current_page = "Analytics"
        st.rerun()

    st.markdown("""
    <div class="quote-card">
        <p>Use what you love.<br>Finish what you start.</p>
    </div>
    """, unsafe_allow_html=True)

else:
    if st.button("← Back to Menu"):
        st.session_state.current_page = "Home"
        st.rerun()

    st.markdown("---")

    # --- COLLECTION ---
    if st.session_state.current_page == "Collection":
        st.markdown("### Your Collection")
        
        col_c_btn1, col_c_btn2 = st.columns(2)
        with col_c_btn1:
            if st.button("+ Add New Product"):
                st.session_state.current_page = "Add Product"
                st.rerun()
        with col_c_btn2:
            if st.button("Empties Graveyard 🪦"):
                st.session_state.current_page = "Empties"
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        products = st.session_state.db.get("products", [])
        finishing_id_key = "finishing_product_id"

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
                is_pan = p.get("in_project_pan", False)
                edit_mode_key = f"edit_mode_{p['id']}"

                st.markdown(f"""
                <div class="vanity-card">
                    <h4 style="margin:0 0 0.4rem 0; font-family:'Playfair Display', serif;">{p['brand']} — <span style="font-weight:400;">{p['shade']}</span></h4>
                    <p style="margin:0 0 0.6rem 0; color:#8c7aa9; font-size:0.88rem;">Category: {p['category']}</p>
                    <p style="margin:0; font-size:0.9rem;"><strong>Price:</strong> {p['price']:.2f} {p['currency']} | <strong>Age:</strong> {days} days | <strong>Uses:</strong> {p.get('total_uses', 0)} | <strong>CPU:</strong> {cpu:.2f} {p['currency']}</p>
                """, unsafe_allow_html=True)

                if is_pan:
                    st.markdown("<hr style='margin: 10px 0; border-color: #eee0f8;'>", unsafe_allow_html=True)
                    col_info, col_act = st.columns([2, 1])
                    with col_info:
                        st.markdown("<p style='font-size:0.8rem; color:#6b5b7a; margin:0;'>✨ Active in Project Pan</p>", unsafe_allow_html=True)
                    with col_act:
                        if st.button("+ Log Use", key=f"quick_use_{p['id']}"):
                            p["total_uses"] = p.get("total_uses", 0) + 1
                            if "stats" not in st.session_state.db: st.session_state.db["stats"] = {"xp": 0}
                            st.session_state.db["stats"]["xp"] = max(st.session_state.db["stats"].get("xp", 0) + 5, 0)
                            save_data(st.session_state.db)
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

                if edit_mode_key not in st.session_state: st.session_state[edit_mode_key] = False

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    if st.button("Unpan" if is_pan else "Pan ✨", key=f"pan_{p['id']}"):
                        p["in_project_pan"] = not is_pan
                        save_data(st.session_state.db)
                        st.rerun()
                with c2:
                    if st.button("Edit ✏️", key=f"edit_toggle_{p['id']}"):
                        st.session_state[edit_mode_key] = not st.session_state[edit_mode_key]
                        st.rerun()
                with c3:
                    if st.button("Finish 🎉", key=f"fin_{p['id']}"):
                        st.session_state[finishing_id_key] = p["id"]
                        st.rerun()
                with c4:
                    if st.button("Delete 🗑️", key=f"del_{p['id']}"):
                        st.session_state.db["products"] = [item for item in st.session_state.db["products"] if item["id"] != p["id"]]
                        save_data(st.session_state.db)
                        st.rerun()

                if st.session_state.get(finishing_id_key) == p["id"]:
                    with st.form(key=f"review_form_{p['id']}"):
                        st.markdown(f"**Review & Grade Finished Product: {p['brand']} - {p['shade']}**")
                        finish_rating = st.slider("Rating (Stars)", 0, 5, 5, 1)
                        finish_review = st.text_area("Thoughts / Mini Review:")
                        rc1, rc2 = st.columns(2)
                        with rc1: submit_review = st.form_submit_button("Complete & Archive 🪦")
                        with rc2: cancel_review = st.form_submit_button("Cancel")
                        
                        if submit_review:
                            is_lip = p["category"].lower() in LIP_CATEGORIES
                            if is_lip:
                                st.session_state.db["stats"]["finished_lip_products"] = st.session_state.db["stats"].get("finished_lip_products", 0) + 1
                            
                            empty_item = p.copy()
                            empty_item["finished_date"] = str(datetime.date.today())
                            empty_item["final_days_owned"] = calculate_days_owned(p["purchase_date"])
                            empty_item["final_cpu"] = calculate_cost_per_use(p["price"], p.get("total_uses", 0))
                            empty_item["rating"] = finish_rating
                            empty_item["review"] = finish_review
                            
                            if "empties" not in st.session_state.db: st.session_state.db["empties"] = []
                            st.session_state.db["empties"].append(empty_item)
                            st.session_state.db["stats"]["xp"] = max(st.session_state.db["stats"].get("xp", 0) + 50, 0)
                            st.session_state.db["products"] = [item for item in st.session_state.db["products"] if item["id"] != p["id"]]
                            st.session_state[finishing_id_key] = None
                            save_data(st.session_state.db)
                            st.rerun()
                        if cancel_review:
                            st.session_state[finishing_id_key] = None
                            st.rerun()

                if st.session_state.get(edit_mode_key):
                    with st.form(key=f"edit_form_{p['id']}"):
                        new_brand = st.text_input("Brand", value=p["brand"])
                        new_shade = st.text_input("Shade", value=p["shade"] if p["shade"] != "N/A" else "")
                        new_category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(p["category"].lower()) if p["category"].lower() in CATEGORIES else 0)
                        new_price = st.number_input("Price", min_value=0.0, value=float(p["price"]))
                        new_currency = st.selectbox("Currency", ["GBP", "PLN", "EUR", "USD"], index=["GBP", "PLN", "EUR", "USD"].index(p["currency"]) if p["currency"] in ["GBP", "PLN", "EUR", "USD"] else 0)
                        
                        old_uses = p.get("total_uses", 0)
                        new_uses_input = st.number_input("Total Uses", min_value=0, value=int(old_uses))

                        if st.form_submit_button("Save Changes ✓"):
                            uses_diff = int(new_uses_input) - int(old_uses)
                            p["brand"] = new_brand
                            p["shade"] = new_shade if new_shade else "N/A"
                            p["category"] = new_category
                            p["price"] = float(new_price)
                            p["currency"] = new_currency
                            p["total_uses"] = int(new_uses_input)
                            
                            if uses_diff != 0:
                                if "stats" not in st.session_state.db: st.session_state.db["stats"] = {"xp": 0}
                                current_xp = st.session_state.db["stats"].get("xp", 0)
                                st.session_state.db["stats"]["xp"] = max(current_xp + (uses_diff * 5), 0)

                            save_data(st.session_state.db)
                            st.session_state[edit_mode_key] = False
                            st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

    # --- ADD PRODUCT ---
    elif st.session_state.current_page == "Add Product":
        st.markdown("### Add New Product")
        with st.form("add_product_form"):
            brand = st.text_input("Brand")
            shade = st.text_input("Shade / Variant (Optional)")
            category = st.selectbox("Category", CATEGORIES)
            price = st.number_input("Price", min_value=0.0, value=0.0)
            currency = st.selectbox("Currency", ["GBP", "PLN", "EUR", "USD"])
            purchase_date = st.date_input("Purchase Date", value=datetime.date.today())
            capacity = st.number_input("Capacity / Size", min_value=0.0, value=10.0)
            unit = st.selectbox("Unit", ["ml", "g", "items"])
            initial_uses = st.number_input("Initial Uses", min_value=0, value=0)

            if st.form_submit_button("Add to Collection ✨"):
                if not brand:
                    st.error("Please enter a brand name.")
                else:
                    new_item = {
                        "id": str(random.randint(100000, 999999)),
                        "brand": brand,
                        "shade": shade if shade else "N/A",
                        "category": category,
                        "price": float(price),
                        "currency": currency,
                        "purchase_date": str(purchase_date),
                        "capacity": float(capacity),
                        "unit": unit,
                        "total_uses": int(initial_uses),
                        "in_project_pan": False
                    }
                    st.session_state.db["products"].append(new_item)
                    
                    if int(initial_uses) > 0:
                        if "stats" not in st.session_state.db: st.session_state.db["stats"] = {"xp": 0}
                        current_xp = st.session_state.db["stats"].get("xp", 0)
                        st.session_state.db["stats"]["xp"] = max(current_xp + (int(initial_uses) * 5), 0)

                    save_data(st.session_state.db)
                    st.success("Product added!")
                    st.session_state.current_page = "Collection"
                    st.rerun()

    # --- EMPTIES GRAVEYARD ---
    elif st.session_state.current_page == "Empties":
        st.markdown("### Empties Graveyard 🪦")
        empties = st.session_state.db.get("empties", [])
        if not empties:
            st.info("No empty products archived yet.")
        else:
            for e in reversed(empties):
                st.markdown(f"""
                <div class="vanity-card">
                    <h4 style="margin:0 0 0.3rem 0; font-family:'Playfair Display', serif;">{e['brand']} — {e['shade']}</h4>
                    <p style="margin:0 0 0.4rem 0; color:#8c7aa9; font-size:0.85rem;">Finished on {e.get('finished_date', 'Unknown')} | Rating: {'⭐' * e.get('rating', 0)}</p>
                    <p style="margin:0; font-size:0.88rem;">Lifespan: {e.get('final_days_owned', 0)} days | Total Uses: {e.get('total_uses', 0)}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Delete from Graveyard 🗑️", key=f"del_empty_{e['id']}"):
                    st.session_state.db["empties"] = [item for item in st.session_state.db["empties"] if item["id"] != e["id"]]
                    save_data(st.session_state.db)
                    st.rerun()

    # --- PROJECT PAN ---
    elif st.session_state.current_page == "Project Pan":
        st.markdown("### Project Pan (Gamified) 🌕")
        
        current_xp = st.session_state.db.get("stats", {}).get("xp", 0)
        current_level_title, _ = get_pan_level(current_xp)
        
        st.markdown(f"""
        <div class="vanity-card" style="background-color: #f7f3fd; text-align: center;">
            <h4 style="margin:0; font-family:'Playfair Display', serif; color:#4a3468;">Rank: {current_level_title}</h4>
            <p style="margin:5px 0 0 0; font-size: 0.9rem; color:#8c7aa9;">Total XP: <b>{current_xp} XP</b> (+5 XP per added use, -5 XP per removed use!)</p>
        </div>
        """, unsafe_allow_html=True)

        products = [p for p in st.session_state.db.get("products", []) if p.get("in_project_pan", False)]
        products = sorted(products, key=lambda x: x.get("purchase_date", "9999-12-31"))

        if not products:
            st.info("No active items in Project Pan. Tag items as panned from your collection.")
        else:
            for p in products:
                days = calculate_days_owned(p["purchase_date"])
                total_uses = p.get("total_uses", 0)
                cpu = calculate_cost_per_use(p["price"], total_uses)

                st.markdown(f"""
                <div class="vanity-card">
                    <h4 style="margin:0 0 1rem 0; font-family:'Playfair Display', serif;">{p['brand']} — {p['shade']}</h4>
                """, unsafe_allow_html=True)

                m1, m2, m3 = st.columns(3)
                with m1: st.markdown(f'<div class="metric-box"><div class="metric-value">{days}</div><div class="metric-label">Days Owned</div></div>', unsafe_allow_html=True)
                with m2: st.markdown(f'<div class="metric-box"><div class="metric-value">{total_uses}</div><div class="metric-label">Uses</div></div>', unsafe_allow_html=True)
                with m3: st.markdown(f'<div class="metric-box"><div class="metric-value">{cpu:.2f} {p["currency"]}</div><div class="metric-label">Cost / Use</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                daily_uses_input = st.number_input("Estimated daily applications:", min_value=1, max_value=5, value=1, key=f"d_uses_{p['id']}")
                d_needed, target_date, total_apps_needed = estimate_pan_completion(p["category"], daily_uses_input)
                
                if d_needed and total_apps_needed > 0:
                    progress_ratio = min(float(total_uses) / total_apps_needed, 1.0)
                    st.markdown(f"""
                    <div style="background-color: #f2ebfc; border-radius: 6px; padding: 0.8rem; margin-top: 10px; font-size: 0.88rem; color: #4a3468;">
                        🔮 <strong>Forecast:</strong> Approx. <b>{d_needed} days</b> ({target_date.strftime('%B %Y')}) to finish.
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(progress_ratio)

                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown("<p style='font-size:0.85rem; color:#8c7aa9; margin-bottom:5px;'>Quick Use Counter:</p>", unsafe_allow_html=True)
                col_btn_minus, col_uses_disp, col_btn_plus = st.columns([1, 2, 1])
                with col_btn_minus:
                    if st.button("➖ -1", key=f"minus_{p['id']}"):
                        if p.get("total_uses", 0) > 0:
                            p["total_uses"] = p.get("total_uses", 0) - 1
                            if "stats" not in st.session_state.db: st.session_state.db["stats"] = {"xp": 0}
                            current_xp = st.session_state.db["stats"].get("xp", 0)
                            st.session_state.db["stats"]["xp"] = max(current_xp - 5, 0)
                            save_data(st.session_state.db)
                            st.rerun()
                with col_uses_disp:
                    st.markdown(f"<div style='text-align: center; padding-top: 5px; font-weight: bold;'>{total_uses} uses</div>", unsafe_allow_html=True)
                with col_btn_plus:
                    if st.button("➕ +1", key=f"plus_{p['id']}"):
                        p["total_uses"] = p.get("total_uses", 0) + 1
                        if "stats" not in st.session_state.db: st.session_state.db["stats"] = {"xp": 0}
                        current_xp = st.session_state.db["stats"].get("xp", 0)
                        st.session_state.db["stats"]["xp"] = max(current_xp + 5, 0)
                        save_data(st.session_state.db)
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

    # --- WISHLIST ---
    elif st.session_state.current_page == "Wishlist":
        st.markdown("### Wishlist ✨")
        st.markdown("<p style='color:#8c7aa9; font-size:0.9rem;'>Track items you are considering before buying.</p>", unsafe_allow_html=True)

        with st.form("add_wishlist_form"):
            w_brand = st.text_input("Brand")
            w_item = st.text_input("Item Name / Shade")
            w_price = st.number_input("Estimated Price", min_value=0.0, value=0.0)
            w_currency = st.selectbox("Currency", ["GBP", "PLN", "EUR", "USD"], key="w_curr")
            w_notes = st.text_area("Why do you want this? Any dupes you own?")
            
            if st.form_submit_button("Add to Wishlist"):
                if not w_brand:
                    st.error("Please enter a brand.")
                else:
                    if "wishlist" not in st.session_state.db: st.session_state.db["wishlist"] = []
                    st.session_state.db["wishlist"].append({
                        "id": str(random.randint(100000, 999999)),
                        "brand": w_brand,
                        "item": w_item,
                        "price": float(w_price),
                        "currency": w_currency,
                        "notes": w_notes
                    })
                    save_data(st.session_state.db)
                    st.success("Added to wishlist!")
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        wishlist_items = st.session_state.db.get("wishlist", [])
        if not wishlist_items:
            st.info("Your wishlist is empty.")
        else:
            for w in wishlist_items:
                st.markdown(f"""
                <div class="vanity-card">
                    <h4 style="margin:0 0 0.3rem 0; font-family:'Playfair Display', serif;">{w['brand']} — {w['item']}</h4>
                    <p style="margin:0 0 0.3rem 0; color:#8c7aa9; font-size:0.85rem;">Price: {w['price']:.2f} {w['currency']}</p>
                    <p style="margin:0; font-size:0.88rem; font-style:italic;">{w.get('notes', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Remove 🗑️", key=f"del_wish_{w['id']}"):
                    st.session_state.db["wishlist"] = [item for item in st.session_state.db["wishlist"] if item["id"] != w["id"]]
                    save_data(st.session_state.db)
                    st.rerun()

    # --- NO-BUY & REWARDS ---
    elif st.session_state.current_page == "No-Buy Rules":
        st.markdown("### No-Buy & Rewards 🌸")
        
        stats = st.session_state.db.get("stats", {})
        start_date_str = stats.get("no_buy_start_date", str(datetime.date.today()))
        try:
            parsed_start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except Exception:
            parsed_start_date = datetime.date.today()
            
        days_on_no_buy = max((datetime.date.today() - parsed_start_date).days, 0)
        finished_lips = stats.get("finished_lip_products", 0)
        rewards_redeemed = stats.get("rewards_redeemed", 0)
        available_rewards = (finished_lips // 5) - rewards_redeemed

        st.markdown(f"""
        <div class="vanity-card">
            <h4 style="margin:0 0 0.5rem 0; font-family:'Playfair Display', serif;">No-Buy Streak Tracker</h4>
            <p style="margin:0; font-size:1.1rem;">You have been strong for <b>{days_on_no_buy} days</b>!</p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("no_buy_date_form"):
            new_start_date = st.date_input("Set or adjust No-Buy start date:", value=parsed_start_date)
            if st.form_submit_button("Update Start Date ✓"):
                st.session_state.db["stats"]["no_buy_start_date"] = str(new_start_date)
                save_data(st.session_state.db)
                st.success("No-buy start date updated successfully!")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚨 Oops, I bought something (Reset Streak & -50 XP)"):
            st.session_state.db["stats"]["no_buy_start_date"] = str(datetime.date.today())
            current_xp_val = st.session_state.db["stats"].get("xp", 0)
            st.session_state.db["stats"]["xp"] = max(current_xp_val - 50, 0)
            save_data(st.session_state.db)
            st.warning("No-buy streak reset to today, and -50 XP penalty applied.")
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="vanity-card" style="background-color: #f7f3fd;">
            <h4 style="margin:0 0 0.5rem 0; font-family:'Playfair Display', serif;">Lip Product Empties Reward System</h4>
            <p style="margin:0 0 0.4rem 0; font-size:0.9rem;">Finish <b>5 lip products</b> (lip gloss, lipstick, lip liner, lip mask, or lip balm) = Unlock 1 reward!</p>
            <p style="margin:0; font-size:0.95rem;">Progress: <b>{finished_lips % 5} / 5</b> toward next reward (Total finished lips: {finished_lips})</p>
            <p style="margin:5px 0 0 0; font-size:0.95rem; color:#4a3468;"><b>Available Rewards to Redeem:</b> {max(available_rewards, 0)}</p>
        </div>
        """, unsafe_allow_html=True)

        if available_rewards > 0:
            if st.button("🎁 Redeem Reward!"):
                st.session_state.db["stats"]["rewards_redeemed"] = rewards_redeemed + 1
                save_data(st.session_state.db)
                st.success("Reward redeemed! Enjoy treating yourself!")
                st.rerun()

    # --- ANALYTICS ---
    elif st.session_state.current_page == "Analytics":
        st.markdown("### Beauty Stats 🐈‍⬛")
        products = st.session_state.db.get("products", [])
        empties = st.session_state.db.get("empties", [])
        
        total_items = len(products)
        total_spent = sum(p.get("price", 0) for p in products)
        total_empties = len(empties)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="metric-box"><div class="metric-value">{total_items}</div><div class="metric-label">Active Items</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-box"><div class="metric-value">{total_empties}</div><div class="metric-label">Empties</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="vanity-card">
            <h4 style="margin:0 0 0.5rem 0; font-family:'Playfair Display', serif;">Collection Overview</h4>
            <p style="margin:0; font-size:0.95rem;">Total Estimated Value: <b>{total_spent:.2f}</b></p>
        </div>
        """, unsafe_allow_html=True)
