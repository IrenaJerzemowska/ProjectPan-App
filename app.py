import datetime
import html
import random

import pandas as pd
import plotly.express as px
import streamlit as st
from st_supabase_connection import SupabaseConnection

# ---------------------------------------------------------
# Page Configuration & Custom CSS for Better Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Vanity Sanctuary",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
/* 1. iOS Touch Optimization & General Button Styling */
button, div[data-baseweb="select"] {
    touch-action: manipulation !important;
    -webkit-tap-highlight-color: transparent !important;
    user-select: none !important;
    -webkit-user-select: none !important;
}

button {
    border-radius: 16px !important;
    border: 1px solid #d4c4ec !important;
    background: linear-gradient(135deg, #ffffff 0%, #f7f1fc 100%) !important;
    color: #3a3342 !important;
    font-weight: 600 !important;
    font-size: 1rem !important; /* Slightly reduced font size so long text fits on 1 line */
    letter-spacing: 0.2px;
    box-shadow: 0 4px 14px rgba(90, 70, 120, 0.10) !important;
    
    /* UNIFIED BUTTON SIZING FIXES */
    width: 100% !important;
    height: 52px !important;      /* Forces all buttons to the exact same vertical height */
    min-height: 52px !important;  /* iOS touch standard */
    padding: 0 0.5rem !important; /* Standardizes inner spacing */
    
    display: flex !important;
    align-items: center;
    justify-content: center;
    text-align: center;
    line-height: 1.2;
    white-space: nowrap !important; /* Prevents text wrap from pushing height out of alignment */
    overflow: hidden;
    text-overflow: ellipsis;
}

button:hover {
    transform: translateY(-2px);
    border-color: #bfa8e4 !important;
    box-shadow: 0 8px 20px rgba(90, 70, 120, 0.18) !important;
    background: linear-gradient(135deg, #f8f5fc 0%, #efe4fb 100%) !important;
}

button:active {
    transform: translateY(0px);
}

/* 2. Global Theme & Mobile Responsiveness */
.stApp {
    background-color: #d8cde9 !important;
    color: #382a4b;
    font-family: 'Lora', serif;
}

.block-container {
    max-width: 480px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 2.5rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}

/* 3. Header & Cards UI Polish */
.sanctuary-header {
    background: #ffffff;
    border-radius: 16px;
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

.home-menu {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e2d7f3;
    padding: 1.2rem 0.9rem 0.6rem 0.9rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 15px rgba(90, 70, 120, 0.06);
}

.home-menu-label {
    text-align: center;
    color: #9d8ab8;
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 0.95rem;
    margin-bottom: 0.7rem;
}

.vanity-card {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #e3d9f2;
    padding: 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(90, 70, 120, 0.05);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.vanity-card:hover {
    box-shadow: 0 6px 16px rgba(90, 70, 120, 0.1);
}

/* Visual Progress Bar */
.progress-bg {
    width: 100%;
    height: 8px;
    background-color: #f1f0f7;
    border-radius: 999px;
    overflow: hidden;
    margin: 0.6rem 0;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #bfa8e4, #7c5295);
    border-radius: 999px;
    transition: width 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Connect to Supabase
# ---------------------------------------------------------
conn = st.connection("supabase", type=SupabaseConnection)

DEFAULT_STATS = {
    "id": 1,
    "finished_lip_products": 0,
    "no_buy_start_date": str(datetime.date.today()),
    "xp": 0,
    "rewards_redeemed": 0,
    "active_challenge": None,
}


def load_cloud_data():
    """Load all app data from Supabase. Falls back to safe empty defaults on error."""
    try:
        products_res = conn.table("products").select("*").execute()
        wishlist_res = conn.table("wishlist").select("*").execute()
        empties_res = conn.table("empties").select("*").execute()
        stats_res = conn.table("stats").select("*").execute()

        products = products_res.data if products_res and hasattr(products_res, "data") else []
        wishlist = wishlist_res.data if wishlist_res and hasattr(wishlist_res, "data") else []
        empties = empties_res.data if empties_res and hasattr(empties_res, "data") else []

        stats_data = stats_res.data[0] if stats_res and hasattr(stats_res, "data") and stats_res.data else {}
        stats = {**DEFAULT_STATS, **{k: v for k, v in stats_data.items() if v is not None}}

        return {"products": products, "wishlist": wishlist, "empties": empties, "stats": stats}
    except Exception as e:
        st.session_state["_last_load_error"] = str(e)
        return {"products": [], "wishlist": [], "empties": [], "stats": DEFAULT_STATS.copy()}


def update_row(table, row_id, values, id_field="id"):
    """Update a single row by id. Returns True on success, shows an error and returns False on failure."""
    try:
        conn.table(table).update(values).eq(id_field, row_id).execute()
        return True
    except Exception as e:
        st.error(f"Couldn't save that change ({e}). Please try again.")
        return False


def insert_row(table, values):
    """Insert a row. Returns True on success, shows an error and returns False on failure."""
    try:
        conn.table(table).insert(values).execute()
        return True
    except Exception as e:
        st.error(f"Couldn't save that change ({e}). Please try again.")
        return False


FINISH_XP_REWARD = 50
LIP_CATEGORY_KEYWORDS = ("lip",)

PRODUCT_CATEGORIES = [
    "Lip Balm",
    "Lip Gloss",
    "Lipstick",
    "Lip Liner",
    "Eyeshadow Palette",
    "Mascara",
    "Eyeliner",
    "Foundation",
    "Concealer",
    "Blush",
    "Highlighter",
    "Bronzer",
    "Brow Product",
    "Setting Powder/Spray",
    "Skincare",
    "Fragrance",
    "Other",
]


def esc(value):
    """HTML-escape any user-entered text before it goes into unsafe_allow_html markup."""
    return html.escape(str(value)) if value is not None else ""


def normalize_str(s):
    """Helper to clean and normalize strings for duplicate detection."""
    return " ".join(str(s).strip().lower().split()) if s else ""


def is_duplicate_product(products, brand, shade, current_id=None):
    """Robust Duplicate Checker Logic: Case-insensitive and whitespace trimmed."""
    norm_brand = normalize_str(brand)
    norm_shade = normalize_str(shade)

    for p in products:
        if current_id and p.get("id") == current_id:
            continue
        p_brand = normalize_str(p.get("brand"))
        p_shade = normalize_str(p.get("shade"))

        if p_brand == norm_brand and p_shade == norm_shade:
            return True
    return False


def calculate_estimated_pan_date(total_uses, total_estimated_uses=100, daily_uses_avg=1.0, created_at=None):
    """
    Estimates usage completion based on either:
    1. Velocity over time (since created_at)
    2. Estimated daily usage rate (daily_uses_avg)
    """
    total_uses = max(0, int(total_uses or 0))
    total_estimated_uses = max(1, int(total_estimated_uses or 100))

    if total_uses >= total_estimated_uses:
        return {"days_left": 0, "est_date_str": "Finished!", "progress_pct": 100}

    remaining_uses = total_estimated_uses - total_uses
    progress_pct = min(100, int((total_uses / total_estimated_uses) * 100))

    # Calculate rate per day dynamically if creation date is present
    rate_per_day = float(daily_uses_avg or 1.0)
    if created_at:
        try:
            start_date = datetime.datetime.strptime(str(created_at)[:10], "%Y-%m-%d").date()
            days_active = max(1, (datetime.date.today() - start_date).days)
            historical_rate = total_uses / days_active
            if historical_rate > 0:
                rate_per_day = historical_rate
        except (ValueError, TypeError):
            pass

    days_left = max(1, int(remaining_uses / rate_per_day))
    est_date = datetime.date.today() + datetime.timedelta(days=days_left)

    return {
        "days_left": days_left,
        "est_date_str": est_date.strftime('%B %d, %Y'),
        "progress_pct": progress_pct
    }


# ---------------------------------------------------------
# Page functions
# ---------------------------------------------------------
def render_product_card(product):
    price = product.get("price") or 0
    try:
        price = float(price)
    except (TypeError, ValueError):
        price = 0.0
    return f"""
<div class="vanity-card">
    <h4 style="margin:0 0 0.4rem 0; font-family:'Playfair Display', serif;">{esc(product.get('brand', ''))} — <span style="font-weight:400;">{esc(product.get('shade', ''))}</span></h4>
    <p style="margin:0 0 0.6rem 0; color:#8c7aa9; font-size:0.88rem;">Category: {esc(product.get('category', ''))}</p>
    <p style="margin:0; font-size:0.9rem;"><strong>Price:</strong> {price:.2f} {esc(product.get('currency', 'GBP'))} | <strong>Logged Uses:</strong> {esc(product.get('total_uses', 0))}</p>
</div>
"""


def show_collection():
    st.markdown("### 🧪 Your Full Collection")

    with st.expander("➕ Add a New Product"):
        with st.form("add_product_form", clear_on_submit=True):
            brand_input = st.text_input("Brand")
            shade_input = st.text_input("Shade / Product Name")
            category_input = st.selectbox("Category", PRODUCT_CATEGORIES)
            col_p, col_c = st.columns(2)
            with col_p:
                price_input = st.number_input("Price", min_value=0.0, value=0.0, step=0.5)
            with col_c:
                currency_input = st.selectbox("Currency", ["GBP", "USD", "EUR"])
            in_pan_input = st.checkbox("🕯️ Add straight to Project Pan")

            if st.form_submit_button("🧪 Add to Collection"):
                existing_products = st.session_state.db.get("products", [])
                
                if not brand_input.strip():
                    st.warning("Please enter at least a brand name.")
                elif is_duplicate_product(existing_products, brand_input, shade_input):
                    st.error(f"⚠️ '{brand_input.strip()} - {shade_input.strip()}' already exists in your collection!")
                else:
                    new_product = {
                        "brand": brand_input.strip(),
                        "shade": shade_input.strip(),
                        "category": category_input,
                        "price": float(price_input),
                        "currency": currency_input,
                        "total_uses": 0,
                        "daily_uses_avg": 1.0,
                        "in_project_pan": in_pan_input,
                        "finished": False,
                    }
                    if insert_row("products", new_product):
                        st.session_state.db = load_cloud_data()
                        st.success(f"Added {brand_input} to your collection! 🔮")
                        st.rerun()

    products = st.session_state.db.get("products", [])
    if not products:
        st.info("Your collection is currently empty.")
        return

    for p in reversed(products):
        st.markdown(render_product_card(p), unsafe_allow_html=True)
        if p.get("finished", False):
            st.caption("🕯️ Finished — used up completely")
            continue

        toggle = st.checkbox(
            "🕯️ Include in Project Pan",
            value=p.get("in_project_pan", False),
            key=f"pan_{p['id']}",
        )
        if toggle != p.get("in_project_pan", False):
            if update_row("products", p["id"], {"in_project_pan": toggle}):
                st.session_state.db = load_cloud_data()
                st.rerun()

        confirm_key = f"confirm_delete_{p['id']}"
        if st.session_state.get(confirm_key):
            st.warning(f"Delete {p.get('brand', '')} — {p.get('shade', '')}? This can't be undone.")
            col_yes, col_no = st.columns(2)
            if col_yes.button("Yes, delete it", key=f"yes_delete_{p['id']}"):
                try:
                    conn.table("products").delete().eq("id", p["id"]).execute()
                    st.session_state.db = load_cloud_data()
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
                except Exception as e:
                    st.error(f"Couldn't delete that item ({e}).")
            if col_no.button("Cancel", key=f"no_delete_{p['id']}"):
                st.session_state.pop(confirm_key, None)
                st.rerun()
        else:
            if st.button("🗑️ Delete", key=f"delete_{p['id']}"):
                st.session_state[confirm_key] = True
                st.rerun()


PAN_MOTIVATORS = [
    "🕯️ A candle burns brightest right before it's spent — use what you have.",
    "🔮 The stars favor those who finish what they started.",
    "🌙 Small nightly rituals become a finished potion in time.",
    "🧙‍♀️ Your vanity is a spellbook — read every page before writing a new one.",
    "🪄 Real magic isn't buying more, it's using what you've already conjured.",
    "🕸️ Let nothing gather dust in your sanctuary.",
    "✨ Every swipe brings you closer to the bottom of the jar.",
    "🦇 Finish the potion before brewing the next.",
]


def daily_motivator():
    """A witchy nudge that stays the same all day, then rotates tomorrow."""
    seed = str(datetime.date.today())
    return random.Random(seed).choice(PAN_MOTIVATORS)


def mark_product_finished(product):
    """Mark a product finished, log it as an empty, and award XP."""
    prod_id = product.get("id")
    stats = st.session_state.db.get("stats", {})
    current_xp = int(stats.get("xp", 0) or 0)
    category = (product.get("category") or "").lower()

    if not update_row("products", prod_id, {"finished": True, "in_project_pan": False}):
        return False

    insert_row(
        "empties",
        {
            "brand": product.get("brand", ""),
            "shade": product.get("shade", ""),
            "category": product.get("category", ""),
            "date_emptied": str(datetime.date.today()),
        },
    )

    stats_update = {"xp": current_xp + FINISH_XP_REWARD}
    if any(k in category for k in LIP_CATEGORY_KEYWORDS):
        stats_update["finished_lip_products"] = int(stats.get("finished_lip_products", 0) or 0) + 1
    update_row("stats", stats.get("id", 1), stats_update)

    return True


def show_project_pan():
    st.markdown("### 🕯️ Usage Logging")
    products = st.session_state.db.get("products", [])
    pan_products = [p for p in products if p.get("in_project_pan", False) and not p.get("finished", False)]

    if not pan_products:
        st.info("No products selected for Project Pan yet. Go to 'Your Collection' and check 'Include in Project Pan' on items you want to focus on! 🕯️")
        return

    st.markdown(
        f"""
<div class="vanity-card" style="text-align:center; background:#f8f5fc;">
    <p style="margin:0; color:#6b5b7a; font-style:italic;">{daily_motivator()}</p>
</div>
""",
        unsafe_allow_html=True,
    )

    for p in pan_products:
        prod_id = p.get("id")
        brand = p.get("brand", "Unknown")
        shade = p.get("shade", "")
        price = float(p.get("price", 0) or 0)
        total_uses = int(p.get("total_uses", 0) or 0)
        daily_avg = float(p.get("daily_uses_avg", 1.0) or 1.0)

        # Estimate Finish Calculation
        est_info = calculate_estimated_pan_date(
            total_uses=total_uses,
            daily_uses_avg=daily_avg,
            created_at=p.get("created_at")
        )

        cost_per_use_line = (
            f"{(price / total_uses):.2f} {esc(p.get('currency', 'GBP'))} / use"
            if total_uses > 0
            else "No uses logged yet"
        )

        st.markdown(
            f"""
<div class="vanity-card">
    <h4 style="margin:0 0 0.4rem 0; font-family:'Playfair Display', serif;">{esc(brand)} — {esc(shade)}</h4>
    <p style="margin:0;">Total logged uses: <b>{total_uses}</b></p>
    <p style="margin:0;">Cost per use: <b>{cost_per_use_line}</b></p>
    <div class="progress-bg">
        <div class="progress-fill" style="width: {est_info['progress_pct']}%;"></div>
    </div>
    <p style="margin:0; font-size:0.9rem; color:#6b5b7a;">Estimated Pan Date: <b>{est_info['est_date_str']}</b> ({est_info['days_left']} days left)</p>
</div>
""",
            unsafe_allow_html=True,
        )

        # Per-product nudges
        if total_uses == 0:
            st.caption("🕸️ Untouched so far — dust it off today!")
        elif 0 < est_info['days_left'] <= 7:
            st.caption(f"✨ Almost there — about {est_info['days_left']} day(s) left on {brand}!")

        col1, col2 = st.columns(2)
        if col1.button("+1 Use ✨", key=f"add_1_{prod_id}"):
            if update_row("products", prod_id, {"total_uses": total_uses + 1}):
                st.session_state.db = load_cloud_data()
                st.rerun()

        if col2.button("🕯️ Mark Finished", key=f"finish_{prod_id}"):
            if mark_product_finished(p):
                st.session_state.db = load_cloud_data()
                st.success(f"🕯️ {brand} — {shade} is finished! +{FINISH_XP_REWARD} XP earned.")
                st.rerun()

        new_daily_avg = st.slider(
            f"Daily usage rate for {brand}",
            min_value=0.1,
            max_value=5.0,
            value=daily_avg,
            step=0.1,
            key=f"slider_{prod_id}",
        )
        if st.button("Save usage rate", key=f"save_rate_{prod_id}"):
            if new_daily_avg != daily_avg:
                if update_row("products", prod_id, {"daily_uses_avg": new_daily_avg}):
                    st.session_state.db = load_cloud_data()
                    st.success(f"Updated daily usage rate for {brand}.")
                    st.rerun()


FULL_FACE_SLOTS = [
    ("Lip Balm", ["lip balm", "balm"]),
    ("Lip Color (Gloss or Lipstick)", ["lip gloss", "gloss", "lipstick"]),
    ("Eyeshadow Palette", ["eyeshadow palette", "eyeshadow", "palette"]),
    ("Mascara", ["mascara"]),
    ("Eyeliner", ["eyeliner", "eye liner"]),
    ("Lip Liner", ["lip liner", "lipliner"]),
]


def _matches_slot(category_text, keywords):
    category_text = (category_text or "").lower()
    return any(k in category_text for k in keywords)


def smart_pick(candidates):
    if not candidates:
        return None
    weights = [1.0 / (int(p.get("total_uses", 0) or 0) + 1) for p in candidates]
    return random.choices(candidates, weights=weights, k=1)[0]


def build_full_face_routine(products):
    active_products = [p for p in products if not p.get("finished", False)]
    routine = {}
    missing_slots = []
    for slot_name, keywords in FULL_FACE_SLOTS:
        candidates = [p for p in active_products if _matches_slot(p.get("category"), keywords)]
        pick = smart_pick(candidates)
        if pick:
            routine[slot_name] = pick
        else:
            missing_slots.append(slot_name)
    return routine, missing_slots


ROULETTE_SINGLE_XP = 10
ROULETTE_FULL_XP = 25


def award_xp(amount):
    stats = st.session_state.db.get("stats", {})
    current_xp = int(stats.get("xp", 0) or 0)
    update_row("stats", stats.get("id", 1), {"xp": current_xp + amount})


def _clear_roulette_state():
    for key in ("roulette_mode", "roulette_single", "roulette_full", "roulette_missing"):
        st.session_state.pop(key, None)


def show_roulette():
    st.markdown("### 🧙‍♀️ Beauty Roulette Challenge")
    products = st.session_state.db.get("products", [])
    active_products = [p for p in products if not p.get("finished", False)]
    if not active_products:
        st.warning("Your product set is empty (or everything's finished). Add some products!")
        return

    col_single, col_full = st.columns(2)
    with col_single:
        if st.button("🔮 Single Product"):
            st.session_state.roulette_single = smart_pick(active_products)
            st.session_state.roulette_mode = "single"
    with col_full:
        if st.button("🧙‍♀️ Full Face Routine"):
            routine, missing = build_full_face_routine(products)
            st.session_state.roulette_full = routine
            st.session_state.roulette_missing = missing
            st.session_state.roulette_mode = "full"

    mode = st.session_state.get("roulette_mode")

    if mode == "single" and st.session_state.get("roulette_single"):
        item = st.session_state.roulette_single
        st.success("🌟 The spirits have chosen today's product!")
        st.markdown(render_product_card(item), unsafe_allow_html=True)

        col_a, col_b, col_c = st.columns(3)
        if col_a.button("✅ Accept"):
            total_uses = int(item.get("total_uses", 0) or 0)
            if update_row("products", item["id"], {"total_uses": total_uses + 1}):
                award_xp(ROULETTE_SINGLE_XP)
                st.session_state.db = load_cloud_data()
                _clear_roulette_state()
                st.success(f"🕯️ Logged a use and earned +{ROULETTE_SINGLE_XP} XP!")
                st.rerun()
        if col_b.button("❌ Decline"):
            _clear_roulette_state()
            st.rerun()
        if col_c.button("🔁 Remix"):
            st.session_state.roulette_single = smart_pick(active_products)
            st.rerun()

    elif mode == "full":
        routine = st.session_state.get("roulette_full") or {}
        missing = st.session_state.get("roulette_missing") or []
        if routine:
            st.success("🧙‍♀️ Your spell is cast — here's today's full look!")
            for slot_name, item in routine.items():
                st.caption(slot_name)
                st.markdown(render_product_card(item), unsafe_allow_html=True)
        if missing:
            st.info(
                "No match found for: **" + ", ".join(missing)
                + "**. Tag a product's category with one of these words to fill that slot next time."
            )

        if routine:
            col_a, col_b, col_c = st.columns(3)
            if col_a.button("✅ Accept", key="accept_full"):
                ok = True
                for item in routine.values():
                    total_uses = int(item.get("total_uses", 0) or 0)
                    if not update_row("products", item["id"], {"total_uses": total_uses + 1}):
                        ok = False
                if ok:
                    award_xp(ROULETTE_FULL_XP)
                    st.session_state.db = load_cloud_data()
                    _clear_roulette_state()
                    st.success(f"🕯️ Full look logged and earned +{ROULETTE_FULL_XP} XP!")
                    st.rerun()
            if col_b.button("❌ Decline", key="decline_full"):
                _clear_roulette_state()
                st.rerun()
            if col_c.button("🔁 Remix", key="remix_full"):
                new_routine, new_missing = build_full_face_routine(products)
                st.session_state.roulette_full = new_routine
                st.session_state.roulette_missing = new_missing
                st.rerun()


def show_analytics():
    st.markdown("### 🐈‍⬛ Beauty Stats & Analytics")
    products = st.session_state.db.get("products", [])
    empties = st.session_state.db.get("empties", [])
    stats = st.session_state.db.get("stats", {})

    total_value = sum(float(p.get("price", 0) or 0) for p in products)
    total_uses = sum(int(p.get("total_uses", 0) or 0) for p in products)

    start_date_str = stats.get("no_buy_start_date", str(datetime.date.today()))
    try:
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        no_buy_days = (datetime.date.today() - start_date).days
    except (ValueError, TypeError):
        no_buy_days = 0

    st.markdown(
        f"""
<div class="vanity-card" style="text-align:center;">
    <h2 style="margin:0; color:#4a3468; font-size:2.4rem;">{no_buy_days} Days</h2>
    <p style="margin:0; color:#8c7aa9;">Low-Buy / No-Buy Streak 🌿</p>
</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
<div class="vanity-card">
    <p style="margin:0; font-size:0.85rem; color:#8c7aa9;">Collection Value</p>
    <h3 style="margin:0.2rem 0; color:#3a3342;">{total_value:.2f} GBP</h3>
</div>
""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
<div class="vanity-card">
    <p style="margin:0; font-size:0.85rem; color:#8c7aa9;">Total Uses</p>
    <h3 style="margin:0.2rem 0; color:#3a3342;">{total_uses} x</h3>
</div>
""",
            unsafe_allow_html=True,
        )

    if products:
        st.markdown("#### 🎨 By Category")
        df = pd.DataFrame(products)
        df["price"] = pd.to_numeric(df.get("price", 0), errors="coerce").fillna(0)
        df["category"] = df.get("category", "Uncategorized").fillna("Uncategorized") if "category" in df else "Uncategorized"

        cat_spend = df.groupby("category", as_index=False)["price"].sum().sort_values("price", ascending=False)
        fig = px.bar(
            cat_spend,
            x="category",
            y="price",
            labels={"category": "Category", "price": "Spend (GBP)"},
            color_discrete_sequence=["#a98fd2"],
        )
        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            font_color="#382a4b",
            margin=dict(l=10, r=10, t=10, b=10),
            height=280,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### 💸 Cost Per Use")
    priced_products = [
        p for p in products if int(p.get("total_uses", 0) or 0) > 0
    ]
    if not priced_products:
        st.info("Log a few uses on your products to see cost-per-use here.")
    else:
        ranked = sorted(
            priced_products,
            key=lambda p: float(p.get("price", 0) or 0) / int(p.get("total_uses", 1) or 1),
        )
        best = ranked[:3]
        worst = list(reversed(ranked[-3:])) if len(ranked) > 3 else []

        st.caption("Best value (lowest cost per use)")
        for p in best:
            cpu = float(p.get("price", 0) or 0) / int(p.get("total_uses", 1) or 1)
            st.markdown(
                f"""
<div class="vanity-card">
    <h4 style="margin:0;">{esc(p.get('brand', ''))} — {esc(p.get('shade', ''))}</h4>
    <p style="margin:4px 0 0 0; color:#8c7aa9; font-size:0.85rem;">{cpu:.2f} GBP per use · {int(p.get('total_uses', 0) or 0)} uses</p>
</div>
""",
                unsafe_allow_html=True,
            )

        if worst:
            st.caption("Worst value (highest cost per use)")
            for p in worst:
                cpu = float(p.get("price", 0) or 0) / int(p.get("total_uses", 1) or 1)
                st.markdown(
                    f"""
<div class="vanity-card">
    <h4 style="margin:0;">{esc(p.get('brand', ''))} — {esc(p.get('shade', ''))}</h4>
    <p style="margin:4px 0 0 0; color:#8c7aa9; font-size:0.85rem;">{cpu:.2f} GBP per use · {int(p.get('total_uses', 0) or 0)} uses</p>
</div>
""",
                    unsafe_allow_html=True,
                )

    if products:
        st.markdown("#### 🏆 Usage Highlights")
        by_uses = sorted(products, key=lambda p: int(p.get("total_uses", 0) or 0), reverse=True)
        most_used = by_uses[0] if by_uses else None
        unused = [p for p in products if int(p.get("total_uses", 0) or 0) == 0]

        col_a, col_b = st.columns(2)
        with col_a:
            if most_used:
                st.markdown(
                    f"""
<div class="vanity-card">
    <p style="margin:0; font-size:0.85rem; color:#8c7aa9;">Most Used</p>
    <h4 style="margin:0.2rem 0;">{esc(most_used.get('brand', ''))} — {esc(most_used.get('shade', ''))}</h4>
    <p style="margin:0; color:#8c7aa9; font-size:0.85rem;">{int(most_used.get('total_uses', 0) or 0)} uses</p>
</div>
""",
                    unsafe_allow_html=True,
                )
        with col_b:
            st.markdown(
                f"""
<div class="vanity-card">
    <p style="margin:0; font-size:0.85rem; color:#8c7aa9;">Never Used</p>
    <h4 style="margin:0.2rem 0;">{len(unused)} item(s)</h4>
    <p style="margin:0; color:#8c7aa9; font-size:0.85rem;">Sitting untouched in your collection</p>
</div>
""",
                unsafe_allow_html=True,
            )

    st.markdown("#### 🗑️ Empties")
    if not empties:
        st.info("No empties recorded.")
    else:
        for e in empties:
            st.markdown(
                f"""
<div class="vanity-card">
    <h4 style="margin:0;">🎉 {esc(e.get('brand'))} — {esc(e.get('shade'))}</h4>
    <p style="margin:4px 0 0 0; color:#8c7aa9; font-size:0.85rem;">Emptied!</p>
</div>
""",
                unsafe_allow_html=True,
            )


def show_wishlist():
    st.markdown("### 🔮 Wishlist")
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
                "notes": notes_input,
                "date_added": str(datetime.date.today()),
            }
            if brand_input.strip() and item_input.strip():
                if insert_row("wishlist", new_item):
                    st.session_state.db = load_cloud_data()
                    st.rerun()
            else:
                st.warning("Please enter at least a brand and item.")

    wishlist_items = st.session_state.db.get("wishlist", [])
    if not wishlist_items:
        st.info("Your wishlist is empty.")
        return

    for w in wishlist_items:
        date_added_str = w.get("date_added")
        cooling_badge = "⏳ Cooling-off period"
        try:
            if date_added_str:
                date_added = datetime.datetime.strptime(date_added_str, "%Y-%m-%d").date()
                days_elapsed = (datetime.date.today() - date_added).days
                days_left = 14 - days_elapsed
                if days_left > 0:
                    cooling_badge = f"⏳ {days_left}-Day Cooling Off Remaining"
                else:
                    cooling_badge = "✅ Cooling-off period over"
        except (ValueError, TypeError):
            pass

        st.markdown(
            f"""
<div class="vanity-card">
    <h4 style="margin:0;">{esc(w.get('brand', ''))} — {esc(w.get('item', ''))}</h4>
    <p style="margin:6px 0; color:#6b5b7a; font-size:0.88rem;">{esc(w.get('notes', ''))}</p>
    <span style="background:#e8dff5; color:#4a3468; padding:3px 8px; border-radius:6px; font-size:0.78rem; font-weight:500;">{cooling_badge}</span>
</div>
""",
            unsafe_allow_html=True,
        )


def show_reward_shop():
    st.markdown("### 🪄 Reward Shop")
    stats = st.session_state.db.get("stats", {})
    xp = int(stats.get("xp", 0) or 0)
    redeemed = int(stats.get("rewards_redeemed", 0) or 0)

    st.markdown(
        f"""
<div class="vanity-card" style="text-align:center;">
    <h2 style="margin:0; color:#4a3468; font-size:2.4rem;">{xp} XP</h2>
    <p style="margin:0; color:#8c7aa9;">Available to spend</p>
</div>
""",
        unsafe_allow_html=True,
    )

    rewards = [
        {"name": "Treat yourself to a mini item", "cost": 50},
        {"name": "One 'skip the no-buy' pass", "cost": 150},
        {"name": "Full-size splurge item", "cost": 300},
    ]

    for r in rewards:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(
                f"""
<div class="vanity-card">
    <h4 style="margin:0;">{esc(r['name'])}</h4>
    <p style="margin:4px 0 0 0; color:#8c7aa9; font-size:0.85rem;">{r['cost']} XP</p>
</div>
""",
                unsafe_allow_html=True,
            )
        with col2:
            disabled = xp < r["cost"]
            if st.button("Redeem", key=f"redeem_{r['name']}", disabled=disabled):
                if update_row(
                    "stats",
                    stats.get("id", 1),
                    {"xp": xp - r["cost"], "rewards_redeemed": redeemed + 1},
                ):
                    st.session_state.db = load_cloud_data()
                    st.rerun()

    st.caption(f"Rewards redeemed so far: {redeemed}")


# ---------------------------------------------------------
# App state & data load
# ---------------------------------------------------------
st.session_state.db = load_cloud_data()
if st.session_state.get("_last_load_error"):
    st.warning("Some data couldn't be loaded from the cloud. Showing what's available.")

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# ---------------------------------------------------------
# Header & Navigation
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
# Routing and Navigation Buttons
# ---------------------------------------------------------
pages = {
    "Collection": "🧪 Your Collection",
    "Project Pan": "🕯️ Project Pan",
    "Roulette": "🧙‍♀️ Beauty Roulette",
    "Analytics": "🐈‍⬛ Beauty Stats",
    "Wishlist": "🔮 Wishlist",
    "Reward Shop": "🪄 Reward Shop"
}

# Main Menu Container
st.markdown('<div class="home-menu">', unsafe_allow_html=True)
st.markdown('<div class="home-menu-label">Where would you like to wander?</div>', unsafe_allow_html=True)

nav_cols = st.columns(2)
for idx, (page_key, label) in enumerate(pages.items()):
    col = nav_cols[idx % 2]
    if col.button(label, key=f"nav_{page_key}"):
        st.session_state.current_page = page_key
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# Page Routing
if st.session_state.current_page == "Collection":
    show_collection()
elif st.session_state.current_page == "Project Pan":
    show_project_pan()
elif st.session_state.current_page == "Roulette":
    show_roulette()
elif st.session_state.current_page == "Analytics":
    show_analytics()
elif st.session_state.current_page == "Wishlist":
    show_wishlist()
elif st.session_state.current_page == "Reward Shop":
    show_reward_shop()
