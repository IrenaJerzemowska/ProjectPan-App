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

    /* Clean Solid Lilac Background */
    .stApp {
        background-color: #d8cde9 !important;
        color: #382a4b;
        font-family: 'Lora', serif;
    }

    /* Container Constrain */
    .block-container {
        max-width: 480px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Header Styling */
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

    /* Bottom Quote Card */
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

    /* Inner Cards - Coherent Radius & Style */
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

    /* Inputs Fix for Coherency */
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
                if "products" not in data:
                    data["products"] = []
                if "wishlist" not in data:
                    data["wishlist"] = []
                if "empties" not in data:
                    data["empties"] = []
                if "stats" not in data:
                    data["stats"] = {"finished_lip_products": 0, "no_buy_start_date": str(datetime.date.today()), "xp": 0}
                if "no_buy_start_date" not in data["stats"]:
                    data["stats"]["no_buy_start_date"] = str(datetime.date.today())
                if "xp" not in data["stats"]:
                    data["stats"]["xp"] = 0
                return data
        except Exception:
            return {"products": [], "wishlist": [], "empties": [], "settings": {}, "stats": {"finished_lip_products": 0, "no_buy_start_date": str(datetime.date.today()), "xp": 0}}
    return {"products": [], "wishlist": [], "empties": [], "settings": {}, "stats": {"finished_lip_products": 0, "no_buy_start_date": str(datetime.date.today()), "xp": 0}}

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
    if xp < 50:
        return "Novice Panner 🌱", 50
    elif xp < 150:
        return "Consistent Enthusiast 🌿", 150
    elif xp < 300:
        return "Expert Finisher 🌸", 300
    else:
        return "Master of the Pan 👑", 500

def estimate_pan_completion(category, capacity, unit, daily_uses):
    if daily_uses <= 0 or capacity <= 0:
        return None, None, 0
        
    cat = category.lower()
    if "foundation" in cat or "setting spray" in cat:
        ml_per_use = 0.75
    elif "concealer" in cat:
        ml_per_use = 0.15
    elif "lip" in cat:
        ml_per_use = 0.04
    elif "mascara" in cat:
        ml_per_use = 0.05
    elif "powder" in cat or "blush" in cat or "contour" in cat or "highlighter" in cat:
        ml_per_use = 0.08
    else:
        ml_per_use = 0.1

    total_applications_needed = capacity / ml_per_use
    days_needed = int(total_applications_needed / daily_uses)
    
    completion_date = datetime.date.today() + datetime.timedelta(days=max(days_needed, 1))
    return days_needed, completion_date, total_applications_needed

def image_to_base64(uploaded_file):
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            image.thumbnail((400, 400))
            buffered = io.BytesIO()
            image.convert("RGB").save(buffered, format="JPEG", quality=85)
            return base64.b64encode(buffered.getvalue()).decode()
        except Exception:
            return None
    return None

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
# PAGE 1: HOME
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
                            st.session_state.db["stats"]["xp"] = st.session_state.db["stats"].get("xp", 0) + 5
                            save_data(st.session_state.db)
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

                if edit_mode_key not in st.session_state:
                    st.session_state[edit_mode_key] = False

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    btn_label = "Unpan" if is_pan else "Pan ✨"
                    if st.button(btn_label, key=f"pan_{p['id']}"):
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
                        st.success("Product deleted.")
                        st.rerun()

                # Review & Rating Section when marking as finished
                if st.session_state.get(finishing_id_key) == p["id"]:
                    st.markdown(f"""
                    <div style="background-color: #f4ecfb; border: 1px solid #d4c2ec; border-radius: 6px; padding: 1.2rem; margin-top: 10px; margin-bottom: 10px;">
                        <h4 style="margin:0 0 0.3rem 0; font-family:'Playfair Display', serif; color:#4a3468;">🌟 Review & Grade Finished Product</h4>
                        <p style="margin:0; font-size:0.9rem; color:#5c5366;">How was your experience with <b>{p['brand']} - {p['shade']}</b>?</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.form(key=f"review_form_{p['id']}"):
                        finish_rating = st.slider("Rating (Stars)", min_value=0, max_value=5, value=5, step=1, help="0 stars is the worst, 5 stars is the best!")
                        finish_review = st.text_area("Write a short review or thoughts:")
                        
                        rc1, rc2 = st.columns(2)
                        with rc1:
                            submit_review = st.form_submit_button("Complete & Archive 🪦")
                        with rc2:
                            cancel_review = st.form_submit_button("Cancel")
                            
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
                            
                            if "empties" not in st.session_state.db:
                                st.session_state.db["empties"] = []
                            st.session_state.db["empties"].append(empty_item)
                            
                            st.session_state.db["stats"]["xp"] = st.session_state.db["stats"].get("xp", 0) + 50
                            st.session_state.db["products"] = [item for item in st.session_state.db["products"] if item["id"] != p["id"]]
                            st.session_state[finishing_id_key] = None
                            save_data(st.session_state.db)
                            
                            if is_lip and st.session_state.db["stats"]["finished_lip_products"] % 5 == 0:
                                st.session_state["show_lip_reward_banner"] = True
                            st.rerun()
                            
                        if cancel_review:
                            st.session_state[finishing_id_key] = None
                            st.rerun()

                if st.session_state[edit_mode_key]:
                    with st.form(key=f"edit_form_{p['id']}"):
                        st.markdown(f"**Edit details for {p['brand']} - {p['shade']}**")
                        new_brand = st.text_input("Brand", value=p["brand"])
                        new_shade = st.text_input("Shade / Variant", value=p["shade"] if p["shade"] != "N/A" else "")
                        
                        try:
                            cat_index = CATEGORIES.index(p["category"].lower())
                        except ValueError:
                            cat_index = 0
                        new_category = st.selectbox("Category", CATEGORIES, index=cat_index)

                        ec1, ec2 = st.columns(2)
                        with ec1:
                            new_price = st.number_input("Price", min_value=0.0, value=float(p["price"]))
                            try:
                                curr_index = ["GBP", "PLN", "EUR", "USD"].index(p["currency"])
                            except ValueError:
                                curr_index = 0
                            new_currency = st.selectbox("Currency", ["GBP", "PLN", "EUR", "USD"], index=curr_index)
                            
                            try:
                                parsed_date = datetime.datetime.strptime(p["purchase_date"], "%Y-%m-%d").date()
                            except Exception:
                                parsed_date = datetime.date.today()
                            new_purchase_date = st.date_input("Purchase Date", value=parsed_date)
                        with ec2:
                            new_capacity = st.number_input("Capacity", min_value=0.0, value=float(p.get("capacity", 10.0)))
                            try:
                                unit_index = ["ml", "g", "items"].index(p.get("unit", "ml"))
                            except ValueError:
                                unit_index = 0
                            new_unit = st.selectbox("Unit", ["ml", "g", "items"], index=unit_index)
                            new_uses = st.number_input("Total Uses", min_value=0, value=int(p.get("total_uses", 0)))

                        if st.form_submit_button("Save Changes ✓"):
                            p["brand"] = new_brand
                            p["shade"] = new_shade if new_shade else "N/A"
                            p["category"] = new_category
                            p["price"] = float(new_price)
                            p["currency"] = new_currency
                            p["purchase_date"] = str(new_purchase_date)
                            p["capacity"] = float(new_capacity)
                            p["unit"] = new_unit
                            p["total_uses"] = int(new_uses)
                            
                            save_data(st.session_state.db)
                            st.session_state[edit_mode_key] = False
                            st.success("Product updated successfully!")
                            st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

    # --- ADD PRODUCT ---
    elif st.session_state.current_page == "Add Product":
        st.markdown("### Add New Product ✨")
        
        with st.form("add_product_form"):
            brand = st.text_input("Brand")
            shade = st.text_input("Shade / Variant (Optional)")
            category = st.selectbox("Category", CATEGORIES)
            
            ac1, ac2 = st.columns(2)
            with ac1:
                price = st.number_input("Price", min_value=0.0, value=0.0)
                currency = st.selectbox("Currency", ["GBP", "PLN", "EUR", "USD"])
                purchase_date = st.date_input("Purchase Date", value=datetime.date.today())
            with ac2:
                capacity = st.number_input("Capacity / Size", min_value=0.0, value=10.0)
                unit = st.selectbox("Unit", ["ml", "g", "items"])
                initial_uses = st.number_input("Initial Uses (if already used)", min_value=0, value=0)

            in_pan = st.checkbox("Add directly to Project Pan 🌕")
            
            submitted = st.form_submit_button("Save Product 💾")
            if submitted:
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
                        "in_project_pan": in_pan
                    }
                    if "products" not in st.session_state.db:
                        st.session_state.db["products"] = []
                    st.session_state.db["products"].append(new_item)
                    save_data(st.session_state.db)
                    st.success("Product added successfully!")
                    st.session_state.current_page = "Collection"
                    st.rerun()

    # --- EMPTIES GRAVEYARD ---
    elif st.session_state.current_page == "Empties":
        st.markdown("### Empties Graveyard 🪦")
        st.markdown("<p style='color:#8c7aa9; font-size:0.9rem;'>Celebrating your successfully panned milestones.</p>", unsafe_allow_html=True)
        
        empties = st.session_state.db.get("empties", [])
        edit_empty_key = "editing_empty_id"
        
        if not empties:
            st.info("No empty products archived yet. Finish items from your collection to see them here!")
        else:
            for e in reversed(empties):
                rating_stars = "⭐" * e.get("rating", 0) if "rating" in e else "No rating"
                review_text = e.get("review", "")
                review_display = f"<p style='margin:6px 0 0 0; font-size:0.86rem; color:#5c5366; font-style:italic;'>\"{review_text}\"</p>" if review_text else ""
                
                st.markdown(f"""
                <div class="vanity-card">
                    <h4 style="margin:0 0 0.3rem 0; font-family:'Playfair Display', serif;">{e['brand']} — {e['shade']}</h4>
                    <p style="margin:0 0 0.4rem 0; color:#8c7aa9; font-size:0.85rem;">Category: {e['category']} | Finished on {e.get('finished_date', 'Unknown')}</p>
                    <p style="margin:0 0 0.3rem 0; font-size:0.88rem;"><strong>Rating:</strong> {rating_stars} ({e.get('rating', 0)}/5)</p>
                    <p style="margin:0; font-size:0.88rem;"><strong>Lifespan:</strong> {e.get('final_days_owned', 0)} days | <strong>Total Uses:</strong> {e.get('total_uses', 0)} | <strong>Final CPU:</strong> {e.get('final_cpu', 0):.2f} {e['currency']}</p>
                    {review_display}
                </div>
                """, unsafe_allow_html=True)
                
                ec1, ec2 = st.columns(2)
                with ec1:
                    if st.button("Edit Review ✏️", key=f"edit_empty_{e['id']}"):
                        st.session_state[edit_empty_key] = e["id"]
                        st.rerun()
                with ec2:
                    if st.button("Delete 🗑️", key=f"del_empty_{e['id']}"):
                        st.session_state.db["empties"] = [item for item in st.session_state.db["empties"] if item["id"] != e["id"]]
                        save_data(st.session_state.db)
                        st.success("Removed item from graveyard.")
                        st.rerun()
                        
                if st.session_state.get(edit_empty_key) == e["id"]:
                    with st.form(key=f"edit_empty_form_{e['id']}"):
                        st.markdown(f"**Edit Review for {e['brand']} - {e['shade']}**")
                        new_emp_rating = st.slider("Rating (Stars)", min_value=0, max_value=5, value=int(e.get("rating", 5)), step=1, key=f"er_{e['id']}")
                        new_emp_review = st.text_area("Review", value=e.get("review", ""), key=f"ev_{e['id']}")
                        
                        erc1, erc2 = st.columns(2)
                        with erc1:
                            if st.form_submit_button("Update Review ✓"):
                                e["rating"] = new_emp_rating
                                e["review"] = new_emp_review
                                save_data(st.session_state.db)
                                st.session_state[edit_empty_key] = None
                                st.success("Review updated successfully!")
                                st.rerun()
                        with erc2:
                            if st.form_submit_button("Cancel"):
                                st.session_state[edit_empty_key] = None
                                st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

    # --- PROJECT PAN ---
    elif st.session_state.current_page == "Project Pan":
        st.markdown("### Project Pan (Gamified) 🌕")
        
        current_xp = st.session_state.db.get("stats", {}).get("xp", 0)
        current_level_title, next_level_xp = get_pan_level(current_xp)
        
        st.markdown(f"""
        <div class="vanity-card" style="background-color: #f7f3fd; text-align: center;">
            <h4 style="margin:0; font-family:'Playfair Display', serif; color:#4a3468;">Rank: {current_level_title}</h4>
            <p style="margin:5px 0 0 0; font-size: 0.9rem; color:#8c7aa9;">Total XP: <b>{current_xp} XP</b></p>
        </div>
        """, unsafe_allow_html=True)

        products = [p for p in st.session_state.db.get("products", []) if p.get("in_project_pan", False)]
        pan_finishing_key = "pan_finishing_id"

        if not products:
            st.info("No active items in Project Pan. Add items from your collection to start earning XP!")
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
                with m1:
                    st.markdown(f'<div class="metric-box"><div class="metric-value">{days}</div><div class="metric-label">Days Owned</div></div>', unsafe_allow_html=True)
                with m2:
                    st.markdown(f'<div class="metric-box"><div class="metric-value">{total_uses}</div><div class="metric-label">Uses</div></div>', unsafe_allow_html=True)
                with m3:
                    st.markdown(f'<div class="metric-box"><div class="metric-value">{cpu:.2f} {p["currency"]}</div><div class="metric-label">Cost / Use</div></div>', unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                daily_uses_input = st.number_input("Estimated daily applications:", min_value=0.5, max_value=10.0, value=1.0, step=0.5, key=f"d_uses_{p['id']}")
                
                if p.get("capacity", 0) > 0:
                    d_needed, target_date, total_apps_needed = estimate_pan_completion(p["category"], p["capacity"], p["unit"], daily_uses_input)
                    if d_needed and total_apps_needed > 0:
                        formatted_date = target_date.strftime("%B %Y")
                        progress_ratio = min(float(total_uses) / total_apps_needed, 1.0)
                        
                        st.markdown(f"""
                        <div style="background-color: #f2ebfc; border-radius: 6px; padding: 0.8rem; margin-top: 10px; font-size: 0.88rem; color: #4a3468;">
                            🔮 <strong>Timeline Forecast:</strong> Approx. <b>{d_needed} days</b> ({formatted_date}) to finish at {daily_uses_input} uses/day.
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown(f"<p style='font-size:0.8rem; color:#6b5b7a; margin-bottom:4px;'><b>Visual Tracking Progress:</b> {total_uses} / ~{int(total_apps_needed)} estimated uses ({int(progress_ratio * 100)}%)</p>", unsafe_allow_html=True)
                        st.progress(progress_ratio)

                st.markdown("<br>", unsafe_allow_html=True)
                col_add, col_btn = st.columns([2, 1])
                with col_add:
                    add_uses = st.number_input("Log Uses:", min_value=1, max_value=10, value=1, key=f"uses_{p['id']}")
                with col_btn:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Log (+XP)", key=f"btn_{p['id']}"):
                        p["total_uses"] = p.get("total_uses", 0) + add_uses
                        st.session_state.db["stats"]["xp"] = st.session_state.db["stats"].get("xp", 0) + (add_uses * 5)
                        save_data(st.session_state.db)
                        st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)
                pc1, pc2 = st.columns(2)
                with pc1:
                    if st.button("Finish Item 🎉", key=f"pan_fin_btn_{p['id']}"):
                        st.session_state[pan_finishing_key] = p["id"]
                        st.rerun()
                with pc2:
                    if st.button("Delete Item 🗑️", key=f"pan_del_btn_{p['id']}"):
                        st.session_state.db["products"] = [item for item in st.session_state.db["products"] if item["id"] != p["id"]]
                        save_data(st.session_state.db)
                        st.success("Product deleted.")
                        st.rerun()

                # Finishing Modal inside Project Pan view
                if st.session_state.get(pan_finishing_key) == p["id"]:
                    st.markdown(f"""
                    <div style="background-color: #f4ecfb; border: 1px solid #d4c2ec; border-radius: 6px; padding: 1.2rem; margin-top: 10px; margin-bottom: 10px;">
                        <h4 style="margin:0 0 0.3rem 0; font-family:'Playfair Display', serif; color:#4a3468;">🌟 Review & Grade Finished Product</h4>
                        <p style="margin:0; font-size:0.9rem; color:#5c5366;">How was your experience with <b>{p['brand']} - {p['shade']}</b>?</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.form(key=f"pan_review_form_{p['id']}"):
                        finish_rating = st.slider("Rating (Stars)", min_value=0, max_value=5, value=5, step=1, key=f"pan_slider_{p['id']}")
                        finish_review = st.text_area("Write a short review or thoughts:", key=f"pan_rev_text_{p['id']}")
                        
                        prc1, prc2 = st.columns(2)
                        with prc1:
                            submit_review = st.form_submit_button("Complete & Archive 🪦")
                        with prc2:
                            cancel_review = st.form_submit_button("Cancel")
                            
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
                            
                            if "empties" not in st.session_state.db:
                                st.session_state.db["empties"] = []
                            st.session_state.db["empties"].append(empty_item)
                            
                            st.session_state.db["stats"]["xp"] = st.session_state.db["stats"].get("xp", 0) + 50
                            st.session_state.db["products"] = [item for item in st.session_state.db["products"] if item["id"] != p["id"]]
                            st.session_state[pan_finishing_key] = None
                            save_data(st.session_state.db)
                            
                            if is_lip and st.session_state.db["stats"]["finished_lip_products"] % 5 == 0:
                                st.session_state["show_lip_reward_banner"] = True
                            st.rerun()
                            
                        if cancel_review:
                            st.session_state[pan_finishing_key] = None
                            st.rerun()

    # --- WISHLIST ---
    elif st.session_state.current_page == "Wishlist":
        st.markdown("### Wishlist ✨")
        
        with st.form("add_wishlist_form"):
            w_brand = st.text_input("Brand")
            w_product = st.text_input("Product Name / Shade")
            w_price = st.number_input("Price", min_value=0.0, value=0.0)
            w_currency = st.selectbox("Currency", ["GBP", "PLN", "EUR", "USD"], key="w_curr")
            
            if st.form_submit_button("Add to Wishlist ➕"):
                if w_brand and w_product:
                    if "wishlist" not in st.session_state.db:
                        st.session_state.db["wishlist"] = []
                    st.session_state.db["wishlist"].append({
                        "id": str(random.randint(100000, 999999)),
                        "brand": w_brand,
                        "product": w_product,
                        "price": float(w_price),
                        "currency": w_currency
                    })
                    save_data(st.session_state.db)
                    st.success("Added to wishlist!")
                    st.rerun()
                else:
                    st.error("Please fill in the brand and product name.")

        st.markdown("<br>", unsafe_allow_html=True)
        wishlist_items = st.session_state.db.get("wishlist", [])
        
        if not wishlist_items:
            st.info("Your wishlist is empty.")
        else:
            for w in wishlist_items:
                st.markdown(f"""
                <div class="vanity-card">
                    <h4 style="margin:0 0 0.2rem 0; font-family:'Playfair Display', serif;">{w['brand']} — {w['product']}</h4>
                    <p style="margin:0; font-size:0.9rem; color:#8c7aa9;">Price: {w['price']:.2f} {w['currency']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                wc1, wc2 = st.columns(2)
                with wc1:
                    if st.button("Move to Collection 🎉", key=f"move_w_{w['id']}"):
                        new_item = {
                            "id": str(random.randint(100000, 999999)),
                            "brand": w["brand"],
                            "shade": w["product"],
                            "category": "lipstick",
                            "price": w["price"],
                            "currency": w["currency"],
                            "purchase_date": str(datetime.date.today()),
                            "capacity": 10.0,
                            "unit": "ml",
                            "total_uses": 0,
                            "in_project_pan": False
                        }
                        st.session_state.db["products"].append(new_item)
                        st.session_state.db["wishlist"] = [item for item in st.session_state.db["wishlist"] if item["id"] != w["id"]]
                        save_data(st.session_state.db)
                        st.success("Moved to collection!")
                        st.rerun()
                with wc2:
                    if st.button("Delete 🗑️", key=f"del_w_{w['id']}"):
                        st.session_state.db["wishlist"] = [item for item in st.session_state.db["wishlist"] if item["id"] != w["id"]]
                        save_data(st.session_state.db)
                        st.rerun()

    # --- NO-BUY RULES & REWARDS ---
    # --- NO-BUY RULES & REWARDS ---
    elif st.session_state.current_page == "No-Buy Rules":
        st.markdown("### No-Buy & Rewards 🌸")
        
        if st.session_state.get("show_lip_reward_banner", False):
            st.markdown("""
            <div style="background-color: #fce8f3; border: 1px solid #f7c5e2; border-radius: 6px; padding: 1.2rem; margin-bottom: 1rem; text-align: center;">
                <h4 style="margin:0 0 0.3rem 0; font-family:'Playfair Display', serif; color: #8a3b6b;">🎉 Reward Unlocked! 🎉</h4>
                <p style="margin:0; font-size:0.95rem; color: #6b3b52;">You've finished 5 lip products! Treat yourself to a guilt-free luxury coffee or small beauty treat!</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Claim & Dismiss Reward"):
                st.session_state["show_lip_reward_banner"] = False
                st.rerun()

        stats = st.session_state.db.get("stats", {})
        start_date_str = stats.get("no_buy_start_date", str(datetime.date.today()))
        try:
            current_start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except Exception:
            current_start_date = datetime.date.today()

        # Allow user to choose/update the date interactively
        st.markdown("<p style='font-size:0.9rem; color:#5c5366;'>Select your no-buy start date below:</p>", unsafe_allow_html=True)
        selected_start_date = st.date_input("No-Buy Start Date", value=current_start_date, key="no_buy_date_picker")

        if str(selected_start_date) != start_date_str:
            st.session_state.db["stats"]["no_buy_start_date"] = str(selected_start_date)
            save_data(st.session_state.db)
            st.rerun()

        no_buy_days = max((datetime.date.today() - selected_start_date).days, 0)
        finished_lips = stats.get("finished_lip_products", 0)

        st.markdown(f"""
        <div class="vanity-card" style="text-align: center;">
            <h4 style="margin:0; font-family:'Playfair Display', serif; color:#4a3468;">No-Buy Track Record</h4>
            <p style="font-size: 2rem; font-family:'Playfair Display', serif; color: #6b4c8c; margin: 10px 0 5px 0;">{no_buy_days} Days</p>
            <p style="margin:0; font-size: 0.85rem; color:#8c7aa9;">Started on {selected_start_date.strftime('%B %d, %Y')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="vanity-card" style="text-align: center;">
            <h4 style="margin:0; font-family:'Playfair Display', serif; color:#4a3468;">Lip Product Milestone</h4>
            <p style="font-size: 2rem; font-family:'Playfair Display', serif; color: #6b4c8c; margin: 10px 0 5px 0;">{finished_lips} / 5</p>
            <p style="margin:0; font-size: 0.85rem; color:#8c7aa9;">Finished lip items toward your next reward voucher.</p>
        </div>
        """, unsafe_allow_html=True)
            if st.button("Claim & Dismiss Reward"):
                st.session_state["show_lip_reward_banner"] = False
                st.rerun()

        stats = st.session_state.db.get("stats", {})
        start_date_str = stats.get("no_buy_start_date", str(datetime.date.today()))
        try:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except Exception:
            start_date = datetime.date.today()
            
        no_buy_days = max((datetime.date.today() - start_date).days, 0)
        finished_lips = stats.get("finished_lip_products", 0)

        st.markdown(f"""
        <div class="vanity-card" style="text-align: center;">
            <h4 style="margin:0; font-family:'Playfair Display', serif; color:#4a3468;">No-Buy Track Record</h4>
            <p style="font-size: 2rem; font-family:'Playfair Display', serif; color: #6b4c8c; margin: 10px 0 5px 0;">{no_buy_days} Days</p>
            <p style="margin:0; font-size: 0.85rem; color:#8c7aa9;">Started on {start_date.strftime('%B %d, %Y')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="vanity-card" style="text-align: center;">
            <h4 style="margin:0; font-family:'Playfair Display', serif; color:#4a3468;">Lip Product Milestone</h4>
            <p style="font-size: 2rem; font-family:'Playfair Display', serif; color: #6b4c8c; margin: 10px 0 5px 0;">{finished_lips} / 5</p>
            <p style="margin:0; font-size: 0.85rem; color:#8c7aa9;">Finished lip items toward your next reward voucher.</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Reset No-Buy Tracker Date"):
            st.session_state.db["stats"]["no_buy_start_date"] = str(datetime.date.today())
            save_data(st.session_state.db)
            st.success("No-buy start date reset to today!")
            st.rerun()

    # --- ANALYTICS ---
    elif st.session_state.current_page == "Analytics":
        st.markdown("### Beauty Stats 🐈‍⬛")
        
        products = st.session_state.db.get("products", [])
        empties = st.session_state.db.get("empties", [])
        total_items = len(products)
        total_spent = sum([p.get("price", 0) for p in products])
        total_empties = len(empties)

        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.markdown(f'<div class="metric-box"><div class="metric-value">{total_items}</div><div class="metric-label">Active Items</div></div>', unsafe_allow_html=True)
        with col_a2:
            st.markdown(f'<div class="metric-box"><div class="metric-value">{total_empties}</div><div class="metric-label">Empties Panned</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="vanity-card" style="text-align: center;">
            <h4 style="margin:0; font-family:'Playfair Display', serif; color:#4a3468;">Active Collection Value</h4>
            <p style="font-size: 1.8rem; font-family:'Playfair Display', serif; color: #6b4c8c; margin: 8px 0 0 0;">{total_spent:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
