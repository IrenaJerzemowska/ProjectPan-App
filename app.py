import datetime
import random
import pandas as pd
from st_supabase_connection import SupabaseConnection
import streamlit as st

# ---------------------------------------------------------
# Page Configuration & Clean Aesthetic Theme
# ---------------------------------------------------------
st.set_page_config(
    page_title="Vanity Sanctuary",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Supabase Cloud Connection Initialization
# ---------------------------------------------------------
conn = st.connection("supabase", type=SupabaseConnection)

CATEGORIES = [
    "foundation",
    "concealer",
    "powder",
    "powder contour",
    "cream contour",
    "liquid contour",
    "powder blush",
    "cream blush",
    "liquid blush",
    "highlighter",
    "eyeshadow palette",
    "lip gloss",
    "lipstick",
    "eyeliner",
    "mascara",
    "lip liner",
    "lip mask",
    "lip balm",
    "setting spray",
    "brow gel",
    "brow pen",
]

LIP_CATEGORIES = ["lip gloss", "lipstick", "lip liner", "lip mask", "lip balm"]


def load_cloud_data():
    try:
        products_res = conn.table("products").select("*").execute()
        wishlist_res = conn.table("wishlist").select("*").execute()
        empties_res = conn.table("empties").select("*").execute()
        stats_res = conn.table("stats").select("*").execute()

        products = products_res.data if products_res and products_res.data else []
        wishlist = wishlist_res.data if wishlist_res and wishlist_res.data else []
        empties = empties_res.data if empties_res and empties_res.data else []

        stats_data = stats_res.data[0] if stats_res and stats_res.data else {}
        stats = {
            "id": stats_data.get("id", 1),
            "finished_lip_products": stats_data.get("finished_lip_products", 0),
            "no_buy_start_date": stats_data.get(
                "no_buy_start_date", str(datetime.date.today())
            ),
            "xp": stats_data.get("xp", 0),
            "rewards_redeemed": stats_data.get("rewards_redeemed", 0),
            "active_challenge": stats_data.get("active_challenge", None),
        }
        return {
            "products": products,
            "wishlist": wishlist,
            "empties": empties,
            "stats": stats,
        }
    except Exception as e:
        return {
            "products": [],
            "wishlist": [],
            "empties": [],
            "stats": {
                "id": 1,
                "finished_lip_products": 0,
                "no_buy_start_date": str(datetime.date.today()),
                "xp": 0,
                "rewards_redeemed": 0,
                "active_challenge": None,
            },
        }


if "db" not in st.session_state:
    st.session_state.db = load_cloud_data()

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"


def calculate_days_owned(purchase_date_str):
    try:
        p_date = datetime.datetime.strptime(
            purchase_date_str, "%Y-%m-%d"
        ).date()
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


def estimate_pan_completion(category, daily_uses):
    if daily_uses <= 0:
        return None, None, 0
    cat = category.lower()

    if "lipstick" in cat:
        days_needed_base = 730
    elif "liquid lipstick" in cat:
        days_needed_base = 270
    elif "lip gloss" in cat:
        days_needed_base = 135
    elif "lip balm" in cat:
        days_needed_base = 90
    elif "lip mask" in cat:
        days_needed_base = 225
    elif "foundation" in cat:
        days_needed_base = 150
    elif "concealer" in cat:
        days_needed_base = 225
    elif "powder" in cat:
        days_needed_base = 300
    elif "setting spray" in cat:
        days_needed_base = 120
    elif "powder contour" in cat or "contour" in cat:
        days_needed_base = 300
    elif "cream contour" in cat:
        days_needed_base = 240
    elif "liquid contour" in cat:
        days_needed_base = 200
    elif "powder blush" in cat or "blush" in cat:
        days_needed_base = 365
    elif "cream blush" in cat:
        days_needed_base = 270
    elif "liquid blush" in cat:
        days_needed_base = 210
    elif "highlighter" in cat:
        days_needed_base = 540
    elif "eyeshadow palette" in cat:
        days_needed_base = 1095
    elif "mascara" in cat:
        days_needed_base = 120
    elif "eyeliner" in cat:
        days_needed_base = 210
    elif "brow pen" in cat:
        days_needed_base = 120
    elif "brow gel" in cat:
        days_needed_base = 150
    else:
        days_needed_base = 250

    days_needed = int(days_needed_base / daily_uses)
    completion_date = datetime.date.today() + datetime.timedelta(
        days=max(days_needed, 1)
    )
    return days_needed, completion_date, days_needed_base


def check_and_update_challenge(product_id, uses_added=1):
    """Sprawdza i aktualizuje progres aktywnego wyzwania po użyciu kosmetyku."""
    stats = st.session_state.db.get("stats", {})
    challenge = stats.get("active_challenge")

    if challenge and challenge.get("product_id") == product_id:
        challenge["current_uses"] += uses_added
        target = challenge.get("target_uses", 1)
        
        if challenge["current_uses"] >= target:
            bonus_xp = challenge.get("reward_xp", 15)
            new_total_xp = stats.get("xp", 0) + bonus_xp
            stats_id = stats.get("id", 1)
            
            # Wyszukaj nazwę produktu dla komunikatu sukcesu
            products = st.session_state.db.get("products", [])
            prod_name = next((f"{p['brand']} - {p['shade']}" for p in products if p['id'] == product_id), "Product")
            
            # Zeruj wyzwanie i dodaj premię XP
            conn.table("stats").update({
                "xp": new_total_xp,
                "active_challenge": None
            }).eq("id", stats_id).execute()
            
            st.session_state.challenge_completed_msg = f"🎉 Wyzwanie Ukończone! Użyto {prod_name} {target}x. Otrzymujesz +{bonus_xp} XP!"
        else:
            stats_id = stats.get("id", 1)
            conn.table("stats").update({
                "active_challenge": challenge
            }).eq("id", stats_id).execute()


# ---------------------------------------------------------
# Header Block
# ---------------------------------------------------------
st.markdown(
    """
<div class="sanctuary-header">
    <h1>Vanity Sanctuary</h1>
    <p>Minimalist inventory & project pan (Cloud Synced)</p>
</div>
""",
    unsafe_allow_html=True,
)

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
        if st.button("Roulette\nChallenge\n\n🎲", key="btn_roulette", use_container_width=True):
            st.session_state.current_page = "Roulette Challenge"
            st.rerun()

    if st.button("Beauty Stats & Analytics 🐈‍⬛", key="btn_stats", use_container_width=True):
        st.session_state.current_page = "Analytics"
        st.rerun()

    st.markdown(
        """
    <div class="quote-card">
        <p>Use what you love.<br>Finish what you start.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

else:
    if st.button("← Back to Menu"):
        st.session_state.db = load_cloud_data()
        st.session_state.current_page = "Home"
        st.rerun()

    st.markdown("---")

    # --- COLLECTION ---
    if st.session_state.current_page == "Collection":
        st.markdown("### Your Collection")

        if "challenge_completed_msg" in st.session_state and st.session_state.challenge_completed_msg:
            st.balloons()
            st.success(st.session_state.challenge_completed_msg)
            st.session_state.challenge_completed_msg = None

        products = st.session_state.db.get("products", [])
        cat_counts = {}
        for p in products:
            c = p.get("category", "Uncategorized")
            cat_counts[c] = cat_counts.get(c, 0) + 1

        with st.expander("📊 View Category Counts"):
            count_cols = st.columns(2)
            sorted_cats = sorted(cat_counts.items(), key=lambda x: x[1], reverse=True)
            for idx, (cat_name, count) in enumerate(sorted_cats):
                with count_cols[idx % 2]:
                    st.markdown(
                        f"<span style='font-size:0.9rem; color:#4a3468;'>•"
                        f" {cat_name.title()}: <b>{count}</b></span>",
                        unsafe_allow_html=True,
                    )

        st.markdown("<br>", unsafe_allow_html=True)

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
        finishing_id_key = "finishing_product_id"

        if not products:
            st.markdown(
                """
                <div class="vanity-card" style="text-align:center; padding:2rem;">
                    <p style="color:#8c7aa9; margin:0;">Your collection is currently empty.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            filter_cat = st.selectbox(
                "Category Filter", ["All Categories"] + CATEGORIES
            )
            filtered_products = [
                p
                for p in products
                if filter_cat == "All Categories"
                or p["category"].lower() == filter_cat.lower()
            ]

            for p in reversed(filtered_products):
                days = calculate_days_owned(p["purchase_date"])
                cpu = calculate_cost_per_use(p["price"], p.get("total_uses", 0))
                is_pan = p.get("in_project_pan", False)
                edit_mode_key = f"edit_mode_{p['id']}"

                st.markdown(
                    f"""
                    <div class="vanity-card">
                        <h4 style="margin:0 0 0.4rem 0; font-family:'Playfair Display', serif;">{p['brand']} — <span style="font-weight:400;">{p['shade']}</span></h4>
                        <p style="margin:0 0 0.6rem 0; color:#8c7aa9; font-size:0.88rem;">Category: {p['category']}</p>
                        <p style="margin:0; font-size:0.9rem;"><strong>Price:</strong> {p['price']:.2f} {p['currency']} | <strong>Age:</strong> {days} days | <strong>Uses:</strong> {p.get('total_uses', 0)} | <strong>CPU:</strong> {cpu:.2f} {p['currency']}</p>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    "<hr style='margin: 10px 0; border-color: #eee0f8;'>",
                    unsafe_allow_html=True,
                )
                col_info, col_act = st.columns([2, 1])
                with col_info:
                    if is_pan:
                        st.markdown(
                            "<p style='font-size:0.8rem; color:#6b5b7a; margin:0;'>✨ Active in Project Pan</p>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            "<p style='font-size:0.8rem; color:#8c7aa9; margin:0;'>In Collection</p>",
                            unsafe_allow_html=True,
                        )
                with col_act:
                    if st.button("+ Log Use", key=f"quick_use_{p['id']}"):
                        p["total_uses"] = p.get("total_uses", 0) + 1
                        p["last_used_timestamp"] = datetime.datetime.now().isoformat()
                        stats_id = st.session_state.db["stats"].get("id", 1)
                        new_xp = max(st.session_state.db["stats"].get("xp", 0) + 5, 0)

                        conn.table("products").update({
                            "total_uses": p["total_uses"],
                            "last_used_timestamp": p["last_used_timestamp"],
                        }).eq("id", p["id"]).execute()
                        conn.table("stats").update({"xp": new_xp}).eq("id", stats_id).execute()

                        # Sprawdź status wyzwania Roulette
                        check_and_update_challenge(p["id"], uses_added=1)

                        st.session_state.db = load_cloud_data()
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

                if edit_mode_key not in st.session_state:
                    st.session_state[edit_mode_key] = False

                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    if st.button(
                        "Unpan" if is_pan else "Pan ✨", key=f"pan_{p['id']}"
                    ):
                        p["in_project_pan"] = not is_pan
                        if p["in_project_pan"]:
                            p["last_used_timestamp"] = datetime.datetime.now().isoformat()
                        conn.table("products").update(
                            {"in_project_pan": p["in_project_pan"]}
                        ).eq("id", p["id"]).execute()
                        st.session_state.db = load_cloud_data()
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
                        conn.table("products").delete().eq("id", p["id"]).execute()
                        st.session_state.db = load_cloud_data()
                        st.rerun()

                if st.session_state.get(finishing_id_key) == p["id"]:
                    with st.form(key=f"review_form_{p['id']}"):
                        st.markdown(
                            f"**Review & Grade Finished Product: {p['brand']} -"
                            f" {p['shade']}**"
                        )
                        finish_rating = st.slider("Rating (Stars)", 0, 5, 5, 1)
                        finish_review = st.text_area("Thoughts / Mini Review:")
                        rc1, rc2 = st.columns(2)
                        with rc1:
                            submit_review = st.form_submit_button("Complete & Archive 🪦")
                        with rc2:
                            cancel_review = st.form_submit_button("Cancel")

                        stats_id = st.session_state.db["stats"].get("id", 1)
                        if submit_review:
                            is_lip = p["category"].lower() in LIP_CATEGORIES
                            fin_lips = st.session_state.db["stats"].get(
                                "finished_lip_products", 0
                            ) + (1 if is_lip else 0)
                            new_xp = max(
                                st.session_state.db["stats"].get("xp", 0) + 50, 0
                            )

                            empty_item = {
                                "id": p["id"],
                                "brand": p["brand"],
                                "shade": p["shade"],
                                "category": p["category"],
                                "price": p["price"],
                                "currency": p["currency"],
                                "purchase_date": p["purchase_date"],
                                "total_uses": p.get("total_uses", 0),
                                "finished_date": str(datetime.date.today()),
                                "final_days_owned": calculate_days_owned(
                                    p["purchase_date"]
                                ),
                                "final_cpu": calculate_cost_per_use(
                                    p["price"], p.get("total_uses", 0)
                                ),
                                "rating": finish_rating,
                                "review": finish_review,
                            }

                            conn.table("empties").insert(empty_item).execute()
                            conn.table("products").delete().eq("id", p["id"]).execute()
                            conn.table("stats").update({
                                "finished_lip_products": fin_lips,
                                "xp": new_xp,
                            }).eq("id", stats_id).execute()

                            st.session_state[finishing_id_key] = None
                            st.session_state.db = load_cloud_data()
                            st.rerun()
                        if cancel_review:
                            st.session_state[finishing_id_key] = None
                            st.rerun()

                if st.session_state.get(edit_mode_key):
                    with st.form(key=f"edit_form_{p['id']}"):
                        new_brand = st.text_input("Brand", value=p["brand"])
                        new_shade = st.text_input(
                            "Shade", value=p["shade"] if p["shade"] != "N/A" else ""
                        )
                        new_category = st.selectbox(
                            "Category",
                            CATEGORIES,
                            index=(
                                CATEGORIES.index(p["category"].lower())
                                if p["category"].lower() in CATEGORIES
                                else 0
                            ),
                        )
                        new_price = st.number_input(
                            "Price", min_value=0.0, value=float(p["price"])
                        )
                        new_currency = st.selectbox(
                            "Currency",
                            ["GBP", "PLN", "EUR", "USD"],
                            index=(
                                ["GBP", "PLN", "EUR", "USD"].index(p["currency"])
                                if p["currency"] in ["GBP", "PLN", "EUR", "USD"]
                                else 0
                            ),
                        )

                        old_uses = p.get("total_uses", 0)
                        new_uses_input = st.number_input(
                            "Total Uses", min_value=0, value=int(old_uses)
                        )

                        if st.form_submit_button("Save Changes ✓"):
                            uses_diff = int(new_uses_input) - int(old_uses)
                            current_xp = st.session_state.db["stats"].get("xp", 0)
                            new_xp = max(current_xp + (uses_diff * 5), 0)

                            conn.table("products").update({
                                "brand": new_brand,
                                "shade": new_shade if new_shade else "N/A",
                                "category": new_category,
                                "price": float(new_price),
                                "currency": new_currency,
                                "total_uses": int(new_uses_input),
                            }).eq("id", p["id"]).execute()

                            stats_id = st.session_state.db["stats"].get("id", 1)
                            conn.table("stats").update({"xp": new_xp}).eq("id", stats_id).execute()

                            st.session_state[edit_mode_key] = False
                            st.session_state.db = load_cloud_data()
                            st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

    # --- ROULETTE CHALLENGE ---
    elif st.session_state.current_page == "Roulette Challenge":
        st.markdown("### Roulette Challenge 🎲✨")
        st.markdown(
            "<p style='color:#6b5b7a; font-size:0.9rem;'>Wylosuj kosmetyk, który leży w szufladzie najdłużej, podejmij wyzwanie i zgarniaj dodatkowe punkty XP!</p>",
            unsafe_allow_html=True,
        )

        if "challenge_completed_msg" in st.session_state and st.session_state.challenge_completed_msg:
            st.balloons()
            st.success(st.session_state.challenge_completed_msg)
            st.session_state.challenge_completed_msg = None

        stats = st.session_state.db.get("stats", {})
        active_ch = stats.get("active_challenge")

        # Pokaż aktywne wyzwanie jeśli istnieje
        if active_ch:
            products = st.session_state.db.get("products", [])
            ch_product = next((p for p in products if p["id"] == active_ch.get("product_id")), None)

            if ch_product:
                st.markdown(
                    f"""
                    <div class="vanity-card" style="border: 2px solid #b5a4c9; background: #faf7ff;">
                        <span style="background:#8c7aa9; color:#fff; padding:2px 8px; border-radius:4px; font-size:0.75rem;">AKTYWNE WYZWANIE</span>
                        <h4 style="margin:0.5rem 0 0.3rem 0; font-family:'Playfair Display', serif;">{ch_product['brand']} — {ch_product['shade']}</h4>
                        <p style="margin:0 0 0.5rem 0; color:#8c7aa9; font-size:0.85rem;">Kategoria: {ch_product['category']}</p>
                        <p style="margin:0; font-size:0.9rem;">Cel: <b>{active_ch['current_uses']} / {active_ch['target_uses']} użyć</b> | Nagroda: <b>+{active_ch['reward_xp']} XP</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(min(active_ch['current_uses'] / active_ch['target_uses'], 1.0))

                col_log_r, col_abandon_r = st.columns([2, 1])
                with col_log_r:
                    if st.button("➕ Log Challenge Use (+1 Use)", key="btn_challenge_log"):
                        ch_product["total_uses"] = ch_product.get("total_uses", 0) + 1
                        ch_product["last_used_timestamp"] = datetime.datetime.now().isoformat()
                        
                        conn.table("products").update({
                            "total_uses": ch_product["total_uses"],
                            "last_used_timestamp": ch_product["last_used_timestamp"]
                        }).eq("id", ch_product["id"]).execute()
                        
                        check_and_update_challenge(ch_product["id"], uses_added=1)
                        st.session_state.db = load_cloud_data()
                        st.rerun()

                with col_abandon_r:
                    if st.button("Anuluj Wyzwanie ❌", key="btn_challenge_cancel"):
                        stats_id = stats.get("id", 1)
                        conn.table("stats").update({"active_challenge": None}).eq("id", stats_id).execute()
                        st.session_state.db = load_cloud_data()
                        st.rerun()

            else:
                # Jeśli produkt został w międzyczasie usunięty
                stats_id = stats.get("id", 1)
                conn.table("stats").update({"active_challenge": None}).eq("id", stats_id).execute()
                st.rerun()

            st.markdown("<hr style='margin:20px 0; border-color:#e2d8ee;'>", unsafe_allow_html=True)

        # Sekcja generatora nowego wyzwania
        st.markdown("#### Wylosuj Nowe Wyzwanie")
        roulette_cat = st.selectbox("Filtruj kadrę do losowania:", ["Wszystkie Kategorie"] + CATEGORIES)
        challenge_type = st.radio("Wybierz tryb wyzwania:", ["Daily Touch (1 Użycie) — +15 XP", "10-Use Focus (10 Użyć) — +100 XP"])

        products_pool = st.session_state.db.get("products", [])
        if roulette_cat != "Wszystkie Kategorie":
            products_pool = [p for p in products_pool if p["category"].lower() == roulette_cat.lower()]

        if st.button("🎲 Zakręć Rulą Pan!", use_container_width=True):
            if not products_pool:
                st.warning("Brak produktów spełniających wybrane kryteria.")
            else:
                # Inteligentny podział i priorytetyzacja (wiek + data ostatniego użycia)
                def calculate_neglect_score(p):
                    days_owned = calculate_days_owned(p.get("purchase_date", str(datetime.date.today())))
                    last_used_str = p.get("last_used_timestamp", "1970-01-01T00:00:00")
                    try:
                        last_used_dt = datetime.datetime.fromisoformat(last_used_str)
                        days_unused = max((datetime.datetime.now() - last_used_dt).days, 0)
                    except Exception:
                        days_unused = 300
                    return (days_owned * 0.4) + (days_unused * 0.6)

                # Sortuj malejąco wg zapomnienia
                sorted_pool = sorted(products_pool, key=calculate_neglect_score, reverse=True)
                
                # Wybierz z top 3 najbardziej zakurzonych produktów
                top_neglected = sorted_pool[:min(3, len(sorted_pool))]
                selected_prod = random.choice(top_neglected)
                st.session_state.roulette_selected = selected_prod

        if "roulette_selected" in st.session_state and st.session_state.roulette_selected:
            sp = st.session_state.roulette_selected
            days = calculate_days_owned(sp["purchase_date"])

            st.markdown(
                f"""
                <div class="vanity-card" style="text-align:center; background:#ffffff;">
                    <p style="color:#8c7aa9; font-size:0.8rem; margin:0;">WYLOSOWANY KOSMETYK:</p>
                    <h3 style="margin:0.2rem 0; font-family:'Playfair Display', serif; color:#4a3468;">{sp['brand']}</h3>
                    <p style="margin:0 0 0.5rem 0; font-size:1.1rem; color:#6b5b7a;">Odcień: <b>{sp['shade']}</b> ({sp['category']})</p>
                    <p style="margin:0; font-size:0.85rem; color:#8c7aa9;">W Twojej kolekcji od {days} dni | Łącznie użyć: {sp.get('total_uses', 0)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            is_ten = "10-Use Focus" in challenge_type
            target_u = 10 if is_ten else 1
            reward_x = 100 if is_ten else 15

            if st.button("Akceptuj To Wyzwanie! ✨", use_container_width=True):
                new_challenge = {
                    "product_id": sp["id"],
                    "target_uses": target_u,
                    "current_uses": 0,
                    "reward_xp": reward_x,
                    "started_date": str(datetime.date.today())
                }
                stats_id = stats.get("id", 1)
                conn.table("stats").update({"active_challenge": new_challenge}).eq("id", stats_id).execute()
                
                st.session_state.roulette_selected = None
                st.session_state.db = load_cloud_data()
                st.rerun()

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
                        "last_used_timestamp": (
                            datetime.datetime.now().isoformat()
                            if int(initial_uses) > 0
                            else "1970-01-01T00:00:00"
                        ),
                        "in_project_pan": False,
                    }
                    conn.table("products").insert(new_item).execute()

                    if int(initial_uses) > 0:
                        current_xp = st.session_state.db["stats"].get("xp", 0)
                        new_xp = max(current_xp + (int(initial_uses) * 5), 0)
                        stats_id = st.session_state.db["stats"].get("id", 1)
                        conn.table("stats").update({"xp": new_xp}).eq("id", stats_id).execute()

                    st.success("Product added!")
                    st.session_state.db = load_cloud_data()
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
                st.markdown(
                    f"""
                    <div class="vanity-card">
                        <h4 style="margin:0 0 0.3rem 0; font-family:'Playfair Display', serif;">{e['brand']} — {e['shade']}</h4>
                        <p style="margin:0 0 0.4rem 0; color:#8c7aa9; font-size:0.85rem;">Finished on {e.get('finished_date', 'Unknown')} | Rating: {'⭐' * e.get('rating', 0)}</p>
                        <p style="margin:0; font-size:0.88rem;">Lifespan: {e.get('final_days_owned', 0)} days | Total Uses: {e.get('total_uses', 0)}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Delete from Graveyard 🗑️", key=f"del_empty_{e['id']}"):
                    conn.table("empties").delete().eq("id", e["id"]).execute()
                    st.session_state.db = load_cloud_data()
                    st.rerun()

    # --- PROJECT PAN ---
    elif st.session_state.current_page == "Project Pan":
        st.markdown("### Project Pan (Gamified) 🌕")

        if "challenge_completed_msg" in st.session_state and st.session_state.challenge_completed_msg:
            st.balloons()
            st.success(st.session_state.challenge_completed_msg)
            st.session_state.challenge_completed_msg = None

        current_xp = st.session_state.db.get("stats", {}).get("xp", 0)
        current_level_title, _ = get_pan_level(current_xp)

        st.markdown(
            f"""
            <div class="vanity-card" style="background-color: #f7f3fd; text-align: center;">
                <h4 style="margin:0; font-family:'Playfair Display', serif; color:#4a3468;">Rank: {current_level_title}</h4>
                <p style="margin:5px 0 0 0; font-size: 0.9rem; color:#8c7aa9;">Total XP: <b>{current_xp} XP</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        products = [
            p
            for p in st.session_state.db.get("products", [])
            if p.get("in_project_pan", False)
        ]
        products = sorted(
            products,
            key=lambda x: x.get(
                "last_used_timestamp", x.get("purchase_date", "1970-01-01")
            ),
            reverse=True,
        )

        if not products:
            st.info(
                "No active items in Project Pan. Tag items as panned from your"
                " collection."
            )
        else:
            for p in products:
                days = calculate_days_owned(p["purchase_date"])
                total_uses = p.get("total_uses", 0)
                cpu = calculate_cost_per_use(p["price"], total_uses)

                st.markdown(
                    f"""
                    <div class="vanity-card">
                        <h4 style="margin:0 0 1rem 0; font-family:'Playfair Display', serif;">{p['brand']} — {p['shade']}</h4>
                    """,
                    unsafe_allow_html=True,
                )

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(
                        f'<div class="metric-box"><div'
                        f' class="metric-value">{days}</div><div'
                        ' class="metric-label">Days Owned</div></div>',
                        unsafe_allow_html=True,
                    )
                with m2:
                    st.markdown(
                        f'<div class="metric-box"><div'
                        f' class="metric-value">{total_uses}</div><div'
                        ' class="metric-label">Uses</div></div>',
                        unsafe_allow_html=True,
                    )
                with m3:
                    st.markdown(
                        f'<div class="metric-box"><div class="metric-value">{cpu:.2f}'
                        f' {p["currency"]}</div><div class="metric-label">Cost /'
                        " Use</div></div>",
                        unsafe_allow_html=True,
                    )

                st.markdown("<br>", unsafe_allow_html=True)
                daily_uses_input = st.number_input(
                    "Estimated daily applications:",
                    min_value=1,
                    max_value=5,
                    value=1,
                    key=f"d_uses_{p['id']}",
                )
                d_needed, target_date, total_apps_needed = estimate_pan_completion(
                    p["category"], daily_uses_input
                )

                if d_needed and total_apps_needed > 0:
                    progress_ratio = min(float(total_uses) / total_apps_needed, 1.0)
                    st.markdown(
                        f"""
                        <div style="background-color: #f2ebfc; border-radius: 6px; padding: 0.8rem; margin-top: 10px; font-size: 0.88rem; color: #4a3468;">
                            🔮 <strong>Forecast:</strong> Approx. <b>{d_needed} days</b> ({target_date.strftime('%B %Y')}) to finish.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.progress(progress_ratio)

                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown(
                    "<p style='font-size:0.85rem; color:#8c7aa9;"
                    " margin-bottom:5px;'>Quick Use Counter:</p>",
                    unsafe_allow_html=True,
                )
                col_btn_minus, col_uses_disp, col_btn_plus = st.columns([1, 2, 1])
                with col_btn_minus:
                    if st.button("➖ -1", key=f"minus_{p['id']}"):
                        if p.get("total_uses", 0) > 0:
                            p["total_uses"] = p.get("total_uses", 0) - 1
                            current_xp = st.session_state.db["stats"].get("xp", 0)
                            new_xp = max(current_xp - 5, 0)
                            stats_id = st.session_state.db["stats"].get("id", 1)

                            conn.table("products").update(
                                {"total_uses": p["total_uses"]}
                            ).eq("id", p["id"]).execute()
                            conn.table("stats").update({"xp": new_xp}).eq("id", stats_id).execute()
                            st.session_state.db = load_cloud_data()
                            st.rerun()
                with col_uses_disp:
                    st.markdown(
                        f"<div style='text-align: center; padding-top: 5px; font-weight:"
                        f" bold;'>{total_uses} uses</div>",
                        unsafe_allow_html=True,
                    )
                with col_btn_plus:
                    if st.button("➕ +1", key=f"plus_{p['id']}"):
                        p["total_uses"] = p.get("total_uses", 0) + 1
                        p["last_used_timestamp"] = datetime.datetime.now().isoformat()
                        current_xp = st.session_state.db["stats"].get("xp", 0)
                        new_xp = max(current_xp + 5, 0)
                        stats_id = st.session_state.db["stats"].get("id", 1)

                        conn.table("products").update({
                            "total_uses": p["total_uses"],
                            "last_used_timestamp": p["last_used_timestamp"],
                        }).eq("id", p["id"]).execute()
                        conn.table("stats").update({"xp": new_xp}).eq("id", stats_id).execute()

                        # Sprawdź status wyzwania Roulette
                        check_and_update_challenge(p["id"], uses_added=1)

                        st.session_state.db = load_cloud_data()
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

    # --- ANALYTICS / BEAUTY STATS ---
    elif st.session_state.current_page == "Analytics":
        st.markdown("### Beauty Stats & Lip Counter 🐈‍⬛")

        products = st.session_state.db.get("products", [])
        empties = st.session_state.db.get("empties", [])
        stats = st.session_state.db.get("stats", {})
        
        total_items = len(products)
        total_spent = sum(p.get("price", 0.0) for p in products)
        finished_lips = stats.get("finished_lip_products", 0)
        rewards_redeemed = stats.get("rewards_redeemed", 0)

        st.markdown(
            f"""
            <div class="vanity-card">
                <h4 style="margin:0 0 0.8rem 0; font-family:'Playfair Display', serif;">Lip Product Completion Milestone</h4>
                <p style="margin:0 0 0.5rem 0; font-size:1.05rem;">Finished Lip Products: <b>{finished_lips}</b> / 5 for next reward</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        brand_counts = {}
        for p in products:
            b_name = p.get("brand", "Unknown").strip().title()
            brand_counts[b_name] = brand_counts.get(b_name, 0) + 1
        
        sorted_brands = sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        top_brands_html = ""
        if not sorted_brands:
            top_brands_html = "<p style='margin:0; font-size:0.95rem; color:#8c7aa9;'>No brands recorded yet.</p>"
        else:
            for idx, (b_brand, b_count) in enumerate(sorted_brands, 1):
                top_brands_html += f"<p style='margin:0 0 0.3rem 0; font-size:0.95rem;'>{idx}. <b>{b_brand}</b> — {b_count} product{'s' if b_count > 1 else ''}</p>"

        st.markdown(
            f"""
            <div class="vanity-card">
                <h4 style="margin:0 0 0.8rem 0; font-family:'Playfair Display', serif;">Your Top 5 Brands</h4>
                {top_brands_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="vanity-card">
                <h4 style="margin:0 0 0.8rem 0; font-family:'Playfair Display', serif;">Collection Overview</h4>
                <p style="margin:0 0 0.4rem 0;">Total Active Items: <b>{total_items}</b></p>
                <p style="margin:0;">Total Estimated Value: <b>{total_spent:.2f}</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --- WISHLIST ---
    elif st.session_state.current_page == "Wishlist":
        st.markdown("### Wishlist ✨")
        st.markdown(
            "<p style='color:#8c7aa9; font-size:0.9rem;'>Track items you are considering before buying.</p>",
            unsafe_allow_html=True,
        )

        with st.form("add_wishlist_form"):
            w_brand = st.text_input("Brand")
            w_item = st.text_input("Item Name / Shade")
            w_price = st.number_input("Estimated Price", min_value=0.0, value=0.0)
            w_currency = st.selectbox(
                "Currency", ["GBP", "PLN", "EUR", "USD"], key="w_curr"
            )
            w_notes = st.text_area("Why do you want this? Any dupes you own?")

            if st.form_submit_button("Add to Wishlist"):
                if not w_brand:
                    st.error("Please enter a brand.")
                else:
                    new_w = {
                        "id": str(random.randint(100000, 999999)),
                        "brand": w_brand,
                        "item": w_item,
                        "price": float(w_price),
                        "currency": w_currency,
                        "notes": w_notes,
                    }
                    conn.table("wishlist").insert(new_w).execute()
                    st.success("Added to wishlist!")
                    st.session_state.db = load_cloud_data()
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        wishlist_items = st.session_state.db.get("wishlist", [])
        if not wishlist_items:
            st.info("Your wishlist is empty.")
        else:
            for w in wishlist_items:
                st.markdown(
                    f"""
                    <div class="vanity-card">
                        <h4 style="margin:0 0 0.3rem 0; font-family:'Playfair Display', serif;">{w['brand']} — {w['item']}</h4>
                        <p style="margin:0 0 0.4rem 0; font-size:0.9rem;"><strong>Price:</strong> {w['price']:.2f} {w['currency']}</p>
                        <p style="margin:0; font-size:0.85rem; color:#6b5b7a;">{w.get('notes', '')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Delete from Wishlist 🗑️", key=f"del_wish_{w['id']}"):
                    conn.table("wishlist").delete().eq("id", w["id"]).execute()
                    st.session_state.db = load_cloud_data()
                    st.rerun()
