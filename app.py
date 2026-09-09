import datetime
import random
import pandas as pd
import plotly.express as px
from st_supabase_connection import SupabaseConnection
import streamlit as st

# ---------------------------------------------------------
# Page Configuration & Custom CSS for Better Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Vanity Sanctuary",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Global CSS for uniform buttons and styling
st.markdown("""
<style>
/* Uniform Buttons */
button {
    border-radius: 10px !important;
    border: 1px solid #d4c4ec !important;
    background-color: #ffffff !important;
    color: #4a3468 !important;
    font-weight: 500 !important;
    box-shadow: 0 2px 6px rgba(90, 70, 120, 0.04) !important;
    padding: 0.5rem 1rem;
    margin: 0.2rem;
}
button:hover {
    border-color: #bfa8e4 !important;
    background-color: #f8f5fc !important;
}

/* App background & font */
.stApp {
    background-color: #d8cde9 !important;
    color: #382a4b;
    font-family: 'Lora', serif;
}

/* Container max width */
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
    border-radius: 12px;
    padding: 1.8rem 1rem 1.4rem 1rem;
    text-align: center;
    margin-bottom: 20px;
    border: 1px solid #e2d7f3;
    box-shadow: 0 4px 15px rgba(90, 70, 120, 0.06);
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
    color: #9d8ab8;
    font-size: 1.05rem;
    font-family: 'Playfair Display', serif;
    font-style: italic;
    margin-top: 0.3rem;
    margin-bottom: 0;
    font-weight: 400;
}

/* Card Style */
.vanity-card {
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e3d9f2;
    padding: 1.25rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 12px rgba(90, 70, 120, 0.05);
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Connect to Supabase
# ---------------------------------------------------------
conn = st.connection("supabase", type=SupabaseConnection)

# Data loading function
def load_cloud_data():
    try:
        products_res = conn.table("products").select("*").execute()
        wishlist_res = conn.table("wishlist").select("*").execute()
        empties_res = conn.table("empties").select("*").execute()
        stats_res = conn.table("stats").select("*").execute()

        products = products_res.data if products_res and hasattr(products_res, 'data') else []
        wishlist = wishlist_res.data if wishlist_res and hasattr(wishlist_res, 'data') else []
        empties = empties_res.data if empties_res and hasattr(empties_res, 'data') else []

        stats_data = stats_res.data[0] if stats_res and hasattr(stats_res, 'data') and stats_res.data else {}
        stats = {
            "id": stats_data.get("id", 1),
            "finished_lip_products": stats_data.get("finished_lip_products", 0),
            "no_buy_start_date": stats_data.get("no_buy_start_date", str(datetime.date.today())),
            "xp": stats_data.get("xp", 0),
            "rewards_redeemed": stats_data.get("rewards_redeemed", 0),
            "active_challenge": stats_data.get("active_challenge", None),
        }
        return {"products": products, "wishlist": wishlist, "empties": empties, "stats": stats}
    except Exception:
        return {
            "products": [], "wishlist": [], "empties": [],
            "stats": {"id": 1, "finished_lip_products": 0, "no_buy_start_date": str(datetime.date.today()), "xp": 0, "rewards_redeemed": 0, "active_challenge": None}
        }

st.session_state.db = load_cloud_data()
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# ---------------------------------------------------------
# Header
# ---------------------------------------------------------
st.markdown(
    """
<div class="sanctuary-header">
    <h1>Vanity Sanctuary</h1>
    <p>Minimalist inventory & project pan</p>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Routing and Main Menu
# ---------------------------------------------------------
if st.session_state.current_page == "Home":
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Your Collection"):
            st.session_state.current_page = "Collection"
            st.rerun()
    with col2:
        if st.button("Project Pan"):
            st.session_state.current_page = "Project Pan"
            st.rerun()

    col3, col4 = st.columns(2)
    with col3:
        if st.button("Wishlist"):
            st.session_state.current_page = "Wishlist"
            st.rerun()
    with col4:
        if st.button("Roulette Challenge"):
            st.session_state.current_page = "Roulette Challenge"
            st.rerun()

    col5, col6 = st.columns(2)
    with col5:
        if st.button("Reward Shop"):
            st.session_state.current_page = "Reward Shop"
            st.rerun()
    with col6:
        if st.button("Statistics & Analytics"):
            st.session_state.current_page = "Analytics"
            st.rerun()

else:
    if st.button("Back to Home"):
        st.session_state.current_page = "Home"
        st.rerun()

    # --- Individual pages ---
    if st.session_state.current_page == "Collection":
        show_collection()
    elif st.session_state.current_page == "Project Pan":
        show_project_pan()
    elif st.session_state.current_page == "Roulette Challenge":
        show_roulette()
    elif st.session_state.current_page == "Analytics":
        show_analytics()
    elif st.session_state.current_page == "Wishlist":
        show_wishlist()

# ---------------------------------------------------------
# Define page functions
# ---------------------------------------------------------
def show_collection():
    st.markdown("### Your Full Collection")
    products = st.session_state.db.get("products", [])
    if not products:
        st.info("Your collection is currently empty.")
        return
    for p in reversed(products):
        st.markdown(render_product_card(p), unsafe_allow_html=True)
        toggle = st.checkbox(
            "🌕 Include in Project Pan",
            value=p.get("in_project_pan", False),
            key=f"pan_{p['id']}"
        )
        if toggle != p.get("in_project_pan", False):
            conn.table("products").update({"in_project_pan": toggle}).eq("id", p['id']).execute()
            st.session_state.db = load_cloud_data()
            st.rerun()

def render_product_card(product):
    return f"""
<div class="vanity-card">
    <h4 style="margin:0 0 0.4rem 0; font-family:'Playfair Display', serif;">{product.get('brand', '')} — <span style="font-weight:400;">{product.get('shade', '')}</span></h4>
    <p style="margin:0 0 0.6rem 0; color:#8c7aa9; font-size:0.88rem;">Category: {product.get('category', '')}</p>
    <p style="margin:0; font-size:0.9rem;"><strong>Price:</strong> {product.get('price', 0):.2f} {product.get('currency', 'GBP')} | <strong>Logged Uses:</strong> {product.get('total_uses', 0)}</p>
</div>
"""

def show_project_pan():
    st.markdown(f"### { 'Usage Logging' }")
    products = st.session_state.db.get("products", [])
    pan_products = [p for p in products if p.get("in_project_pan", False)]
    if not pan_products:
        st.info("No products selected for Project Pan yet. Go to 'Your Collection' and check 'Include in Project Pan' on the items you want to focus on! 🌕")
        return
    for p in pan_products:
        prod_id = p.get("id")
        brand = p.get("brand", "Unknown")
        shade = p.get("shade", "")
        total_uses = p.get("total_uses", 0)
        daily_avg = float(p.get("daily_uses_avg", 1.0) or 1.0)
        remaining_uses_est = max(100 - total_uses, 1)
        est_date = datetime.date.today() + datetime.timedelta(days=int(remaining_uses_est / daily_avg))
        days_left = (est_date - datetime.date.today()).days

        st.markdown(
            f"""
<div class="vanity-card">
    <h4 style="margin:0 0 0.4rem 0; font-family:'Playfair Display', serif;">{brand} — {shade}</h4>
    <p style="margin:0;">Total logged uses: <b>{total_uses}</b></p>
    <p style="margin:0;">Estimated Pan Date: <b>{est_date.strftime('%B %d, %Y')}</b> ({days_left} days left)</p>
</div>
""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        if col1.button(f"+1 Use ✨", key=f"add_1_{prod_id}"):
            conn.table("products").update({"total_uses": total_uses + 1}).eq("id", prod_id).execute()
            st.session_state.db = load_cloud_data()
            st.rerun()
        if col2.button(f"+5 Uses 🚀", key=f"add_5_{prod_id}"):
            conn.table("products").update({"total_uses": total_uses + 5}).eq("id", prod_id).execute()
            st.session_state.db = load_cloud_data()
            st.rerun()

        new_daily_avg = st.slider(
            f"Daily usage rate for {brand}",
            min_value=0.1,
            max_value=5.0,
            value=daily_avg,
            step=0.1,
            key=f"slider_{prod_id}"
        )
        if new_daily_avg != daily_avg:
            conn.table("products").update({"daily_uses_avg": new_daily_avg}).eq("id", prod_id).execute()

def show_roulette():
    st.markdown("### 🎲 Beauty Roulette Challenge")
    products = st.session_state.db.get("products", [])
    if not products:
        st.warning("Your product set is empty. Add some products!")
        return

    col_single, col_full = st.columns(2)

    with col_single:
        if st.button("🎲 Single Product"):
            st.session_state.roulette_single = random.choice(products)
            st.session_state.roulette_mode = "single"

    with col_full:
        if st.button("👑 Full Face Routine"):
            categories = set(p.get("category", "Uncategorized") for p in products)
            routine = []
            for cat in categories:
                cat_prods = [p for p in products if p.get("category") == cat]
                routine.append(random.choice(cat_prods))
            st.session_state.roulette_full = routine
            st.session_state.roulette_mode = "full"

    if st.session_state.get("roulette_mode") == "single":
        item = st.session_state.roulette_single
        st.success("🎉 You drew a product for today's look!")
        st.markdown(render_product_card(item), unsafe_allow_html=True)

    elif st.session_state.get("roulette_mode") == "full":
        st.success("👑 Full Routine Selected!")
        for item in st.session_state.roulette_full:
            st.markdown(render_product_card(item), unsafe_allow_html=True)

def show_analytics():
    st.markdown("### 🐈‍⬛ Beauty Stats & Analytics")
    products = st.session_state.db.get("products", [])
    empties = st.session_state.db.get("empties", [])
    stats = st.session_state.db.get("stats", {})

    total_value = sum(float(p.get("price", 0) or 0) for p in products)
    total_uses = sum(int(p.get("total_uses", 0) or 0) for p in products)

    # Days in No-Buy streak
    start_date_str = stats.get("no_buy_start_date", str(datetime.date.today()))
    try:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        no_buy_days = (datetime.date.today() - start_date).days
    except:
        no_buy_days = 0

    st.markdown(
        f"""
<div class="vanity-card" style="text-align:center;">
    <h2 style="margin:0; color:#4a3468; font-size:2.4rem;">{no_buy_days} Days</h2>
    <p style="margin:0; color:#8c7aa9;">Low-Buy / No-Buy Streak 🌿</p>
</div>
""", unsafe_allow_html=True)

    # Show collection value and usage
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
<div class="vanity-card">
    <p style="margin:0; font-size:0.85rem; color:#8c7aa9;">Collection Value</p>
    <h3 style="margin:0.2rem 0; color:#3a3342;">{total_value:.2f} GBP</h3>
</div>
""", unsafe_allow_html=True)
    with col2:
        st.markdown(
            f"""
<div class="vanity-card">
    <p style="margin:0; font-size:0.85rem; color:#8c7aa9;">Total Uses</p>
    <h3 style="margin:0.2rem 0; color:#3a3342;">{total_uses} x</h3>
</div>
""", unsafe_allow_html=True)

    # Empties
    st.markdown("#### 🗑️ Empties")
    if not empties:
        st.info("No empties recorded.")
    else:
        for e in empties:
            st.markdown(
                f"""
<div class="vanity-card">
    <h4 style="margin:0;">🎉 {e.get('brand')} — {e.get('shade')}</h4>
    <p style="margin:4px 0 0 0; color:#8c7aa9; font-size:0.85rem;">Emptied!</p>
</div>
""", unsafe_allow_html=True)

def show_wishlist():
    st.markdown("### Wishlist ✨")
    with st.form("add_wishlist_form"):
        brand_input = st.text_input("Brand")
        item_input = st.text_input("Item / Shade")
        price_input = st.number_input("Estimated Price", min_value=0.0, value=0.0)
        notes_input = st.text_area("Why do you want this?")
        if st.form_submit_button("Add to Wishlist"):
            new_item = {
                "brand": brand_input,
                "item": item_input,
                "price": float(price_input),
                "currency": "GBP",
                "notes": f"{notes_input} (Added: {datetime.date.today()})"
            }
            conn.table("wishlist").insert(new_item).execute()
            st.session_state.db = load_cloud_data()
            st.rerun()

    wishlist_items = st.session_state.db.get("wishlist", [])
    if not wishlist_items:
        st.info("Your wishlist is empty.")
    else:
        for w in wishlist_items:
            st.markdown(
                f"""
<div class="vanity-card">
    <h4 style="margin:0;">{w.get('brand', '')} — {w.get('item', '')}</h4>
    <p style="margin:6px 0; color:#6b5b7a; font-size:0.88rem;">{w.get('notes', '')}</p>
    <span style="background:#e8dff5; color:#4a3468; padding:3px 8px; border-radius:6px; font-size:0.78rem; font-weight:500;">⏳ 14-Day Cooling Off Active</span>
</div>
""", unsafe_allow_html=True)

# --- END of code ---
