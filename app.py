import streamlit as st

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Vanity Sanctuary",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# ---------------------------------------------------------
# Global Styles (Stylizujemy natywne st.button)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');

    .stApp {
        background-color: #d8cde9 !important;
        font-family: 'Lora', serif;
    }

    .main .block-container {
        max-width: 440px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

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

    /* Wymuszamy na przyciskach wygląd kwadratowych kafelków */
    div[data-testid="column"] button {
        background-color: #ffffff !important;
        border: 1px solid #e2d8ee !important;
        border-radius: 4px !important;
        height: 170px !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(100, 80, 130, 0.06) !important;
        white-space: pre-line !important;
        font-family: 'Playfair Display', serif !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: #554a60 !important;
        line-height: 1.2 !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }

    div[data-testid="column"] button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 18px rgba(100, 80, 130, 0.12) !important;
        border-color: #cbbba6 !important;
        background-color: #ffffff !important;
        color: #3a3342 !important;
    }

    .quote-card {
        background: #ffffff;
        border: 2px solid #3a3342 !important;
        border-radius: 2px;
        padding: 2.2rem 1.5rem;
        text-align: center;
        margin-top: 18px;
    }

    .quote-card p {
        font-family: 'Lora', serif;
        color: #5c5366;
        font-size: 1.35rem;
        margin: 0;
        line-height: 1.4;
    }
</style>
""", unsafe_allow_html=True)

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
# HOME PAGE (100% DZIAŁAJĄCE PRZYCISKI STREAMLIT)
# ---------------------------------------------------------
if st.session_state.current_page == "Home":

    # Rząd 1
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Your\nCollection\n\n🦇", key="btn_coll"):
            st.session_state.current_page = "Collection"
            st.rerun()

    with col2:
        if st.button("Project\nPan\n\n🌕", key="btn_pan"):
            st.session_state.current_page = "Project Pan"
            st.rerun()

    # Rząd 2
    col3, col4 = st.columns(2)
    with col3:
        if st.button("No - Buy\n& Rewards\n\n🌸", key="btn_nobuy"):
            st.session_state.current_page = "No-Buy Rules"
            st.rerun()

    with col4:
        if st.button("Beauty\nstats\n\n🐈‍⬛", key="btn_stats"):
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

    if st.session_state.current_page == "Collection":
        st.markdown("### Your Collection")

    elif st.session_state.current_page == "Project Pan":
        st.markdown("### Project Pan")

    elif st.session_state.current_page == "No-Buy Rules":
        st.markdown("### No - Buy & Rewards")

    elif st.session_state.current_page == "Analytics":
        st.markdown("### Beauty Stats")
