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

    .vanity-card {
        background: #ffffff;
        border-radius: 6px;
        border: 1px solid #e9e2f4;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 3px 10px rgba(130, 110, 160, 0.04);
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
# Supabase Cloud Connection
# ---------------------------------------------------------
conn = st.connection("supabase", type=SupabaseConnection)

TEXTS = {
    "PL": {
        "tagline": "Minimalistyczna kolekcja i projekt pan",
        "btn_coll": "Twoja\nKolekcja\n\n🦇",
        "btn_pan": "Project\nPan\n\n🌕",
        "btn_wish": "Wishlista\n\n✨",
        "btn_roulette": "Wyzwanie\nRuletka\n\n🎲",
        "btn_shop": "Sklep\nNagród\n\n🛍️",
        "btn_stats": "Statystyki i Analityka 🐈‍⬛",
        "back_menu": "← Powrót do Menu",
        "routine_title": "👑 30-Dniowe Wyzwanie Pełnej Rutyny",
        "routine_desc": "Wylosuj po 1 produkcie z każdej kategorii i używaj ich przez miesiąc!",
        "btn_gen_routine": "🎲 Wylosuj Pełną Rutynę (30 Dni)",
        "estimate_title": "🔮 Estymacja Zużycia i Daty Denka",
    },
    "EN": {
        "tagline": "Minimalist inventory & project pan",
        "btn_coll": "Your\nCollection\n\n🦇",
        "btn_pan": "Project\nPan\n\n🌕",
        "btn_wish": "Wishlist\n\n✨",
        "btn_roulette": "Roulette\nChallenge\n\n🎲",
        "btn_shop": "Reward\nShop\n\n🛍️",
        "btn_stats": "Beauty Stats & Analytics 🐈‍⬛",
        "back_menu": "← Back to Menu",
        "routine_title": "👑 30-Day Full Routine Challenge",
        "routine_desc": "Pick 1 product per category and commit to using them for a full month!",
        "btn_gen_routine": "🎲 Generate Full Routine (30 Days)",
        "estimate_title": "🔮 Pan Date Estimation",
    }
}


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


if "db" not in st.session_state:
    st.session_state.db = load_cloud_data()

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

t = TEXTS[st.session_state.lang]

# ---------------------------------------------------------
# Header & Language Selector
# ---------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h2:
    lang_choice = st.selectbox("🌐", ["EN", "PL"], index=0 if st.session_state.lang == "EN" else 1, key="lang_select")
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

st.markdown(
    f"""
<div class="sanctuary-header">
    <h1>Vanity Sanctuary</h1>
    <p>{t['tagline']}</p>
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# ROUTING
# ---------------------------------------------------------
if st.session_state.current_page == "Home":
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["btn_coll"], key="btn_coll", use_container_width=True):
            st.session_state.current_page = "Collection"
            st.rerun()
    with col2:
        if st.button(t["btn_pan"], key="btn_pan", use_container_width=True):
            st.session_state.current_page = "Project Pan"
            st.rerun()

    col3, col4 = st.columns(2)
    with col3:
        if st.button(t["btn_wish"], key="btn_wishlist", use_container_width=True):
            st.session_state.current_page = "Wishlist"
            st.rerun()
    with col4:
        if st.button(t["btn_roulette"], key="btn_roulette", use_container_width=True):
            st.session_state.current_page = "Roulette Challenge"
            st.rerun()

    col5, col6 = st.columns(2)
    with col5:
        if st.button(t["btn_shop"], key="btn_shop", use_container_width=True):
            st.session_state.current_page = "Reward Shop"
            st.rerun()
    with col6:
        if st.button(t["btn_stats"], key="btn_stats", use_container_width=True):
            st.session_state.current_page = "Analytics"
            st.rerun()

else:
    if st.button(t["back_menu"]):
        st.session_state.db = load_cloud_data()
        st.session_state.current_page = "Home"
        st.rerun()

    st.markdown("---")

    # --- ROULETTE CHALLENGE WITH MONTHLY ROUTINE ---
    if st.session_state.current_page == "Roulette Challenge":
        st.markdown(f"### {t['routine_title']}")
        st.write(t["routine_desc"])

        products = st.session_state.db.get("products", [])

        if st.button(t["btn_gen_routine"]):
            if not products:
                st.warning("Your collection is empty! Add products first.")
            else:
                # Pogrupuj po kategoriach i wylosuj po jednym
                categories = set(p.get("category", "Uncategorized") for p in products)
                routine = []
                for cat in categories:
                    cat_prods = [p for p in products if p.get("category") == cat]
                    routine.append(random.choice(cat_prods))

                # Zapisz wyzwanie do sesji / bazy
                st.session_state.monthly_routine = routine
                st.success("Selected Routine Challenge generated below!")

        if "monthly_routine" in st.session_state:
            st.markdown("#### Your 30-Day Project Pan Routine:")
            for item in st.session_state.monthly_routine:
                st.markdown(
                    f"""
                    <div class="vanity-card">
                        <b>{item.get('category', '').upper()}:</b> {item.get('brand')} - {item.get('shade')}
                        <br><small>Target: 30 days of consistent use</small>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # --- PROJECT PAN & AUTOMATIC ESTIMATIONS ---
    elif st.session_state.current_page == "Project Pan":
        st.markdown(f"### {t['estimate_title']}")
        products = st.session_state.db.get("products", [])

        if not products:
            st.info("No products found to estimate.")
        else:
            for p in products:
                prod_id = p.get("id")
                brand = p.get("brand", "Unknown")
                shade = p.get("shade", "")
                total_uses = p.get("total_uses", 0)
                daily_avg = float(p.get("daily_uses_avg", 1.0))
                remaining_uses_est = max(100 - total_uses, 1)  # Szacowane pozostałe użycia do denka

                st.markdown(
                    f"""
                    <div class="vanity-card">
                        <h4>{brand} — {shade}</h4>
                        <p>Total logged uses: <b>{total_uses}</b></p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Dzienny suwak, którego wartość ZAPISUJE SIĘ w bazie
                new_daily_avg = st.slider(
                    f"Daily usage rate for {brand}",
                    min_value=0.1,
                    max_value=5.0,
                    value=daily_avg,
                    step=0.1,
                    key=f"slider_{prod_id}",
                )

                if new_daily_avg != daily_avg:
                    # Aktualizacja w Supabase bez konieczności resetu
                    conn.table("products").update({"daily_uses_avg": new_daily_avg}).eq("id", prod_id).execute()
                    p["daily_uses_avg"] = new_daily_avg

                days_left = int(remaining_uses_est / new_daily_avg)
                est_date = datetime.date.today() + datetime.timedelta(days=days_left)

                st.info(f"⏳ Estimated Pan Date: **{est_date.strftime('%B %d, %Y')}** ({days_left} days left)")
                st.markdown("---")
