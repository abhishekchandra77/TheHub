import streamlit as st
import requests
import os

# --- Configuration & Environment ---
API_BASE = os.getenv("API_URL", "http://localhost:8000/api")

st.set_page_config(
    page_title="TheHub",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"


def apply_theme_css():
    theme = st.session_state.get("theme", "dark")
    if theme == "dark":
        bg = "#0b1020"
        bg_alt = "#111827"
        panel = "rgba(15, 23, 42, 0.82)"
        panel_soft = "rgba(15, 23, 42, 0.66)"
        text = "#e5eefb"
        text_soft = "#cbd5e1"
        line = "rgba(148, 163, 184, 0.2)"
        input_bg = "rgba(15,23,42,0.72)"
        button_bg = "rgba(15, 23, 42, 0.8)"
        accent_1 = "#8b5cf6"
        accent_2 = "#60a5fa"
    else:
        bg = "#f3f6fb"
        bg_alt = "#edf2ff"
        panel = "rgba(255, 255, 255, 0.9)"
        panel_soft = "rgba(255, 255, 255, 0.72)"
        text = "#111827"
        text_soft = "#475569"
        line = "rgba(148, 163, 184, 0.35)"
        input_bg = "rgba(255,255,255,0.82)"
        button_bg = "rgba(255,255,255,0.9)"
        accent_1 = "#7c3aed"
        accent_2 = "#2563eb"

    st.markdown(
        f"""
        <style>
            :root {{
                --app-bg: {bg};
                --app-bg-alt: {bg_alt};
                --app-panel: {panel};
                --app-panel-soft: {panel_soft};
                --app-text: {text};
                --app-text-soft: {text_soft};
                --app-line: {line};
                --app-input-bg: {input_bg};
                --app-button-bg: {button_bg};
            }}
            html, body, [data-testid="stAppViewContainer"] {{
                background: linear-gradient(180deg, var(--app-bg) 0%, var(--app-bg-alt) 100%);
                color: var(--app-text);
            }}
            .stApp {{ background: transparent; }}
            .block-container {{ max-width: 1380px; padding-top: 2rem; padding-bottom: 2rem; }}
            [data-testid="stHeader"] {{ background: rgba(15, 23, 42, 0.55); backdrop-filter: blur(8px); }}
            .brand-shell {{
                background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(14,165,233,0.10));
                border: 1px solid {line};
                border-radius: 22px;
                padding: 1.2rem 1.3rem;
                margin-bottom: 1rem;
                box-shadow: 0 20px 45px rgba(15, 23, 42, 0.12);
            }}
            .brand-badge {{
                display: inline-flex; align-items: center; gap: 0.5rem;
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 999px; padding: 0.45rem 0.8rem; font-size: 0.72rem; font-weight: 700;
                text-transform: uppercase; letter-spacing: 0.12em; color: #c4b5fd;
            }}
            .hero-title {{ margin-top: 0.55rem; margin-bottom: 0.2rem; font-size: clamp(2.1rem, 4vw, 3.5rem); font-weight: 900; letter-spacing: -0.06em; line-height: 1.02; color: {text}; }}
            .hero-subtitle {{ margin: 0; color: {text_soft}; font-size: 1.02rem; max-width: 760px; line-height: 1.6; }}
            .status-chip {{
                display: inline-flex; align-items: center; justify-content: center; width: 100%;
                padding: 0.72rem 0.9rem; border-radius: 16px; font-weight: 700;
                background: rgba(15, 118, 110, 0.12); border: 1px solid rgba(45, 212, 191, 0.25); color: #a7f3d0;
                box-shadow: 0 16px 30px rgba(16, 185, 129, 0.12);
            }}
            .status-chip.offline {{ background: rgba(127, 29, 29, 0.18); border-color: rgba(248, 113, 113, 0.18); color: #fecaca; }}
            .metric-card {{
                background: linear-gradient(180deg, {panel}, {panel_soft}); border: 1px solid {line}; border-radius: 18px; padding: 1rem 1.1rem; box-shadow: 0 18px 35px rgba(15, 23, 42, 0.12); min-height: 120px;
            }}
            [data-testid="stMetricValue"] {{ font-size: 1.65rem !important; font-weight: 800 !important; color: {text}; }}
            [data-testid="stMetricLabel"] {{ color: {text_soft} !important; font-weight: 600 !important; letter-spacing: 0.01em; }}
            .badge-video {{ background: linear-gradient(135deg, #8b5cf6, #7c3aed); color: #fff; padding: 0.38rem 0.8rem; border-radius: 9999px; font-size: 0.76rem; font-weight: 700; display: inline-block; letter-spacing: 0.01em; box-shadow: 0 12px 25px rgba(124, 58, 237, 0.26); }}
            .badge-design {{ background: linear-gradient(135deg, #ec4899, #f43f5e); color: white; padding: 0.38rem 0.8rem; border-radius: 9999px; font-size: 0.76rem; font-weight: 700; display: inline-block; letter-spacing: 0.01em; box-shadow: 0 12px 25px rgba(236, 72, 153, 0.20); }}
            .badge-writing {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 0.38rem 0.8rem; border-radius: 9999px; font-size: 0.76rem; font-weight: 700; display: inline-block; letter-spacing: 0.01em; box-shadow: 0 12px 25px rgba(16, 185, 129, 0.22); }}
            .badge-tech {{ background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; padding: 0.38rem 0.8rem; border-radius: 9999px; font-size: 0.76rem; font-weight: 700; display: inline-block; letter-spacing: 0.01em; box-shadow: 0 12px 25px rgba(59, 130, 246, 0.22); }}
            .rate-pill {{ font-size: 1.7rem; font-weight: 900; color: #34d399; letter-spacing: -0.05em; line-height: 1; }}
            .gig-card {{
                background: linear-gradient(180deg, {panel}, {panel_soft}); border: 1px solid {line}; border-radius: 22px; padding: 1.25rem; box-shadow: 0 18px 35px rgba(15,23,42,0.12); margin-bottom: 1rem;
            }}
            .feature-panel {{ background: linear-gradient(180deg, {panel}, {panel_soft}); border: 1px solid {line}; border-radius: 18px; padding: 1rem 1.1rem; margin-top: 0.5rem; box-shadow: 0 14px 32px rgba(15, 23, 42, 0.12); }}
            .mini-label {{ display: inline-block; margin-bottom: 0.5rem; color: #a5b4fc; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }}
            .stTabs [role="tablist"] {{ gap: 0.6rem; }}
            .stTabs [role="tab"] {{ border-radius: 12px 12px 0 0; background: rgba(15,23,42,0.2); border: 1px solid {line}; padding: 0.6rem 1rem; color: {text}; font-weight: 600; }}
            .stTabs [role="tab"][aria-selected="true"] {{ background: linear-gradient(135deg, rgba(139,92,246,0.20), rgba(59,130,246,0.20)); border-color: rgba(165,180,252,0.3); color: {text}; }}
            .stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div, .stTextArea > div > div > textarea {{ background: {input_bg}; border: 1px solid {line}; color: {text}; border-radius: 12px; }}
            .stTextInput label, .stNumberInput label, .stSelectbox label, .stTextArea label {{ color: {text} !important; font-weight: 600 !important; }}
            .stPopover > button {{ background: {button_bg} !important; border: 1px solid {line} !important; color: {text} !important; border-radius: 12px !important; }}
            .stButton > button {{ background: linear-gradient(135deg, {accent_1}, {accent_2}) !important; color: white !important; border: none !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_theme_toggle():
    theme = st.session_state.get("theme", "dark")
    selected = st.radio("Theme", ["Dark", "Light"], index=0 if theme == "dark" else 1, horizontal=True, key=f"theme_choice_{hash(str(st.session_state.get('user_email','guest')))}")
    st.session_state["theme"] = "dark" if selected == "Dark" else "light"


# --- Custom Styling (Premium Creator Marketplace Theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Inter', sans-serif;
        background: var(--app-bg, #0b1020);
        color: var(--app-text, #e5eefb);
    }

    .stApp {
        background: transparent;
    }

    .block-container {
        max-width: 1380px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stHeader"] {
        background: rgba(15, 23, 42, 0.6);
        backdrop-filter: blur(8px);
    }

    .brand-shell {
        background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(14,165,233,0.10));
        border: 1px solid rgba(148,163,184,0.18);
        border-radius: 22px;
        padding: 1.2rem 1.3rem;
        margin-bottom: 1rem;
        box-shadow: 0 20px 45px rgba(15, 23, 42, 0.22);
    }

    .brand-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 999px;
        padding: 0.45rem 0.8rem;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #c4b5fd;
    }

    .hero-title {
        margin-top: 0.55rem;
        margin-bottom: 0.2rem;
        font-size: clamp(2.1rem, 4vw, 3.5rem);
        font-weight: 900;
        letter-spacing: -0.06em;
        line-height: 1.02;
        color: var(--app-text, #f8fbff);
    }

    .hero-subtitle {
        margin: 0;
        color: var(--app-text-soft, #cbd5e1);
        font-size: 1.02rem;
        max-width: 760px;
        line-height: 1.6;
    }

    .status-chip {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 0.72rem 0.9rem;
        border-radius: 16px;
        font-weight: 700;
        background: rgba(15, 118, 110, 0.12);
        border: 1px solid rgba(45, 212, 191, 0.25);
        color: #a7f3d0;
        box-shadow: 0 16px 30px rgba(16, 185, 129, 0.12);
    }

    .status-chip.offline {
        background: rgba(127, 29, 29, 0.18);
        border-color: rgba(248, 113, 113, 0.18);
        color: #fecaca;
    }

    .metric-card {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.82), rgba(15, 23, 42, 0.62));
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 18px 35px rgba(15, 23, 42, 0.18);
        min-height: 120px;
    }

    .metric-card .stMetric {
        background: transparent;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.65rem !important;
        font-weight: 800 !important;
        color: #f8fafc;
    }

    [data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em;
    }

    .badge-video {
        background: linear-gradient(135deg, #8b5cf6, #7c3aed);
        color: #fff;
        padding: 0.38rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        display: inline-block;
        letter-spacing: 0.01em;
        box-shadow: 0 12px 25px rgba(124, 58, 237, 0.26);
    }

    .badge-design {
        background: linear-gradient(135deg, #ec4899, #f43f5e);
        color: white;
        padding: 0.38rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        display: inline-block;
        letter-spacing: 0.01em;
        box-shadow: 0 12px 25px rgba(236, 72, 153, 0.20);
    }

    .badge-writing {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 0.38rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        display: inline-block;
        letter-spacing: 0.01em;
        box-shadow: 0 12px 25px rgba(16, 185, 129, 0.22);
    }

    .badge-tech {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        padding: 0.38rem 0.8rem;
        border-radius: 9999px;
        font-size: 0.76rem;
        font-weight: 700;
        display: inline-block;
        letter-spacing: 0.01em;
        box-shadow: 0 12px 25px rgba(59, 130, 246, 0.22);
    }

    .rate-pill {
        font-size: 1.7rem;
        font-weight: 900;
        color: #34d399;
        letter-spacing: -0.05em;
        line-height: 1;
    }

    .gig-card {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.82), rgba(15, 23, 42, 0.66));
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 22px;
        padding: 1.25rem;
        box-shadow: 0 18px 35px rgba(15,23,42,0.22);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .gig-card:hover {
        transform: translateY(-2px);
        border-color: rgba(96, 165, 250, 0.5);
    }

    .premium-button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.01em !important;
        background: linear-gradient(135deg, #8b5cf6, #4f46e5) !important;
        border: none !important;
        color: #fff !important;
        box-shadow: 0 16px 30px rgba(79, 70, 229, 0.28) !important;
    }

    .secondary-button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        background: rgba(148, 163, 184, 0.10) !important;
        border: 1px solid rgba(148, 163, 184, 0.15) !important;
        color: #e2e8f0 !important;
    }

    .stButton > button:hover {
        filter: brightness(1.02);
    }

    .theme-toggle {
        padding: 0.35rem 0.6rem;
        border-radius: 999px;
        background: rgba(15, 23, 42, 0.18);
        border: 1px solid rgba(148, 163, 184, 0.18);
        margin-bottom: 1rem;
    }

    .login-shell {
        background: linear-gradient(135deg, rgba(124,58,237,0.10), rgba(14,165,233,0.08));
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 28px;
        padding: 1.6rem;
        box-shadow: 0 28px 60px rgba(15, 23, 42, 0.18);
    }

    .login-card {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.82), rgba(15, 23, 42, 0.68));
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 22px;
        padding: 1.4rem;
    }

    .glass-box {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.72), rgba(15, 23, 42, 0.58));
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 20px;
        padding: 1.1rem;
    }

    .page-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .page-chip {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.45rem 0.8rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(148,163,184,0.18);
        font-size: 0.75rem;
        font-weight: 700;
        color: var(--app-text, #f8fafc);
    }

    .stTabs [role="tablist"] {
        gap: 0.6rem;
    }

    .stTabs [role="tab"] {
        border-radius: 12px 12px 0 0;
        background: rgba(15,23,42,0.55);
        border: 1px solid rgba(148,163,184,0.12);
        padding: 0.6rem 1rem;
        color: #dfe7f5;
        font-weight: 600;
    }

    .stTabs [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(139,92,246,0.20), rgba(59,130,246,0.20));
        border-color: rgba(165,180,252,0.3);
        color: #fff;
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea {
        background: rgba(15,23,42,0.72);
        border: 1px solid rgba(148,163,184,0.2);
        color: #f1f5f9;
        border-radius: 12px;
    }

    .stTextInput label, .stNumberInput label, .stSelectbox label, .stTextArea label {
        color: var(--app-text, #dfe7f5) !important;
        font-weight: 600 !important;
    }

    .stPopover > button {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(148,163,184,0.2) !important;
        color: #f8fafc !important;
        border-radius: 12px !important;
    }

    .feature-panel {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.66));
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        margin-top: 0.5rem;
        box-shadow: 0 14px 32px rgba(15, 23, 42, 0.18);
    }

    .mini-label {
        display: inline-block;
        margin-bottom: 0.5rem;
        color: #a5b4fc;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    div[data-testid="stContainer"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: transparent;
    }
</style>
""", unsafe_allow_html=True)

# Helper function for badges
def get_category_badge(category: str) -> str:
    cat_lower = category.lower()
    if "video" in cat_lower or "ugc" in cat_lower:
        return f'<span class="badge-video">📹 {category}</span>'
    elif "design" in cat_lower or "graphics" in cat_lower:
        return f'<span class="badge-design">🎨 {category}</span>'
    elif "writing" in cat_lower or "translation" in cat_lower:
        return f'<span class="badge-writing">✍️ {category}</span>'
    else:
        return f'<span class="badge-tech">⚡ {category}</span>'


def clear_session():
    for key in ["logged_in", "user_role", "user_name", "user_email"]:
        st.session_state.pop(key, None)


def render_login():
    render_theme_toggle()
    left_col, right_col = st.columns([1.2, 1.0], gap="large")

    with left_col:
        st.markdown(
            """
            <div class="login-shell">
                <div class="brand-badge">✨ Smart marketplace</div>
                <div class="hero-title" style="margin-top: 1rem;">Welcome to TheHub</div>
                <p class="hero-subtitle">Your workspace for discovering talent, managing bookings, and scaling creative projects with clarity.</p>
                <div style="margin-top: 1.5rem; display: flex; gap: 0.75rem; flex-wrap: wrap;">
                    <span class="page-chip">🎨 Creators</span>
                    <span class="page-chip">💼 Clients</span>
                    <span class="page-chip">⚡ Fast booking</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.subheader("Sign in")
        st.caption("Choose your role and continue to your workspace")

        demo_accounts = {
            "creator@thehub.com": {"password": "creator123", "role": "creator", "name": "Alex Rivera"},
            "client@thehub.com": {"password": "client123", "role": "client", "name": "Ava Johnson"},
        }

        selected_role = st.radio("I am signing in as a", ["Creator", "Client"], horizontal=True)
        email = st.text_input("Email address", placeholder="creator@thehub.com")
        password = st.text_input("Password", type="password", placeholder="Enter password")

        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("Login", type="primary", use_container_width=True):
                account = demo_accounts.get(email.strip().lower())
                if account and account["password"] == password and account["role"] == selected_role.lower():
                    st.session_state["logged_in"] = True
                    st.session_state["user_role"] = account["role"]
                    st.session_state["user_name"] = account["name"]
                    st.session_state["user_email"] = email.strip().lower()
                    st.rerun()
                else:
                    st.error("Invalid email, password, or role selection.")

        with c2:
            if st.button("Demo Creator", use_container_width=True):
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "creator"
                st.session_state["user_name"] = "Alex Rivera"
                st.session_state["user_email"] = "creator@thehub.com"
                st.rerun()

        with c3:
            if st.button("Demo Client", use_container_width=True):
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "client"
                st.session_state["user_name"] = "Ava Johnson"
                st.session_state["user_email"] = "client@thehub.com"
                st.rerun()

        st.markdown("<div class='glass-box' style='margin-top: 1.2rem;'>", unsafe_allow_html=True)
        st.write("Demo credentials")
        st.code("Creator: creator@thehub.com / creator123\nClient: client@thehub.com / client123")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_client_app():
    st.markdown("<div class='page-topbar'>", unsafe_allow_html=True)
    left, right = st.columns([2, 1])
    with left:
        st.markdown("<span class='page-chip'>💼 Client portal</span>", unsafe_allow_html=True)
    with right:
        render_theme_toggle()
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Logout"):
        clear_session()
        st.rerun()

    st.markdown(
        """
        <div class="brand-shell">
            <div class="brand-badge">💼 Client portal</div>
            <div class="hero-title">Find the right creator for your next project</div>
            <p class="hero-subtitle">Browse vetted creators, compare offers, and track each project from a dedicated client workspace.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    client_tabs = st.tabs(["Browse Gigs", "My Bookings", "Saved Shortlist"])

    with client_tabs[0]:
        st.header("Marketplace")
        filter_col1, filter_col2, filter_col3 = st.columns([1.5, 2, 1.5])
        with filter_col1:
            category_choice = st.selectbox("Filter Category", ["All", "Video & UGC", "Design & Graphics", "Writing & Translation", "Tech & AI"])
        with filter_col2:
            search_term = st.text_input("Search services or creators", placeholder="e.g. TikTok, thumbnails, AI automation")
        with filter_col3:
            sort_choice = st.selectbox("Sort by", ["Newest First", "Price: Low to High", "Price: High to Low"])

        sort_param = "newest"
        if sort_choice == "Price: Low to High":
            sort_param = "cheapest"
        elif sort_choice == "Price: High to Low":
            sort_param = "priciest"

        try:
            params = {"sort_by": sort_param}
            if category_choice != "All":
                params["category"] = category_choice
            if search_term.strip():
                params["search"] = search_term.strip()
            resp = requests.get(f"{API_BASE}/gigs", params=params, timeout=5)
            if resp.status_code == 200:
                gigs = resp.json()
                if not gigs:
                    st.info("No gigs match your current filters.")
                else:
                    for gig in gigs:
                        st.markdown("<div class='gig-card'>", unsafe_allow_html=True)
                        left_col, right_col = st.columns([3.2, 1.2])
                        with left_col:
                            st.markdown(get_category_badge(gig["category"]), unsafe_allow_html=True)
                            st.subheader(gig["title"])
                            st.caption(f"Creator: **{gig['creator_name']}** | **{gig['category']}**")
                            st.write(gig["description"])
                        with right_col:
                            st.markdown(f"<div class='rate-pill'>${gig['rate']:.2f}</div>", unsafe_allow_html=True)
                            st.caption("Fast turnaround")
                            with st.popover("Book this gig", use_container_width=True):
                                st.write(f"Project for: **{gig['title']}**")
                                client_name = st.text_input("Your name", key=f"client_name_{gig['id']}")
                                client_email = st.text_input("Email", key=f"client_email_{gig['id']}")
                                brief = st.text_area("Project requirements", key=f"client_brief_{gig['id']}")
                                if st.button("Submit booking", key=f"booking_{gig['id']}", type="primary", use_container_width=True):
                                    if not client_name.strip() or not client_email.strip() or not brief.strip():
                                        st.error("Please complete the booking details.")
                                    else:
                                        payload = {
                                            "gig_id": gig["id"],
                                            "client_name": client_name.strip(),
                                            "client_email": client_email.strip(),
                                            "requirements": brief.strip(),
                                        }
                                        res = requests.post(f"{API_BASE}/bookings", json=payload, timeout=5)
                                        if res.status_code in [200, 201]:
                                            st.success("Booking sent successfully.")
                                            st.session_state["active_client"] = client_name.strip()
                                        else:
                                            st.error(f"Booking failed: {res.text}")
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("Unable to load marketplace.")
        except Exception as e:
            st.error(f"Connection error: {str(e)}")

    with client_tabs[1]:
        st.header("My Bookings")
        client_name_query = st.text_input("Filter by your name", value=st.session_state.get("active_client", ""))
        try:
            params = {}
            if client_name_query.strip():
                params["client_name"] = client_name_query.strip()
            res = requests.get(f"{API_BASE}/client/bookings", params=params, timeout=5)
            if res.status_code == 200:
                bookings = res.json()
                if not bookings:
                    st.info("No bookings yet. Browse the marketplace to begin.")
                else:
                    for booking in bookings:
                        st.markdown("<div class='gig-card'>", unsafe_allow_html=True)
                        st.subheader(booking["gig_title"])
                        st.write(f"Creator: **{booking['creator_name']}** | Category: **{booking['category']}** | Rate: **${booking['rate']:.2f}**")
                        st.write(f"Requirements: {booking['requirements']}")
                        if booking["status"] == "Accepted":
                            st.success("Accepted")
                        elif booking["status"] == "Declined":
                            st.error("Declined")
                            if booking.get("rejection_reason"):
                                st.info(f"Reason: {booking['rejection_reason']}")
                        else:
                            st.warning("Pending review")
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("Could not load bookings.")
        except Exception as e:
            st.error(f"Connection error: {str(e)}")

    with client_tabs[2]:
        st.header("Saved Shortlist")
        st.info("This space can hold favorite creators or preferred categories for faster booking later.")
        st.markdown(
            """
            - TikTok / UGC creators
            - AI automation specialists
            - YouTube thumbnail designers
            - Newsletter & copywriting experts
            """
        )


apply_theme_css()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state.get("logged_in", False):
    render_login()
    st.stop()

if st.session_state.get("user_role") != "creator":
    render_client_app()
    st.stop()

apply_theme_css()

# --- Header & Live Stats Bar ---
st.markdown("<div class='page-topbar'>", unsafe_allow_html=True)
head_left, head_right = st.columns([2, 1])
with head_left:
    st.markdown("<span class='page-chip'>🚀 Creator marketplace</span>", unsafe_allow_html=True)
with head_right:
    render_theme_toggle()
st.markdown("</div>", unsafe_allow_html=True)

col_title, col_status = st.columns([3.2, 1.0], gap="medium")
with col_title:
    st.markdown(
        """
        <div class="brand-shell">
            <div class="brand-badge">🚀 Creator marketplace</div>
            <div class="hero-title">TheHub</div>
            <p class="hero-subtitle">Find the right creator for video, design, writing, and AI work — all in one polished marketplace built for modern digital brands and young talent.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Fetch Live Stats from Backend
stats = {"total_gigs": 0, "pending_bookings": 0, "accepted_bookings": 0, "total_volume": 0}
backend_online = True
try:
    s_res = requests.get(f"{API_BASE}/stats", timeout=3)
    if s_res.status_code == 200:
        stats = s_res.json()
    else:
        backend_online = False
except Exception:
    backend_online = False

with col_status:
    if backend_online:
        st.markdown('<div class="status-chip">🟢 Backend Connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-chip offline">🔴 Backend Offline</div>', unsafe_allow_html=True)
    st.markdown("<div style='height: 0.9rem;'></div>", unsafe_allow_html=True)
    st.caption("Code2Career AI Hackathon 2026")
    st.caption("Elevating creator careers")

# Live Stats Metrics Bar
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(label="🎯 Active Gigs", value=stats.get("total_gigs", 0))
    st.markdown('</div>', unsafe_allow_html=True)
with m2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(label="⏳ Pending Requests", value=stats.get("pending_bookings", 0))
    st.markdown('</div>', unsafe_allow_html=True)
with m3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(label="🤝 Accepted Deals", value=stats.get("accepted_bookings", 0))
    st.markdown('</div>', unsafe_allow_html=True)
with m4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(label="💰 Platform Volume", value=f"${stats.get('total_volume', 0):,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# --- Main Navigation Tabs ---
tabs = st.tabs([
    "🛒 Marketplace (Browse & Book)",
    "➕ Post a Gig",
    "📊 Creator Dashboard",
    "📋 My Bookings",
    "💡 Decision Points (DP1-DP3)"
])

# ==============================================================================
# TAB 1: BROWSE & BOOK (Features 2 & 3 + DP3 Sorting)
# ==============================================================================
with tabs[0]:
    st.header("Browse Creator Gigs")
    st.write("Discover verified services from top young talent or book tailored creative work.")

    filter_col1, filter_col2, filter_col3 = st.columns([1.5, 2, 1.5])
    with filter_col1:
        category_choice = st.selectbox(
            "Filter Category",
            ["All", "Video & UGC", "Design & Graphics", "Writing & Translation", "Tech & AI"],
            key="market_cat"
        )
    with filter_col2:
        search_term = st.text_input(
            "Search Services or Creators",
            placeholder="e.g. TikTok, AI Workflow, YouTube Thumbnail...",
            key="market_search"
        )
    with filter_col3:
        # DP3 Sorting Dropdown
        sort_choice = st.selectbox(
            "Rank By (DP3 Discovery)",
            ["Newest First", "Price: Low to High", "Price: High to Low"],
            key="market_sort"
        )

    # Map UI sort string to API query param
    sort_param = "newest"
    if sort_choice == "Price: Low to High":
        sort_param = "cheapest"
    elif sort_choice == "Price: High to Low":
        sort_param = "priciest"

    try:
        query_params = {"sort_by": sort_param}
        if category_choice != "All":
            query_params["category"] = category_choice
        if search_term.strip():
            query_params["search"] = search_term.strip()

        resp = requests.get(f"{API_BASE}/gigs", params=query_params, timeout=5)
        if resp.status_code == 200:
            gigs = resp.json()
            if not gigs:
                st.info("🔍 No gigs found matching your criteria. Try adjusting your filters or post the first one!")
            else:
                st.caption(f"Showing **{len(gigs)}** creator service(s)")
                
                # Render gigs in cards
                for gig in gigs:
                    st.markdown("<div class='gig-card'>", unsafe_allow_html=True)
                    card_left, card_right = st.columns([3.2, 1.2])
                    with card_left:
                        st.markdown(get_category_badge(gig['category']), unsafe_allow_html=True)
                        st.subheader(gig['title'])
                        st.caption(f"👤 Creator: **{gig['creator_name']}** • Category: **{gig['category']}**")
                        st.write(gig['description'])
                    
                    with card_right:
                        st.markdown(f"<div class='rate-pill'>${gig['rate']:.2f}</div>", unsafe_allow_html=True)
                        st.caption("Standard Delivery")
                        
                        # Feature 3: Book a Gig with Popover
                        with st.popover("⚡ Book Now", use_container_width=True):
                            st.write(f"Book: **{gig['title']}**")
                            st.caption(f"Creator: {gig['creator_name']} | Rate: ${gig['rate']:.2f}")
                            
                            prefill_name = st.session_state.get("prefill_client_name", "")
                            prefill_email = st.session_state.get("prefill_client_email", "")
                            prefill_req = st.session_state.get("prefill_reqs", "")

                            b_client_name = st.text_input("Your Full Name", value=prefill_name, key=f"cn_{gig['id']}")
                            b_client_email = st.text_input("Your Email Address", value=prefill_email, key=f"ce_{gig['id']}")
                            b_requirements = st.text_area(
                                "Project Brief & Requirements",
                                value=prefill_req,
                                placeholder="Describe your goals, deliverables, deadline...",
                                key=f"req_{gig['id']}"
                            )

                            if st.button("🚀 Confirm Booking", key=f"confirm_btn_{gig['id']}", type="primary", use_container_width=True):
                                if not b_client_name or not b_client_email or not b_requirements:
                                    st.error("Please fill in all booking fields.")
                                else:
                                    book_payload = {
                                        "gig_id": gig['id'],
                                        "client_name": b_client_name,
                                        "client_email": b_client_email,
                                        "requirements": b_requirements
                                    }
                                    book_res = requests.post(f"{API_BASE}/bookings", json=book_payload, timeout=5)
                                    if book_res.status_code in [200, 201]:
                                        st.balloons()
                                        st.success(f"🎉 Booking request #{book_res.json().get('id')} submitted to {gig['creator_name']}!")
                                        st.info("You can track this under the '📋 My Bookings' tab.")
                                        st.session_state["active_client"] = b_client_name
                                    elif book_res.status_code == 404:
                                        st.error("Gig validation failed: Gig does not exist.")
                                    else:
                                        st.error(f"Error submitting booking: {book_res.text}")
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error(f"Failed to fetch gigs from server (HTTP {resp.status_code}).")
    except Exception as e:
        st.error(f"Unable to connect to Marketplace API: {str(e)}")

# ==============================================================================
# TAB 2: POST A GIG (Feature 1)
# ==============================================================================
with tabs[1]:
    st.header("List Your Creator Skill")
    st.write("Fill out the listing form below to publish your gig on the live marketplace.")

    post_col, preview_col = st.columns([1.8, 1.2])

    with post_col:
        with st.form("new_gig_form", clear_on_submit=True):
            f_creator = st.text_input("Creator / Handle Name", placeholder="e.g. Maya Chen, DevStudio")
            f_title = st.text_input("Gig Title", placeholder="e.g. 4K TikTok UGC Video Ads")
            f_cat = st.selectbox("Category", ["Video & UGC", "Design & Graphics", "Writing & Translation", "Tech & AI"])
            f_rate = st.number_input("Rate in USD ($)", min_value=1.0, value=75.0, step=5.0)
            f_desc = st.text_area(
                "Detailed Description & Deliverables",
                placeholder="List what you will provide, your turnaround time, and requirements from the client..."
            )

            submit_gig = st.form_submit_button("✨ Publish Gig to Marketplace", type="primary", use_container_width=True)
            if submit_gig:
                if not f_creator.strip() or not f_title.strip() or not f_desc.strip():
                    st.error("⚠️ All fields are required to publish your gig.")
                else:
                    payload = {
                        "creator_name": f_creator.strip(),
                        "title": f_title.strip(),
                        "category": f_cat,
                        "rate": float(f_rate),
                        "description": f_desc.strip()
                    }
                    try:
                        g_res = requests.post(f"{API_BASE}/gigs", json=payload, timeout=5)
                        if g_res.status_code in [200, 201]:
                            st.balloons()
                            st.success(f"🎉 Awesome! Your gig '{f_title}' is now live on the marketplace.")
                        else:
                            st.error(f"Failed to publish gig: {g_res.text}")
                    except Exception as err:
                        st.error(f"Connection error: {str(err)}")

    with preview_col:
        st.markdown('<div class="mini-label">Live preview</div>', unsafe_allow_html=True)
        st.markdown("<div class='gig-card'>", unsafe_allow_html=True)
        st.markdown(get_category_badge(f_cat if 'f_cat' in locals() else "Video & UGC"), unsafe_allow_html=True)
        st.write(f"### {f_title if 'f_title' in locals() and f_title.strip() else 'Sample Gig Title'}")
        st.caption(f"By {f_creator if 'f_creator' in locals() and f_creator.strip() else 'Your Name'}")
        st.write(f_desc if 'f_desc' in locals() and f_desc.strip() else "Your full gig description and scope will appear here for clients.")
        st.markdown(f"<div class='rate-pill'>${f_rate if 'f_rate' in locals() else 75:.2f}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================================================================
# TAB 3: CREATOR DASHBOARD (Feature 4 & DP2)
# ==============================================================================
with tabs[2]:
    st.header("Creator Booking Inquiries")
    st.write("Manage client project requests. Accept inquiries or decline with constructive feedback.")

    try:
        c_res = requests.get(f"{API_BASE}/creator/bookings", timeout=5)
        if c_res.status_code == 200:
            c_bookings = c_res.json()
            if not c_bookings:
                st.info("Inbox clean! No booking requests yet.")
            else:
                # Filter dashboard by status
                dash_filter = st.radio(
                    "Filter Inquiries:",
                    ["All Inquiries", "Pending", "Accepted", "Declined"],
                    horizontal=True
                )

                filtered_bookings = [
                    b for b in c_bookings
                    if dash_filter == "All Inquiries" or b["status"] == dash_filter
                ]

                st.caption(f"Showing **{len(filtered_bookings)}** inquiry item(s)")

                for b in filtered_bookings:
                    st.markdown("<div class='gig-card'>", unsafe_allow_html=True)
                    b_col1, b_col2 = st.columns([3, 1.2])
                    with b_col1:
                        st.subheader(f"{b['gig_title']}")
                        st.markdown(
                            f"**Client:** `{b['client_name']}` (<a href='mailto:{b['client_email']}'>{b['client_email']}</a>) • **Rate:** `${b['rate']}`",
                            unsafe_allow_html=True
                        )
                        st.write(f"**Brief / Scope:** {b['requirements']}")
                    
                    with b_col2:
                        status = b["status"]
                        if status == "Pending":
                            st.warning("⏳ Status: Pending Review")
                            
                            if st.button("✅ Accept", key=f"dash_acc_{b['id']}", type="primary", use_container_width=True):
                                patch_res = requests.patch(f"{API_BASE}/bookings/{b['id']}", json={"status": "Accepted"}, timeout=5)
                                if patch_res.status_code == 200:
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error("Failed to accept booking.")
                            
                            with st.popover("❌ Decline", use_container_width=True):
                                st.write(f"Decline booking from **{b['client_name']}**")
                                reason_input = st.text_input(
                                    "Rejection Reason (Optional)",
                                    placeholder="e.g. Schedule fully booked, outside my scope...",
                                    key=f"reason_{b['id']}"
                                )
                                if st.button("Confirm Decline", key=f"confirm_dec_{b['id']}", use_container_width=True):
                                    patch_res = requests.patch(
                                        f"{API_BASE}/bookings/{b['id']}",
                                        json={"status": "Declined", "rejection_reason": reason_input.strip()},
                                        timeout=5
                                    )
                                    if patch_res.status_code == 200:
                                        st.rerun()
                                    else:
                                        st.error("Failed to decline booking.")
                        elif status == "Accepted":
                            st.success("✅ Status: Accepted", icon="🎉")
                            st.caption("Confirmed project. Proceed with deliverables.")
                        else:
                            st.error("❌ Status: Declined", icon="⛔")
                            if b.get("rejection_reason"):
                                st.caption(f"Reason: *{b['rejection_reason']}*")
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Unable to load creator inquiries.")
    except Exception as e:
        st.error(f"Error connecting to dashboard: {str(e)}")

# ==============================================================================
# TAB 4: MY BOOKINGS (Feature 5 & DP1 Re-booking)
# ==============================================================================
with tabs[3]:
    st.header("Client Order Tracker")
    st.write("Track the progress of your booked services across all creators in real time.")

    default_client = st.session_state.get("active_client", "")
    client_name_query = st.text_input(
        "Enter Your Client Name to Filter",
        value=default_client,
        placeholder="e.g. Alex, Sarah, or leave blank to see all"
    )

    try:
        c_params = {}
        if client_name_query.strip():
            c_params["client_name"] = client_name_query.strip()

        cb_res = requests.get(f"{API_BASE}/client/bookings", params=c_params, timeout=5)
        if cb_res.status_code == 200:
            client_bookings = cb_res.json()
            if not client_bookings:
                st.info("No bookings found. Head to the Marketplace tab to book your first creator!")
            else:
                for mb in client_bookings:
                    st.markdown("<div class='gig-card'>", unsafe_allow_html=True)
                    col_l, col_r = st.columns([3, 1.2])
                    with col_l:
                        st.subheader(mb['gig_title'])
                        st.write(f"**Creator:** {mb['creator_name']} | **Category:** {mb['category']} | **Rate:** ${mb['rate']:.2f}")
                        st.write(f"**Your Brief:** {mb['requirements']}")
                    
                    with col_r:
                        b_stat = mb['status']
                        if b_stat == "Accepted":
                            st.success("🎉 Accepted & Active")
                            st.caption("The creator accepted your project! Check your inbox for updates.")
                        elif b_stat == "Declined":
                            st.error("❌ Booking Declined")
                            if mb.get('rejection_reason'):
                                st.info(f"💬 **Feedback from Creator:**\n\n\"{mb['rejection_reason']}\"")
                            else:
                                st.caption("No specific reason provided.")
                            
                            st.markdown("---")
                            st.caption("💡 **Actionable Recovery:**")
                            if st.button("🔄 1-Click Re-book Alternative", key=f"rebook_{mb['id']}", use_container_width=True):
                                st.session_state["prefill_client_name"] = mb["client_name"]
                                st.session_state["prefill_client_email"] = mb["client_email"]
                                st.session_state["prefill_reqs"] = mb["requirements"]
                                st.toast("Re-book details copied! Select an alternative creator in the Marketplace tab.", icon="🚀")
                        else:
                            st.warning("⏳ Pending Creator Review")
                            st.caption("Waiting for creator response. You will receive notification soon.")
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Failed to retrieve your bookings.")
    except Exception as e:
        st.error(f"Error connecting to bookings service: {str(e)}")

# ==============================================================================
# TAB 5: DECISION POINTS (DP1, DP2, DP3)
# ==============================================================================
with tabs[4]:
    st.header("Architecture & Decision Points Rationale")
    st.caption("Detailed breakdown for Hackathon Judges and Graders (20 Points Criteria)")

    with st.expander("📌 DP1 · Rejection: Feedback & Actionable Re-booking (Graded Criteria)", expanded=True):
        st.markdown("""
        **What the client sees and can do:**
        - The client sees the status explicitly updated to **Declined** along with a transparent rejection reason provided by the creator (e.g. schedule conflict or out-of-scope).
        - An actionable **"🔄 1-Click Re-book Alternative"** feature immediately copies their previous brief and contacts so they can book an alternate creator in the same category without re-typing.
        
        **Why:**
        - Displaying clear creator feedback eliminates guesswork and user frustration.
        - Rather than bouncing from the marketplace upon rejection, providing a one-click alternative recovery keeps clients engaged and preserves marketplace liquidity.
        """)

    with st.expander("📌 DP2 · Double Booking: Concurrent Inquiries Allowed", expanded=True):
        st.markdown("""
        **Choice:** **Yes**, new booking requests remain open for a gig even while another request is in **Pending** status.
        
        **Why:**
        - Creators operate on flexible bandwidth and can take multiple concurrent orders or select the best fit.
        - Freezing a gig listing while an inquiry is pending causes catastrophic drop-off if the inquiry is eventually declined or abandoned.
        - Allowing concurrent requests guarantees creators maintain an active pipeline.
        """)

    with st.expander("📌 DP3 · Discovery: Multi-Strategy Dynamic Ranking", expanded=True):
        st.markdown("""
        **Choice:** **Hybrid Recency + On-Demand Multi-Sort** (Newest First, Price: Low-to-High, Price: High-to-Low).
        
        **Why:**
        - Defaulting to **Newest First** gives newly registered young creators immediate algorithmic exposure on the platform without requiring existing reviews.
        - Providing instant one-click switching to **Cheapest** or **Priciest** empowers budget-conscious clients and enterprise buyers to discover the exact tier of creator they need.
        """)