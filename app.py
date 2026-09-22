import os
from html import escape
from typing import Any, Optional

import requests
import streamlit as st


API_BASE = os.getenv("API_URL", "http://localhost:8000/api")
PAGE_SIZE = 12
CATEGORIES = ["All", "Video & UGC", "Design & Graphics", "Writing & Translation", "Tech & AI"]
CATEGORY_CARDS = [
    ("Video & UGC", "V", "Scroll-stopping stories, product films, and social ads.", "violet"),
    ("Design & Graphics", "D", "Identity systems, thumbnails, and visual direction.", "coral"),
    ("Writing & Translation", "W", "Words that clarify ideas and make brands memorable.", "mint"),
    ("Programming & Tech", "<>", "Products, websites, and technical solutions that ship.", "blue"),
    ("Marketing", "M", "Campaigns that turn attention into meaningful growth.", "gold"),
    ("AI & Automation", "AI", "Practical systems that make repetitive work disappear.", "violet"),
    ("Music & Audio", "A", "Distinctive sound design, podcasts, and original music.", "coral"),
    ("Photography", "P", "Thoughtful images for products, people, and places.", "mint"),
]
CATEGORY_API_MAP = {"Programming & Tech": "Tech & AI", "AI & Automation": "Tech & AI"}

st.set_page_config(page_title="TheHub | Creator marketplace", page_icon="T", layout="wide", initial_sidebar_state="collapsed")

for key, value in {
    "theme": "light",
    "logged_in": False,
    "page": "home",
    "user_role": "",
    "user_name": "",
    "user_email": "",
    "active_client": "",
    "selected_gig": None,
}.items():
    st.session_state.setdefault(key, value)


def api_request(method: str, path: str, **kwargs: Any) -> tuple[Optional[Any], Optional[str]]:
    try:
        timeout = kwargs.pop("timeout", 3)
        response = get_http_session().request(method, f"{API_BASE}{path}", timeout=timeout, **kwargs)
        if response.ok:
            return response.json(), None
        return None, f"Request failed ({response.status_code})."
    except requests.RequestException:
        return None, "The marketplace service is offline. Start the API on port 8000."


@st.cache_resource(show_spinner=False)
def get_http_session() -> requests.Session:
    """Reuse a connection pool across Streamlit reruns."""
    return requests.Session()


@st.cache_data(ttl=15, show_spinner=False)
def cached_get(path: str, params_items: tuple[tuple[str, str], ...] = ()) -> tuple[Optional[Any], Optional[str]]:
    """Cache short-lived read requests so Streamlit reruns stay responsive."""
    return api_request("GET", path, params=dict(params_items))


def clear_read_cache() -> None:
    cached_get.clear()


def safe(value: Any) -> str:
    return escape(str(value))


def apply_styles() -> None:
    dark = st.session_state.get("theme") == "dark"
    colors = {
        "bg": "#0c1424" if dark else "#f5f7fb",
        "surface": "#121e31" if dark else "#ffffff",
        "surface2": "#18283d" if dark else "#edf2f8",
        "text": "#f4f7fb" if dark else "#101827",
        "muted": "#a5b3c7" if dark else "#65748a",
        "line": "#2b3c55" if dark else "#dce3ed",
        "accent": "#5b5cf0",
        "accent2": "#746eff",
        "shadow": "rgba(4, 14, 30, .15)" if not dark else "rgba(0, 0, 0, .30)",
    }
    st.markdown(
        f"""
        <style>
        :root {{ --bg:{colors['bg']}; --surface:{colors['surface']}; --surface-2:{colors['surface2']}; --text:{colors['text']}; --muted:{colors['muted']}; --line:{colors['line']}; --accent:{colors['accent']}; --accent-2:{colors['accent2']}; --shadow:{colors['shadow']}; }}
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{ background:var(--bg); color:var(--text); font-family:'DM Sans', sans-serif; }}
        [data-testid="stHeader"] {{ height:0; background:transparent; }}
        [data-testid="stToolbar"] {{ visibility:hidden; height:0; }}
        .block-container {{ width:100%; max-width:1280px; padding:1rem clamp(1rem, 4vw, 3.5rem) 4rem; margin:0 auto; }}
        h1, h2, h3, h4 {{ color:var(--text) !important; font-family:'Manrope', sans-serif !important; letter-spacing:-.035em; }}
        p, label, [data-testid="stCaptionContainer"] {{ color:var(--muted); }}
        .nav-shell {{ position:relative; z-index:5; display:flex; align-items:center; gap:1rem; padding:.65rem .9rem; margin-bottom:2.1rem; background:color-mix(in srgb, var(--surface) 82%, transparent); border:1px solid var(--line); border-radius:18px; box-shadow:0 8px 30px var(--shadow); backdrop-filter:blur(16px); }}
        .wordmark {{ color:var(--text); white-space:nowrap; font:800 1.38rem 'Manrope', sans-serif; letter-spacing:-.055em; }}
        .mark {{ display:inline-grid; place-items:center; width:29px; height:29px; margin-right:.42rem; color:white; background:linear-gradient(135deg,var(--accent),#9d71ff); border-radius:9px; font:800 .95rem 'Manrope', sans-serif; box-shadow:0 6px 16px rgba(91,92,240,.3); }}
        .eyebrow {{ color:var(--accent); font-size:.71rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; }}
        .hero {{ position:relative; display:grid; grid-template-columns:minmax(0, 1.08fr) minmax(360px, .92fr); gap:2rem; min-height:510px; padding:clamp(2rem, 5vw, 4.4rem); overflow:hidden; border:1px solid var(--line); border-radius:28px; background:radial-gradient(circle at 78% 20%, rgba(116,110,255,.16), transparent 31%), linear-gradient(135deg,var(--surface),var(--surface-2)); box-shadow:0 28px 70px var(--shadow); }}
        .hero:before {{ content:''; position:absolute; width:560px; height:560px; right:-200px; bottom:-320px; border:1px solid rgba(116,110,255,.18); border-radius:50%; box-shadow:0 0 0 45px rgba(116,110,255,.04), 0 0 0 90px rgba(116,110,255,.025); }}
        .hero-copy {{ position:relative; z-index:2; align-self:center; max-width:660px; }}
        .hero h1 {{ max-width:700px; margin:.8rem 0 1.15rem; font-size:clamp(2.7rem, 6vw, 5.55rem); line-height:.99; }}
        .hero h1 span {{ color:var(--accent); }}
        .hero-lead {{ max-width:590px; margin:0 0 1.8rem; font-size:1.1rem; line-height:1.7; }}
        .hero-actions {{ display:flex; gap:.75rem; flex-wrap:wrap; margin-bottom:1.8rem; }}
        .hero-note {{ color:var(--muted); font-size:.78rem; }}
        .hero-art {{ position:relative; min-height:350px; perspective:1000px; align-self:center; }}
        .orbit {{ position:absolute; inset:12% 7%; border:1px solid rgba(116,110,255,.22); border-radius:50%; transform:rotate(-22deg) skewX(-12deg); }}
        .orbit:after {{ content:''; position:absolute; width:11px; height:11px; top:12%; right:16%; background:#ffb86b; border-radius:50%; box-shadow:0 0 18px #ffb86b; }}
        .stack-card {{ position:absolute; display:flex; flex-direction:column; justify-content:space-between; width:190px; height:130px; padding:1rem; border:1px solid rgba(255,255,255,.36); border-radius:18px; color:#151d31; background:linear-gradient(135deg,#fff,#e5eaff); box-shadow:0 28px 45px rgba(18,28,70,.25); transform-style:preserve-3d; transition:transform .35s ease, box-shadow .35s ease; animation:float 5s ease-in-out infinite; }}
        .stack-card:hover {{ transform:translateY(-12px) rotateX(6deg) rotateY(-8deg) !important; box-shadow:0 38px 65px rgba(18,28,70,.34); }}
        .stack-card small {{ color:#67728b; font-weight:700; letter-spacing:.08em; text-transform:uppercase; }}
        .stack-card strong {{ font:800 1.15rem 'Manrope', sans-serif; }}
        .stack-card.one {{ top:8%; left:14%; transform:rotate(-9deg); }}
        .stack-card.two {{ top:33%; right:4%; transform:rotate(8deg); background:linear-gradient(135deg,#e7e4ff,#cfd3ff); }}
        .stack-card.three {{ bottom:3%; left:22%; transform:rotate(5deg); background:linear-gradient(135deg,#e1fff4,#c4f2e5); }}
        .stack-card .mini-bars {{ display:flex; gap:4px; align-items:end; height:25px; }}
        .mini-bars i {{ display:block; width:8px; border-radius:4px; background:#5b5cf0; }}
        .mini-bars i:nth-child(1) {{ height:12px; }} .mini-bars i:nth-child(2) {{ height:22px; }} .mini-bars i:nth-child(3) {{ height:17px; }} .mini-bars i:nth-child(4) {{ height:27px; }}
        .search-panel {{ position:relative; z-index:3; display:flex; align-items:center; gap:.55rem; max-width:700px; padding:.45rem; margin:-1.8rem auto 0; background:var(--surface); border:1px solid var(--line); border-radius:14px; box-shadow:0 16px 40px var(--shadow); }}
        .search-panel > div {{ flex:1; }}
        .section {{ padding-top:5.2rem; }}
        .section-head {{ display:flex; align-items:end; justify-content:space-between; gap:1rem; margin-bottom:1.35rem; }}
        .section-head h2 {{ margin:.35rem 0 0; font-size:clamp(1.75rem, 3vw, 2.5rem); }}
        .section-head p {{ max-width:460px; margin:0; text-align:right; line-height:1.55; }}
        .category-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1rem; }}
        .category-card {{ min-height:188px; padding:1.25rem; border:1px solid var(--line); border-radius:18px; background:var(--surface); box-shadow:0 10px 30px var(--shadow); transition:transform .28s ease, border-color .28s ease, box-shadow .28s ease; }}
        .category-card:hover {{ transform:translateY(-7px) rotateX(2deg); border-color:var(--accent); box-shadow:0 20px 40px var(--shadow); }}
        .category-icon {{ display:grid; place-items:center; width:43px; height:43px; margin-bottom:1.4rem; border-radius:13px; font-weight:800; color:#fff; background:linear-gradient(135deg,var(--accent),#9a76ff); }}
        .category-icon.coral {{ background:linear-gradient(135deg,#f27d71,#e74f8c); }} .category-icon.mint {{ background:linear-gradient(135deg,#20ae9b,#55c978); }} .category-icon.blue {{ background:linear-gradient(135deg,#4286f4,#32c3db); }} .category-icon.gold {{ background:linear-gradient(135deg,#e19a3f,#e6c35c); }}
        .category-card h3 {{ margin:0 0 .45rem; font-size:1rem; }}
        .category-card p {{ margin:0; font-size:.84rem; line-height:1.5; }}
        .gig-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1rem; }}
        .gig-card {{ display:flex; min-width:0; min-height:355px; flex-direction:column; justify-content:space-between; overflow:hidden; border:1px solid var(--line); border-radius:18px; background:var(--surface); box-shadow:0 10px 30px var(--shadow); transition:transform .28s ease, box-shadow .28s ease; }}
        .gig-card:hover {{ transform:translateY(-7px); box-shadow:0 22px 44px var(--shadow); }}
        .gig-visual {{ display:flex; align-items:end; height:135px; padding:1.1rem; color:white; background:linear-gradient(135deg,#313b76,#8c75e9); }}
        .gig-visual.coral {{ background:linear-gradient(135deg,#7d354f,#f28b70); }} .gig-visual.mint {{ background:linear-gradient(135deg,#145968,#44c7a0); }} .gig-visual.blue {{ background:linear-gradient(135deg,#174a78,#4fc8df); }}
        .visual-word {{ opacity:.92; font:800 1.55rem 'Manrope', sans-serif; letter-spacing:-.06em; }}
        .gig-body {{ padding:1.15rem; }}
        .gig-meta {{ display:flex; align-items:center; justify-content:space-between; gap:.6rem; color:var(--muted); font-size:.77rem; }}
        .tag {{ display:inline-block; padding:.28rem .6rem; color:var(--accent); background:color-mix(in srgb, var(--accent) 11%, transparent); border-radius:99px; font-size:.7rem; font-weight:700; }}
        .gig-card h3 {{ margin:.7rem 0 .45rem; font-size:1rem; line-height:1.35; }}
        .gig-card p {{ min-height:48px; margin:0; font-size:.84rem; line-height:1.5; }}
        .gig-footer {{ display:flex; align-items:center; justify-content:space-between; padding:0 1.15rem 1.15rem; }}
        .avatar {{ display:inline-grid; place-items:center; width:30px; height:30px; margin-right:.45rem; color:#fff; background:linear-gradient(135deg,#111b35,#6475a6); border-radius:50%; font-size:.7rem; font-weight:700; }}
        .creator-line {{ display:flex; align-items:center; color:var(--muted); font-size:.78rem; }}
        .price {{ color:var(--text); font:800 1.1rem 'Manrope', sans-serif; }}
        .showcase {{ position:relative; min-height:440px; padding:3rem; overflow:hidden; border-radius:24px; background:linear-gradient(120deg,#121b35,#212b55 62%,#3b3d85); color:white; }}
        .showcase h2, .showcase p {{ color:white !important; }}
        .showcase-copy {{ position:relative; z-index:2; max-width:390px; }}
        .showcase-copy p {{ line-height:1.65; opacity:.76; }}
        .showcase-cards {{ position:absolute; inset:0; margin-left:43%; perspective:900px; }}
        .showcase-tile {{ position:absolute; display:flex; align-items:center; gap:.65rem; width:170px; padding:1rem; border:1px solid rgba(255,255,255,.22); border-radius:15px; background:rgba(255,255,255,.1); backdrop-filter:blur(12px); box-shadow:0 20px 50px rgba(0,0,0,.24); transition:transform .35s ease, background .35s ease; }}
        .showcase-tile:hover {{ transform:translateY(-10px) rotateY(-10deg) !important; background:rgba(255,255,255,.2); }}
        .showcase-tile:nth-child(1) {{ top:17%; left:16%; transform:rotate(-8deg); }} .showcase-tile:nth-child(2) {{ top:10%; right:8%; transform:rotate(7deg); }} .showcase-tile:nth-child(3) {{ top:44%; left:7%; transform:rotate(5deg); }} .showcase-tile:nth-child(4) {{ top:47%; right:12%; transform:rotate(-5deg); }} .showcase-tile:nth-child(5) {{ bottom:12%; left:25%; transform:rotate(-6deg); }} .showcase-tile:nth-child(6) {{ bottom:10%; right:2%; transform:rotate(8deg); }}
        .tile-dot {{ display:grid; place-items:center; flex:none; width:31px; height:31px; color:#18203d; background:#c7c9ff; border-radius:9px; font-weight:800; font-size:.72rem; }}
        .steps {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:0; }}
        .step {{ position:relative; padding:1.2rem 1.5rem 1.2rem 0; }}
        .step:not(:last-child):after {{ content:''; position:absolute; top:29px; left:47px; right:0; height:1px; background:var(--line); }}
        .step-number {{ position:relative; z-index:1; display:grid; place-items:center; width:58px; height:58px; margin-bottom:1.25rem; color:var(--accent); background:var(--surface); border:1px solid var(--line); border-radius:50%; font:800 1rem 'Manrope', sans-serif; box-shadow:0 7px 18px var(--shadow); }}
        .step h3 {{ margin:0 0 .45rem; font-size:1.05rem; }} .step p {{ margin:0; font-size:.85rem; line-height:1.55; }}
        .cta {{ position:relative; display:flex; align-items:center; justify-content:space-between; gap:2rem; overflow:hidden; margin-top:5.2rem; padding:3.3rem clamp(1.4rem, 5vw, 4rem); border-radius:24px; color:white; background:linear-gradient(120deg,#252a67,#5750c5 60%,#8670ed); }}
        .cta:after {{ content:''; position:absolute; width:300px; height:300px; right:-70px; top:-150px; border:1px solid rgba(255,255,255,.2); border-radius:50%; box-shadow:0 0 0 28px rgba(255,255,255,.05), 0 0 0 58px rgba(255,255,255,.04); }}
        .cta h2, .cta p {{ position:relative; z-index:1; color:white !important; }} .cta h2 {{ margin:.45rem 0 .6rem; font-size:clamp(1.8rem, 3vw, 2.8rem); }} .cta p {{ max-width:510px; margin:0; opacity:.78; }}
        .footer {{ display:grid; grid-template-columns:2fr repeat(3,1fr); gap:2rem; margin-top:4.5rem; padding-top:2rem; border-top:1px solid var(--line); color:var(--muted); font-size:.82rem; }} .footer strong {{ color:var(--text); font:800 1.2rem 'Manrope', sans-serif; }} .footer h4 {{ margin:0 0 .7rem; font-size:.8rem; }} .footer p {{ margin:.3rem 0; }}
        .metric {{ padding:1.15rem; border:1px solid var(--line); border-radius:15px; background:var(--surface); box-shadow:0 9px 25px var(--shadow); }} .metric-label {{ color:var(--muted); font-size:.78rem; font-weight:600; }} .metric-value {{ color:var(--text); margin-top:.35rem; font:800 1.75rem 'Manrope', sans-serif; }}
        .preview {{ padding:1.3rem; border:1px dashed var(--line); border-radius:17px; background:var(--surface-2); }}
        .stButton > button, .stFormSubmitButton > button {{ min-height:2.55rem; border:1px solid var(--line); border-radius:10px; background:var(--surface); color:var(--text); font-weight:700; transition:transform .2s ease, border-color .2s ease, background .2s ease; }}
        .stButton > button:hover, .stFormSubmitButton > button:hover {{ transform:translateY(-2px); border-color:var(--accent); color:var(--accent); }} .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{ color:white; border-color:var(--accent); background:var(--accent); }} .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {{ color:white; background:var(--accent-2); }}
        input, textarea, [data-baseweb="select"] > div {{ background:var(--surface) !important; color:var(--text) !important; border-color:var(--line) !important; }}
        [data-testid="stSidebar"] {{ background:var(--surface); border-right:1px solid var(--line); }}
        @media (max-width:1000px) {{ .nav-shell {{ padding:.45rem .35rem; }} .nav-shell .wordmark {{ font-size:1.05rem; }} .nav-shell .mark {{ width:25px; height:25px; margin-right:.25rem; }} .stButton > button {{ padding-left:.2rem; padding-right:.2rem; font-size:.76rem; }} }}
        @media (max-width:900px) {{ .hero {{ grid-template-columns:1fr; }} .hero-art {{ min-height:300px; }} .category-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} .gig-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} .showcase-cards {{ margin-left:37%; }} }}
        @media (max-width:620px) {{ .block-container {{ padding:1rem 1rem 3rem; }} .nav-shell {{ margin-bottom:1.2rem; }} .hero {{ min-height:0; padding:2rem 1.25rem; border-radius:20px; }} .hero h1 {{ font-size:2.75rem; }} .hero-art {{ min-height:285px; transform:scale(.88); transform-origin:top center; margin-bottom:-35px; }} .search-panel {{ flex-direction:column; align-items:stretch; margin-top:1rem; }} .section {{ padding-top:3.2rem; }} .section-head {{ display:block; }} .section-head p {{ margin-top:.5rem; text-align:left; }} .category-grid, .gig-grid {{ grid-template-columns:1fr; }} .showcase {{ min-height:650px; padding:2rem 1.3rem; }} .showcase-cards {{ inset:230px 0 0; margin:0; transform:scale(.9); }} .steps {{ grid-template-columns:1fr 1fr; gap:1rem; }} .step:not(:last-child):after {{ display:none; }} .cta {{ display:block; padding:2.2rem 1.3rem; }} .cta .stButton {{ margin-top:1.4rem; }} .footer {{ grid-template-columns:1fr 1fr; }} }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def navigate(page: str) -> None:
    st.session_state["page"] = page
    st.rerun()


def creator_name() -> str:
    return st.session_state.get("user_name", "").strip().lower()


def creator_gigs() -> tuple[list[dict], Optional[str]]:
    gigs, error = cached_get("/creator/gigs", tuple(sorted((("creator_email", client_email()), ("creator_name", st.session_state.get("user_name", "")), ("limit", str(PAGE_SIZE))))))
    return (gigs or []), error


def creator_bookings() -> tuple[list[dict], Optional[str]]:
    bookings, error = cached_get("/creator/bookings", tuple(sorted((("creator_email", client_email()), ("creator_name", st.session_state.get("user_name", "")), ("limit", str(PAGE_SIZE))))))
    return (bookings or []), error


def client_email() -> str:
    return st.session_state.get("user_email", "").strip().lower()


def client_saved_gigs() -> tuple[list[dict], Optional[str]]:
    return cached_get("/client/saved-gigs", (("client_email", client_email()),))


def save_client_gig(gig_id: int, saved: bool) -> Optional[str]:
    method = "DELETE" if saved else "POST"
    _, error = api_request(method, f"/client/saved-gigs/{gig_id}", params={"client_email": client_email()})
    if not error:
        clear_read_cache()
    return error


def render_theme_control() -> None:
    selected = st.sidebar.selectbox("Appearance", ["Light", "Dark"], index=0 if st.session_state["theme"] == "light" else 1)
    selected_theme = selected.lower()
    if selected_theme != st.session_state["theme"]:
        st.session_state["theme"] = selected_theme
        st.rerun()


def render_nav(authenticated: bool = False) -> None:
    nav = st.columns([1.35, 1, 1, 1.05, 1.2, 1, 1, 1.35] if not authenticated else [1.35, 1, 1, 1.05, 1.2, 1.1])
    with nav[0]:
        st.markdown('<div class="nav-shell"><div class="wordmark"><span class="mark">T</span>TheHub</div></div>', unsafe_allow_html=True)
    links = [(1, "Home", "home"), (2, "Explore", "explore"), (3, "Categories", "categories"), (4, "How It Works", "how")]
    for index, label, page in links:
        with nav[index]:
            if st.button(label, key=f"nav_{label}", use_container_width=True):
                navigate("home" if page in {"categories", "how"} else page)
    if not authenticated:
        with nav[5]:
            if st.button("Login", key="nav_login", use_container_width=True):
                navigate("login")
        with nav[6]:
            if st.button("Sign Up", key="nav_signup", use_container_width=True):
                navigate("login")
        with nav[7]:
            if st.button("Post a Gig", key="nav_post", type="primary", use_container_width=True):
                navigate("login")


def category_class(category: str) -> str:
    for name, _, _, color in CATEGORY_CARDS:
        if name == category:
            return color
    return "violet"


def render_category_grid() -> None:
    st.markdown('<section class="section"><div class="section-head"><div><div class="eyebrow">Browse by expertise</div><h2>Find the right specialist</h2></div><p>Explore a focused network of people who make ambitious work happen.</p></div></section>', unsafe_allow_html=True)
    for row_start in range(0, len(CATEGORY_CARDS), 4):
        columns = st.columns(4)
        for column, (name, icon, copy, color) in zip(columns, CATEGORY_CARDS[row_start:row_start + 4]):
            with column:
                st.markdown(f'<div class="category-card"><div class="category-icon {color}">{icon}</div><h3>{name}</h3><p>{copy}</p></div>', unsafe_allow_html=True)
                if st.button("Explore category", key=f"category_{name}", use_container_width=True):
                    st.session_state["category_filter"] = CATEGORY_API_MAP.get(name, name)
                    navigate("explore")


def render_gig_card(gig: dict, key_prefix: str) -> None:
    category = safe(gig.get("category", "Creator service"))
    title = safe(gig.get("title", "Untitled gig"))
    creator = safe(gig.get("creator_name", "Creator"))
    description = safe(gig.get("description", ""))
    initials = "".join(part[0] for part in creator.split()[:2]).upper() or "C"
    visual_word = {"Video & UGC": "MAKE / MOVE", "Design & Graphics": "FORM / FEEL", "Writing & Translation": "WORDS / WORK", "Tech & AI": "BUILD / SHIP"}.get(gig.get("category"), "CREATE / GROW")
    color = category_class(gig.get("category", ""))
    st.markdown(f'<div class="gig-card"><div class="gig-visual {color}"><span class="visual-word">{visual_word}</span></div><div class="gig-body"><div class="gig-meta"><span class="tag">{category}</span><span>Top rated</span></div><h3>{title}</h3><p>{description}</p></div><div class="gig-footer"><span class="creator-line"><span class="avatar">{initials}</span>{creator}</span><span class="price">From ${float(gig.get("rate", 0)):.0f}</span></div></div>', unsafe_allow_html=True)
    if st.button("View gig", key=f"{key_prefix}_{gig['id']}", use_container_width=True):
        st.session_state["selected_gig"] = gig
        navigate("gig")


def render_client_gig_card(gig: dict, key_prefix: str, saved_ids: set[int]) -> None:
    """Marketplace card with client actions, keeping creator cards unchanged."""
    category = safe(gig.get("category", "Creator service"))
    title = safe(gig.get("title", "Untitled gig"))
    creator = safe(gig.get("creator_name", "Creator"))
    description = safe(gig.get("description", ""))
    initials = "".join(part[0] for part in creator.split()[:2]).upper() or "C"
    color = category_class(gig.get("category", ""))
    st.markdown(f'<div class="gig-card"><div class="gig-visual {color}"><span class="visual-word">{category}</span></div><div class="gig-body"><div class="gig-meta"><span class="tag">{category}</span><span>Rating unavailable</span></div><h3>{title}</h3><p>{description}</p></div><div class="gig-footer"><span class="creator-line"><span class="avatar">{initials}</span>{creator}</span><span class="price">From ${float(gig.get("rate", 0)):.0f}</span></div></div>', unsafe_allow_html=True)
    view_col, save_col = st.columns([1.35, 1])
    with view_col:
        if st.button("View Gig", key=f"{key_prefix}_view_{gig['id']}", use_container_width=True):
            st.session_state["selected_gig"] = gig
            navigate("client_gig")
    with save_col:
        is_saved = gig["id"] in saved_ids
        if st.button("Saved" if is_saved else "Save", key=f"{key_prefix}_save_{gig['id']}", use_container_width=True):
            error = save_client_gig(gig["id"], is_saved)
            if error:
                st.error(error)
            else:
                st.rerun()


def render_home() -> None:
    render_nav()
    st.markdown('<section class="hero"><div class="hero-copy"><div class="eyebrow">The creator marketplace for modern teams</div><h1>Turn Your Skills Into <span>Opportunities.</span></h1><p class="hero-lead">Discover talented creators, showcase your skills, and connect with people looking for what you do best.</p><div class="hero-actions"><div id="explore-cta"></div></div><span class="hero-note">A thoughtful network for work with a point of view.</span></div><div class="hero-art"><div class="orbit"></div><div class="stack-card one"><small>Creator profile</small><strong>Visual identity</strong><div class="mini-bars"><i></i><i></i><i></i><i></i></div></div><div class="stack-card two"><small>New opportunity</small><strong>AI workflow</strong><span style="font-size:.75rem;color:#67728b">12 proposals this week</span></div><div class="stack-card three"><small>Live project</small><strong>Launch campaign</strong><span style="font-size:.75rem;color:#487b6f">On track · 86%</span></div></div></section>', unsafe_allow_html=True)
    search_col, category_col, button_col = st.columns([2.4, 1.25, .85])
    with search_col:
        search = st.text_input("Search services", placeholder="What are you looking for?", label_visibility="collapsed", key="home_search")
    with category_col:
        category = st.selectbox("Category", CATEGORIES, label_visibility="collapsed", key="home_category")
    with button_col:
        if st.button("Search", type="primary", use_container_width=True):
            st.session_state["explore_search"] = search
            st.session_state["category_filter"] = category
            navigate("explore")
    explore_col, sell_col = st.columns([1, 1])
    with explore_col:
        if st.button("Explore Gigs", type="primary", use_container_width=True):
            navigate("explore")
    with sell_col:
        if st.button("Start Selling", use_container_width=True):
            navigate("login")

    render_category_grid()
    st.markdown('<section class="section"><div class="section-head"><div><div class="eyebrow">Fresh on TheHub</div><h2>Explore what creators are offering</h2></div><p>Real services from the marketplace, ready for your next brief.</p></div>', unsafe_allow_html=True)
    gigs, error = cached_get("/gigs", (("limit", "6"), ("sort_by", "newest")))
    if error:
        st.warning(error)
    elif gigs:
        for row_start in range(0, min(len(gigs), 6), 3):
            columns = st.columns(3)
            for column, gig in zip(columns, gigs[row_start:row_start + 3]):
                with column:
                    render_gig_card(gig, "featured")
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<section class="section showcase"><div class="showcase-copy"><div class="eyebrow" style="color:#a8adff">Built for creators</div><h2>One place for every kind of good work.</h2><p>From a first sketch to a finished launch, TheHub brings independent talent and meaningful projects into the same room.</p></div><div class="showcase-cards"><div class="showcase-tile"><span class="tile-dot">D</span><strong>Design</strong></div><div class="showcase-tile"><span class="tile-dot">AI</span><strong>AI systems</strong></div><div class="showcase-tile"><span class="tile-dot">V</span><strong>Video</strong></div><div class="showcase-tile"><span class="tile-dot">&lt;&gt;</span><strong>Coding</strong></div><div class="showcase-tile"><span class="tile-dot">M</span><strong>Marketing</strong></div><div class="showcase-tile"><span class="tile-dot">W</span><strong>Writing</strong></div></div></section>', unsafe_allow_html=True)

    st.markdown('<section class="section"><div class="section-head"><div><div class="eyebrow">A clearer way to collaborate</div><h2>How it works</h2></div></div><div class="steps">', unsafe_allow_html=True)
    for number, title, copy in [("01", "Discover", "Search creator services by skill, category, or budget."), ("02", "Choose", "Compare the right fit and send a clear project brief."), ("03", "Collaborate", "Work together with transparent expectations and pricing."), ("04", "Get results", "Move your idea forward with work made for your goals.")]:
        st.markdown(f'<div class="step"><div class="step-number">{number}</div><h3>{title}</h3><p>{copy}</p></div>', unsafe_allow_html=True)
    st.markdown('</div></section>', unsafe_allow_html=True)
    render_creator_cta()
    render_footer()


def render_creator_cta() -> None:
    st.markdown('<section class="cta"><div><div class="eyebrow" style="color:#b8b9ff">For creators</div><h2>Your Skill Could Be Someone’s Next Solution.</h2><p>Create your first gig and put your skills in front of people who need them.</p></div>', unsafe_allow_html=True)
    if st.button("Create Your Gig", key="creator_cta", type="primary"):
        navigate("login")
    st.markdown('</section>', unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown('<footer class="footer"><div><strong>TheHub</strong><p>A more human marketplace for ambitious work.</p></div><div><h4>Marketplace</h4><p>Explore Gigs</p><p>Categories</p></div><div><h4>For creators</h4><p>Post a Gig</p><p>How It Works</p></div><div><h4>Support</h4><p>Privacy</p><p>Terms</p></div></footer>', unsafe_allow_html=True)


def render_explore() -> None:
    render_nav(authenticated=st.session_state["logged_in"])
    st.markdown('<div class="section-head"><div><div class="eyebrow">The marketplace</div><h1>Explore Gigs</h1><p>Compare services from creators ready to help you move faster.</p></div></div>', unsafe_allow_html=True)
    filter_one, filter_two, filter_three, filter_four = st.columns([2, 1.2, 1, 1.2])
    with filter_one:
        search = st.text_input("Search services", value=st.session_state.pop("explore_search", ""), placeholder="Try branding or automation")
    with filter_two:
        saved_category = st.session_state.pop("category_filter", "All")
        category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(saved_category) if saved_category in CATEGORIES else 0)
    with filter_three:
        max_price = st.number_input("Max price", min_value=0, value=0, step=25, help="Set to 0 for any price.")
    with filter_four:
        sort_label = st.selectbox("Sort by", ["Newest", "Price: Low to High", "Price: High to Low"])
    params = {"sort_by": {"Newest": "newest", "Price: Low to High": "cheapest", "Price: High to Low": "priciest"}[sort_label]}
    if search.strip():
        params["search"] = search.strip()
    if category != "All":
        params["category"] = CATEGORY_API_MAP.get(category, category)
    gigs, error = cached_get("/gigs", tuple(sorted((str(key), str(value)) for key, value in params.items())))
    if error:
        st.error(error)
        return
    gigs = [gig for gig in gigs if not max_price or gig["rate"] <= max_price]
    st.caption(f"{len(gigs)} service(s) available")
    if not gigs:
        st.info("No gigs match these filters. Try another category or broader search.")
        return
    for row_start in range(0, len(gigs), 3):
        columns = st.columns(3)
        for column, gig in zip(columns, gigs[row_start:row_start + 3]):
            with column:
                render_gig_card(gig, "explore")


def render_gig_detail() -> None:
    render_nav(authenticated=st.session_state["logged_in"])
    gig = st.session_state.get("selected_gig")
    if not gig:
        navigate("explore")
    latest, _ = cached_get(f"/gigs/{gig['id']}")
    gig = latest or gig
    st.markdown(f'<div class="eyebrow">{safe(gig["category"])}</div><h1>{safe(gig["title"])}</h1><p>Created by <strong>{safe(gig["creator_name"])}</strong></p>', unsafe_allow_html=True)
    left, right = st.columns([1.7, 1])
    with left:
        st.markdown(f'<div class="preview"><h3>About this gig</h3><p>{safe(gig["description"])}</p><div class="price">Starting at ${float(gig["rate"]):.2f}</div></div>', unsafe_allow_html=True)
    with right:
        if not st.session_state["logged_in"]:
            st.info("Log in as a client to send a booking request.")
            if st.button("Login to book", type="primary", use_container_width=True):
                navigate("login")
        else:
            with st.form(f"book_{gig['id']}"):
                st.subheader("Start a conversation")
                name = st.text_input("Your name")
                email = st.text_input("Email")
                requirements = st.text_area("Project brief")
                if st.form_submit_button("Send booking request", type="primary", use_container_width=True):
                    payload = {"gig_id": gig["id"], "client_name": name.strip(), "client_email": email.strip(), "requirements": requirements.strip()}
                    if not all(payload.values()):
                        st.error("Complete every field before sending.")
                    else:
                        _, error = api_request("POST", "/bookings", json=payload)
                        if error:
                            st.error(error)
                        else:
                            st.success("Booking request sent.")
                            st.session_state["active_client"] = name.strip()
    if st.button("Back to Explore"):
        navigate("explore")


def render_login() -> None:
    render_nav()
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown('<section class="section"><div class="eyebrow">Welcome to TheHub</div><h1>Bring your next idea to life.</h1><p class="hero-lead">Use a demo workspace to explore the creator marketplace and experience the complete workflow.</p></section>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="preview">', unsafe_allow_html=True)
        st.subheader("Sign in")
        role = st.radio("Workspace", ["Creator", "Client"], horizontal=True)
        email = st.text_input("Email", placeholder="creator@thehub.com")
        password = st.text_input("Password", type="password")
        if st.button("Continue", type="primary", use_container_width=True):
            accounts = {"creator@thehub.com": ("creator123", "creator", "Alex Rivera"), "client@thehub.com": ("client123", "client", "Ava Johnson")}
            account = accounts.get(email.strip().lower())
            if account and account[0] == password and account[1] == role.lower():
                st.session_state.update(logged_in=True, user_role=account[1], user_name=account[2], user_email=email.strip().lower(), page="dashboard")
                st.rerun()
            else:
                st.error("Use one of the demo accounts below.")
        st.caption("Demo access")
        st.code("Creator: creator@thehub.com / creator123\nClient: client@thehub.com / client123")
        st.markdown('</div>', unsafe_allow_html=True)


def render_creator_overview() -> None:
    stats, error = cached_get("/stats")
    gigs, _ = cached_get("/gigs", (("limit", str(PAGE_SIZE)), ("sort_by", "newest")))
    st.markdown('<div class="eyebrow">Creator workspace</div><h1>Good work starts here.</h1><p>Track your marketplace presence and respond to new opportunities.</p>', unsafe_allow_html=True)
    if error:
        st.warning(error)
        stats = {"total_gigs": 0, "pending_bookings": 0, "accepted_bookings": 0, "total_volume": 0}
    metrics = [("Total Gigs", stats.get("total_gigs", 0)), ("Pending Requests", stats.get("pending_bookings", 0)), ("Accepted Deals", stats.get("accepted_bookings", 0)), ("Platform Volume", f'${stats.get("total_volume", 0):,.0f}')]
    cols = st.columns(4)
    for column, (label, value) in zip(cols, metrics):
        with column:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)
    st.markdown('<section class="section"><div class="section-head"><div><div class="eyebrow">Recent activity</div><h2>Recent gigs</h2></div></div>', unsafe_allow_html=True)
    if gigs:
        columns = st.columns(3)
        for column, gig in zip(columns, gigs[:3]):
            with column:
                render_gig_card(gig, "dashboard")
    st.markdown('</section>', unsafe_allow_html=True)


def render_post_gig() -> None:
    st.markdown('<div class="eyebrow">Creator tools</div><h1>Post a Gig</h1><p>Give clients a clear, confident reason to choose your expertise.</p>', unsafe_allow_html=True)
    form_col, preview_col = st.columns([1.15, .85])
    with form_col:
        with st.form("post_gig_form", clear_on_submit=True):
            st.markdown("#### Creator information")
            creator = st.text_input("Creator name", value=st.session_state.get("user_name", ""))
            st.markdown("#### Gig information")
            title = st.text_input("Service title", placeholder="e.g. Brand identity for a growing startup")
            category = st.selectbox("Category", CATEGORIES[1:])
            st.markdown("#### Pricing and description")
            rate = st.number_input("Starting price (USD)", min_value=1.0, value=75.0, step=5.0)
            deliverables = st.text_input("Deliverables", placeholder="e.g. 3 concepts, source files, 2 revisions")
            delivery_time = st.text_input("Delivery time", placeholder="e.g. 3 days")
            skills = st.text_input("Skills", placeholder="e.g. React, Figma, SEO")
            thumbnail_url = st.text_input("Optional thumbnail URL", placeholder="https://...")
            description = st.text_area("What will you deliver?", placeholder="Describe your process, deliverables, and ideal client.")
            publish = st.form_submit_button("Publish gig", type="primary", use_container_width=True)
            if publish:
                payload = {"creator_name": creator.strip(), "owner_email": st.session_state.get("user_email", ""), "title": title.strip(), "category": category, "rate": float(rate), "description": description.strip(), "deliverables": deliverables.strip(), "delivery_time": delivery_time.strip(), "skills": skills.strip(), "thumbnail_url": thumbnail_url.strip()}
                if not payload["creator_name"] or not payload["title"] or not payload["description"]:
                    st.error("Complete the creator name, title, and description.")
                else:
                    _, error = api_request("POST", "/gigs", json=payload)
                    if error:
                        st.error(error)
                    else:
                        st.success("Your gig is live on TheHub.")
                        clear_read_cache()
    with preview_col:
        st.markdown("#### Live preview")
        st.markdown(f'<div class="preview"><span class="tag">{safe(category if "category" in locals() else "Video & UGC")}</span><h3>{safe(title if "title" in locals() and title else "Your service title")}</h3><div class="creator-line">By {safe(creator if "creator" in locals() and creator else "Your name")}</div><p>{safe(description if "description" in locals() and description else "Your clear, useful service description will appear here.")}</p><div class="price">From ${rate if "rate" in locals() else 75:.0f}</div></div>', unsafe_allow_html=True)


def render_bookings() -> None:
    is_creator = st.session_state["user_role"] == "creator"
    endpoint = "/creator/bookings" if is_creator else "/client/bookings"
    params = {} if is_creator else {"client_name": st.session_state.get("active_client", "")}
    st.markdown(f'<div class="eyebrow">{"Creator inbox" if is_creator else "Client workspace"}</div><h1>{"Booking requests" if is_creator else "My bookings"}</h1><p>{"Review requests and keep projects moving." if is_creator else "Track every request from first brief to accepted project."}</p>', unsafe_allow_html=True)
    if not is_creator:
        params["client_name"] = st.text_input("Filter by client name", value=params["client_name"])
    bookings, error = cached_get(endpoint, tuple(sorted((str(key), str(value)) for key, value in params.items())))
    if error:
        st.error(error)
        return
    if not bookings:
        st.info("No bookings yet. Explore gigs to start a project.")
        return
    for booking in bookings:
        with st.container(border=True):
            left, right = st.columns([3, 1])
            with left:
                st.markdown(f"### {safe(booking['gig_title'])}")
                st.write(f"**{('Client' if is_creator else 'Creator')}:** {safe(booking['client_name'] if is_creator else booking['creator_name'])}  \n**Brief:** {safe(booking['requirements'])}")
            with right:
                st.metric("Status", booking["status"])
                if is_creator and booking["status"] == "Pending":
                    if st.button("Accept", key=f"accept_{booking['id']}", type="primary", use_container_width=True):
                        api_request("PATCH", f"/bookings/{booking['id']}", json={"status": "Accepted"})
                        st.rerun()
                    with st.popover("Decline", use_container_width=True):
                        reason = st.text_input("Reason", key=f"reason_{booking['id']}")
                        if st.button("Confirm decline", key=f"decline_{booking['id']}"):
                            api_request("PATCH", f"/bookings/{booking['id']}", json={"status": "Declined", "rejection_reason": reason.strip()})
                            st.rerun()
                elif booking["status"] == "Declined" and booking.get("rejection_reason"):
                    st.caption(booking["rejection_reason"])


def creator_metric_cards(gigs: list[dict], bookings: list[dict]) -> None:
    accepted = [booking for booking in bookings if booking.get("status") == "Accepted"]
    earnings = sum(float(next((gig.get("rate", 0) for gig in gigs if gig.get("id") == booking.get("gig_id")), 0)) for booking in accepted)
    metrics = [("Total Gigs", len(gigs)), ("Active Gigs", len(gigs)), ("Orders", len(bookings)), ("Earnings", f"${earnings:,.0f}")]
    columns = st.columns(4)
    for column, (label, value) in zip(columns, metrics):
        with column:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)


def render_creator_home() -> None:
    gigs, gigs_error = creator_gigs()
    bookings, bookings_error = creator_bookings()
    st.markdown('<div class="eyebrow">Creator workspace</div><h1>Welcome back, Creator</h1><p>Everything you need to publish, manage, and grow your work is here.</p>', unsafe_allow_html=True)
    if gigs_error or bookings_error:
        st.warning(gigs_error or bookings_error)
    creator_metric_cards(gigs, bookings)
    recent_orders, recent_messages = st.columns([1.25, .75])
    with recent_orders:
        st.markdown('<section class="section"><div class="section-head"><div><div class="eyebrow">Live activity</div><h2>Recent orders</h2></div></div>', unsafe_allow_html=True)
        if bookings:
            for booking in bookings[:4]:
                with st.container(border=True):
                    st.markdown(f"**#{booking['id']} · {safe(booking['gig_title'])}**")
                    st.caption(f"Client: {safe(booking['client_name'])} · Status: {safe(booking['status'])}")
        else:
            st.info("Orders from clients will appear here.")
        st.markdown('</section>', unsafe_allow_html=True)
    with recent_messages:
        st.markdown('<section class="section"><div class="section-head"><div><div class="eyebrow">Inbox</div><h2>Recent messages</h2></div></div>', unsafe_allow_html=True)
        st.info("Messaging is not part of the current API yet. Your booking requests are available in Orders.")
        st.markdown('</section>', unsafe_allow_html=True)
    st.markdown('<section class="section"><div class="section-head"><div><div class="eyebrow">Your storefront</div><h2>Gig performance</h2></div></div>', unsafe_allow_html=True)
    if gigs:
        for gig in gigs[:3]:
            left, right = st.columns([3, 1])
            with left:
                st.markdown(f"**{safe(gig['title'])}**")
                st.progress(min(1.0, 0.25 + (float(gig.get('rate', 0)) / 600)), text=f"${float(gig.get('rate', 0)):.0f} starting price")
            with right:
                st.caption("Views")
                st.metric("Orders", sum(1 for booking in bookings if booking.get("gig_id") == gig.get("id")))
    else:
        st.info("Publish your first gig to see performance here.")
    st.markdown('</section>', unsafe_allow_html=True)


def render_creator_gigs() -> None:
    gigs, error = creator_gigs()
    st.markdown('<div class="eyebrow">Creator catalog</div><h1>My Gigs</h1><p>Manage the services you offer to the TheHub marketplace.</p>', unsafe_allow_html=True)
    selected_filter = st.radio("Gig status", ["All", "Active", "Draft", "Paused"], horizontal=True, label_visibility="collapsed")
    if error:
        st.error(error)
        return
    if not gigs:
        st.info("You have not published a gig yet.")
        if st.button("Create your first gig", type="primary"):
            navigate("creator_create")
        return
    for gig in gigs:
        if selected_filter != "All" and gig.get("status", "Active") != selected_filter:
            continue
        with st.container(border=True):
            left, middle, right = st.columns([2.3, 1.1, .9])
            with left:
                st.markdown(f"### {safe(gig['title'])}")
                st.caption(f"{safe(gig['category'])} · Published gig")
                st.write(safe(gig["description"]))
            with middle:
                st.metric("Price", f"${float(gig['rate']):.0f}")
                st.caption(f"Status: {gig.get('status', 'Active')}")
                st.caption(f"Views: {gig.get('views', 0)} · Rating: {gig.get('rating', 0) or 'Not rated'}")
            with right:
                if st.button("View", key=f"creator_view_{gig['id']}", use_container_width=True):
                    st.session_state["selected_gig"] = gig
                    navigate("gig")
                if st.button("Edit", key=f"creator_edit_{gig['id']}", use_container_width=True):
                    st.session_state["editing_gig"] = gig
                    navigate("creator_edit")
                if st.button("Delete", key=f"creator_delete_{gig['id']}", use_container_width=True):
                    st.session_state["delete_gig_id"] = gig["id"]
                    st.rerun()
                if st.session_state.get("delete_gig_id") == gig["id"]:
                    st.warning("Delete this gig permanently?")
                    confirm_col, cancel_col = st.columns(2)
                    with confirm_col:
                        if st.button("Confirm", key=f"confirm_delete_{gig['id']}", type="primary"):
                            _, delete_error = api_request("DELETE", f"/gigs/{gig['id']}", params={"owner_email": st.session_state["user_email"]})
                            if delete_error:
                                st.error(delete_error)
                            else:
                                st.session_state.pop("delete_gig_id", None)
                                clear_read_cache()
                                st.rerun()
                    with cancel_col:
                        if st.button("Cancel", key=f"cancel_delete_{gig['id']}"):
                            st.session_state.pop("delete_gig_id", None)
                            st.rerun()


def render_creator_edit() -> None:
    gig = st.session_state.get("editing_gig")
    if not gig:
        navigate("creator_gigs")
    st.markdown('<div class="eyebrow">Creator catalog</div><h1>Edit Gig</h1><p>Update your service and keep the marketplace listing current.</p>', unsafe_allow_html=True)
    with st.form(f"edit_gig_{gig['id']}"):
        title = st.text_input("Gig title", value=gig.get("title", ""))
        category = st.selectbox("Category", CATEGORIES[1:], index=CATEGORIES[1:].index(gig.get("category")) if gig.get("category") in CATEGORIES[1:] else 0)
        description = st.text_area("Description", value=gig.get("description", ""))
        deliverables = st.text_input("Deliverables", value=gig.get("deliverables", ""))
        delivery_time = st.text_input("Delivery time", value=gig.get("delivery_time", ""))
        skills = st.text_input("Skills", value=gig.get("skills", ""))
        thumbnail_url = st.text_input("Thumbnail URL", value=gig.get("thumbnail_url", ""))
        rate = st.number_input("Price", min_value=1.0, value=float(gig.get("rate", 75)), step=5.0)
        status = st.selectbox("Status", ["Active", "Paused", "Draft"], index=["Active", "Paused", "Draft"].index(gig.get("status", "Active")) if gig.get("status", "Active") in ["Active", "Paused", "Draft"] else 0)
        if st.form_submit_button("Save changes", type="primary"):
            payload = {"owner_email": st.session_state["user_email"], "title": title.strip(), "category": category, "description": description.strip(), "deliverables": deliverables.strip(), "delivery_time": delivery_time.strip(), "skills": skills.strip(), "thumbnail_url": thumbnail_url.strip(), "rate": float(rate), "status": status}
            _, error = api_request("PATCH", f"/gigs/{gig['id']}", json=payload)
            if error:
                st.error(error)
            else:
                clear_read_cache()
                st.session_state.pop("editing_gig", None)
                st.success("Gig updated.")
    if st.button("Back to My Gigs"):
        navigate("creator_gigs")


def render_creator_create() -> None:
    render_post_gig()


def render_creator_orders() -> None:
    bookings, error = creator_bookings()
    st.markdown('<div class="eyebrow">Order management</div><h1>Orders</h1><p>Review incoming client requests and keep every project moving.</p>', unsafe_allow_html=True)
    if error:
        st.error(error)
        return
    if not bookings:
        st.info("No creator orders yet. New client requests will appear here.")
        return
    for booking in bookings:
        with st.container(border=True):
            left, right = st.columns([3, 1])
            with left:
                st.markdown(f"### Order #{booking['id']} · {safe(booking['gig_title'])}")
                st.write(f"**Client:** {safe(booking['client_name'])}  \n**Brief:** {safe(booking['requirements'])}")
                st.caption(f"Amount: ${float(booking.get('rate', 0)):.2f} · Date: available when order timestamps are added")
            with right:
                st.metric("Status", booking["status"])
                if booking["status"] == "Pending":
                    if st.button("Accept", key=f"creator_order_accept_{booking['id']}", type="primary", use_container_width=True):
                        _, update_error = api_request("PATCH", f"/bookings/{booking['id']}", json={"status": "In Progress", "owner_email": st.session_state["user_email"]})
                        if update_error:
                            st.error(update_error)
                        else:
                            clear_read_cache()
                            st.rerun()
                    with st.popover("Decline", use_container_width=True):
                        reason = st.text_input("Reason", key=f"creator_order_reason_{booking['id']}")
                        if st.button("Confirm decline", key=f"creator_order_decline_{booking['id']}"):
                            _, update_error = api_request("PATCH", f"/bookings/{booking['id']}", json={"status": "Cancelled", "owner_email": st.session_state["user_email"], "rejection_reason": reason.strip()})
                            if update_error:
                                st.error(update_error)
                            else:
                                clear_read_cache()
                                st.rerun()
                elif booking["status"] == "In Progress":
                    if st.button("Mark completed", key=f"creator_order_complete_{booking['id']}", type="primary", use_container_width=True):
                        _, update_error = api_request("PATCH", f"/bookings/{booking['id']}", json={"status": "Completed", "owner_email": st.session_state["user_email"]})
                        if update_error:
                            st.error(update_error)
                        else:
                            clear_read_cache()
                            st.rerun()


def render_creator_earnings() -> None:
    earnings_params = (("creator_email", st.session_state["user_email"]), ("creator_name", st.session_state["user_name"]))
    earnings, earnings_error = cached_get("/creator/earnings", tuple(sorted(earnings_params)))
    st.markdown('<div class="eyebrow">Financial overview</div><h1>Earnings</h1><p>Understand the value of the work you have accepted.</p>', unsafe_allow_html=True)
    if earnings_error:
        st.error(earnings_error)
        earnings = {"total_earnings": 0, "completed_earnings": 0, "pending_earnings": 0, "orders": 0}
    columns = st.columns(4)
    average = earnings["total_earnings"] / earnings["orders"] if earnings["orders"] else 0
    for column, (label, value) in zip(columns, [("Total Earnings", f"${earnings['total_earnings']:,.0f}"), ("Pending Earnings", f"${earnings['pending_earnings']:,.0f}"), ("Completed Orders", earnings["orders"]), ("Average Order Value", f"${average:,.0f}")]):
        with column:
            st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)
    st.markdown('<section class="section"><div class="section-head"><div><div class="eyebrow">Simple reporting</div><h2>Order mix</h2></div></div>', unsafe_allow_html=True)
    st.info("Earnings are calculated from actual accepted/completed creator orders.")
    st.markdown('</section>', unsafe_allow_html=True)


def render_creator_profile() -> None:
    profile_params = (("creator_email", st.session_state["user_email"]), ("creator_name", st.session_state["user_name"]))
    profile, error = cached_get("/creator/profile", tuple(sorted(profile_params)))
    bookings, _ = creator_bookings()
    if error:
        st.error(error)
        return
    st.markdown('<div class="eyebrow">Creator identity</div><h1>Profile</h1><p>Keep the profile clients see connected to your real creator account.</p>', unsafe_allow_html=True)
    left, right = st.columns([1, 2])
    with left:
        st.markdown(f'<div class="avatar" style="width:76px;height:76px;font-size:1.4rem;margin-bottom:1rem">{safe(st.session_state["user_name"][:2].upper())}</div><h2>{safe(st.session_state["user_name"])}</h2><p>{safe(st.session_state["user_email"])}</p>', unsafe_allow_html=True)
        st.metric("Completed Orders", sum(1 for booking in bookings if booking.get("status") == "Accepted"))
    with right:
        with st.form("creator_profile_form"):
            name = st.text_input("Creator name", value=profile.get("creator_name", st.session_state["user_name"]))
            username = st.text_input("Username", value=profile.get("username", st.session_state["user_email"].split("@")[0]))
            bio = st.text_area("Bio", value=profile.get("bio", ""))
            skills = st.text_input("Skills", value=profile.get("skills", ""))
            categories = st.text_input("Categories", value=profile.get("categories", ""))
            portfolio = st.text_input("Portfolio URL", value=profile.get("portfolio", ""))
            avatar_url = st.text_input("Avatar URL", value=profile.get("avatar_url", ""))
            if st.form_submit_button("Save profile", type="primary"):
                payload = {"creator_email": st.session_state["user_email"], "creator_name": name.strip(), "username": username.strip(), "bio": bio.strip(), "skills": skills.strip(), "categories": categories.strip(), "portfolio": portfolio.strip(), "avatar_url": avatar_url.strip()}
                _, update_error = api_request("PUT", "/creator/profile", json=payload)
                if update_error:
                    st.error(update_error)
                else:
                    st.session_state["user_name"] = name.strip()
                    clear_read_cache()
                    st.success("Profile saved.")
            st.caption(f"{len(bookings)} orders · Rating is calculated when review fields are available.")


def render_creator_analytics() -> None:
    analytics_params = (("creator_email", st.session_state["user_email"]), ("creator_name", st.session_state["user_name"]))
    analytics, error = cached_get("/creator/analytics", tuple(sorted(analytics_params)))
    st.markdown('<div class="eyebrow">Performance</div><h1>Analytics</h1><p>A lightweight view of your current marketplace activity.</p>', unsafe_allow_html=True)
    if error:
        st.error(error)
        return
    cols = st.columns(5)
    for column, (label, value) in zip(cols, [("Gig Views", analytics["gig_views"]), ("Orders", analytics["orders"]), ("Completed", analytics["completed_orders"]), ("Revenue", f"${analytics['revenue']:,.0f}"), ("Conversion", f"{analytics['conversion_rate']:.1f}%")]):
        with column:
            st.metric(label, value)


def render_creator_messages() -> None:
    st.markdown('<div class="eyebrow">Communication</div><h1>Messages</h1><p>Persistent creator-client conversations from the shared messages table.</p>', unsafe_allow_html=True)
    messages, error = cached_get("/messages", (("user_email", st.session_state["user_email"]),))
    if error:
        st.error(error)
        return
    for message in messages or []:
        with st.container(border=True):
            st.caption(f"{safe(message['sender_email'])} → {safe(message['receiver_email'])} · {safe(message['created_at'])}")
            st.write(safe(message["message"]))
    st.markdown("#### Send a message")
    receiver = st.text_input("Client email")
    message_text = st.text_area("Message")
    if st.button("Send message", type="primary"):
        _, send_error = api_request("POST", "/messages", json={"sender_email": st.session_state["user_email"], "receiver_email": receiver.strip(), "message": message_text.strip()})
        if send_error:
            st.error(send_error)
        else:
            clear_read_cache()
            st.success("Message sent.")


def render_client_home() -> None:
    st.markdown('<div class="eyebrow">Client marketplace</div><h1>What do you need help with?</h1><p>Find independent talent for the work that matters next.</p>', unsafe_allow_html=True)
    search_col, button_col = st.columns([4, 1])
    with search_col:
        search = st.text_input("Search", placeholder="Search for services, creators or skills...", label_visibility="collapsed", key="client_home_search")
    with button_col:
        if st.button("Search", type="primary", use_container_width=True):
            st.session_state["client_search"] = search
            navigate("client_explore")
    st.markdown('<section class="section"><div class="section-head"><div><div class="eyebrow">Start here</div><h2>Popular categories</h2></div><p>Explore a focused network of specialists across creative, technical, and growth work.</p></div></section>', unsafe_allow_html=True)
    for row_start in range(0, len(CATEGORY_CARDS), 4):
        columns = st.columns(4)
        for column, (name, icon, copy, color) in zip(columns, CATEGORY_CARDS[row_start:row_start + 4]):
            with column:
                st.markdown(f'<div class="category-card"><div class="category-icon {color}">{icon}</div><h3>{name}</h3><p>{copy}</p></div>', unsafe_allow_html=True)
                if st.button("Browse", key=f"client_category_{name}", use_container_width=True):
                    st.session_state["client_category"] = CATEGORY_API_MAP.get(name, name)
                    navigate("client_explore")
    gigs, error = cached_get("/gigs", (("limit", "6"), ("sort_by", "newest")))
    if error:
        st.warning(error)
    st.markdown('<section class="section"><div class="section-head"><div><div class="eyebrow">Fresh from creators</div><h2>Recommended for you</h2></div></div>', unsafe_allow_html=True)
    if gigs:
        saved_ids = set()
        for row_start in range(0, min(6, len(gigs)), 3):
            columns = st.columns(3)
            for column, gig in zip(columns, gigs[row_start:row_start + 3]):
                with column:
                    render_client_gig_card(gig, "client_home", saved_ids)
    else:
        st.info("No gigs are available yet.")
    st.markdown('</section>', unsafe_allow_html=True)


def render_client_explore() -> None:
    st.markdown('<div class="eyebrow">Client marketplace</div><h1>Explore Gigs</h1><p>Search and compare real services from creators on TheHub.</p>', unsafe_allow_html=True)
    search_col, category_col, price_col, sort_col = st.columns([2.1, 1.2, 1, 1.25])
    with search_col:
        search = st.text_input("Search services", value=st.session_state.pop("client_search", ""), placeholder="Search for services, creators or skills...")
    with category_col:
        saved_category = st.session_state.pop("client_category", "All")
        category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(saved_category) if saved_category in CATEGORIES else 0)
    with price_col:
        max_price = st.number_input("Max price", min_value=0, value=0, step=25, help="Use 0 for any price.")
    with sort_col:
        sort_label = st.selectbox("Sort by", ["Newest", "Price: Low to High", "Price: High to Low", "Rating (unavailable)"])
    params = {"limit": str(PAGE_SIZE), "sort_by": {"Newest": "newest", "Price: Low to High": "cheapest", "Price: High to Low": "priciest", "Rating (unavailable)": "newest"}[sort_label]}
    if search.strip():
        params["search"] = search.strip()
    if category != "All":
        params["category"] = CATEGORY_API_MAP.get(category, category)
    gigs, error = cached_get("/gigs", tuple(sorted((str(key), str(value)) for key, value in params.items())))
    saved, saved_error = client_saved_gigs()
    if error or saved_error:
        st.error(error or saved_error)
        return
    if sort_label == "Rating (unavailable)":
        st.caption("Rating data is not present in the current gig schema, so this view uses newest-first ordering.")
    gigs = [gig for gig in gigs if not max_price or float(gig.get("rate", 0)) <= max_price]
    st.caption(f"{len(gigs)} gig(s) available")
    if not gigs:
        st.info("No gigs match your filters. Try a broader search.")
        return
    saved_ids = {gig["id"] for gig in (saved or [])}
    for row_start in range(0, len(gigs), 3):
        columns = st.columns(3)
        for column, gig in zip(columns, gigs[row_start:row_start + 3]):
            with column:
                render_client_gig_card(gig, "client_explore", saved_ids)


def render_client_gig_detail() -> None:
    gig = st.session_state.get("selected_gig")
    if not gig:
        navigate("client_explore")
    latest, _ = cached_get(f"/gigs/{gig['id']}")
    gig = latest or gig
    saved, _ = client_saved_gigs()
    saved_ids = {item["id"] for item in (saved or [])}
    st.markdown(f'<div class="eyebrow">{safe(gig["category"])}</div><h1>{safe(gig["title"])}</h1><p>Created by <strong>{safe(gig["creator_name"])}</strong> · Rating unavailable</p>', unsafe_allow_html=True)
    left, right = st.columns([1.65, 1])
    with left:
        st.markdown(f'<div class="preview"><div class="gig-visual {category_class(gig.get("category", ""))}" style="border-radius:12px;margin-bottom:1rem"><span class="visual-word">{safe(gig["category"])}</span></div><h2>About this gig</h2><p>{safe(gig["description"])}</p><h3>Deliverables</h3><p>Deliverables and delivery time will be confirmed directly with the creator because these fields are not present in the current database schema.</p><div class="price">Starting at ${float(gig["rate"]):.2f}</div></div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="preview"><h3>Work with this creator</h3><p>Send a brief to start the conversation and place a booking request.</p>', unsafe_allow_html=True)
        if st.button("Contact Creator", use_container_width=True):
            st.info("Messaging is not available in the current API. Use the booking brief below to contact the creator.")
        if st.button("Saved" if gig["id"] in saved_ids else "Save Gig", use_container_width=True):
            error = save_client_gig(gig["id"], gig["id"] in saved_ids)
            if error:
                st.error(error)
            else:
                st.rerun()
        with st.form(f"client_order_{gig['id']}"):
            st.markdown("#### Place order")
            requirements = st.text_area("Project brief")
            if st.form_submit_button("Place Order", type="primary", use_container_width=True):
                payload = {"gig_id": gig["id"], "client_name": st.session_state["user_name"], "client_email": st.session_state["user_email"], "requirements": requirements.strip()}
                if not requirements.strip():
                    st.error("Add a short project brief before placing the order.")
                else:
                    _, error = api_request("POST", "/bookings", json=payload)
                    if error:
                        st.error(error)
                    else:
                        clear_read_cache()
                        st.success("Order request placed.")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Back to Explore"):
        navigate("client_explore")


def render_client_orders() -> None:
    st.markdown('<div class="eyebrow">Client workspace</div><h1>My Orders</h1><p>Track every booking request from brief to completion.</p>', unsafe_allow_html=True)
    bookings, error = cached_get("/client/bookings", (("client_name", st.session_state["user_name"]), ("limit", str(PAGE_SIZE))))
    if error:
        st.error(error)
        return
    if not bookings:
        st.info("You do not have orders yet. Explore gigs to start a project.")
        return
    for booking in bookings:
        with st.container(border=True):
            left, right = st.columns([3, 1])
            with left:
                st.markdown(f"### Order #{booking['id']} · {safe(booking['gig_title'])}")
                st.caption(f"Creator: {safe(booking['creator_name'])} · Date: available when order timestamps are added")
                st.write(f"Amount: ${float(booking.get('rate', 0)):.2f}  \nBrief: {safe(booking['requirements'])}")
            with right:
                st.metric("Status", booking["status"])
                if booking.get("rejection_reason"):
                    st.caption(booking["rejection_reason"])


def render_client_saved() -> None:
    st.markdown('<div class="eyebrow">Your shortlist</div><h1>Saved Gigs</h1><p>Keep promising services close while you compare options.</p>', unsafe_allow_html=True)
    saved, error = client_saved_gigs()
    if error:
        st.error(error)
        return
    if not saved:
        st.info("Saved gigs will appear here. Use Save on any marketplace card.")
        return
    saved_ids = {gig["id"] for gig in saved}
    for row_start in range(0, len(saved), 3):
        columns = st.columns(3)
        for column, gig in zip(columns, saved[row_start:row_start + 3]):
            with column:
                render_client_gig_card(gig, "saved", saved_ids)


def render_client_messages() -> None:
    st.markdown('<div class="eyebrow">Communication</div><h1>Messages</h1><p>Keep creator conversations close to the work you are commissioning.</p>', unsafe_allow_html=True)
    st.info("Messaging is not available in the current API yet. Your project briefs and creator responses remain available in My Orders.")


def render_client_profile() -> None:
    saved, _ = client_saved_gigs()
    bookings, _ = cached_get("/client/bookings", (("client_name", st.session_state["user_name"]), ("limit", str(PAGE_SIZE))))
    st.markdown('<div class="eyebrow">Your account</div><h1>My Profile</h1><p>Manage the client identity used when you place orders.</p>', unsafe_allow_html=True)
    left, right = st.columns([1, 2])
    with left:
        st.markdown(f'<div class="avatar" style="width:76px;height:76px;font-size:1.4rem;margin-bottom:1rem">{safe(st.session_state["user_name"][:2].upper())}</div><h2>{safe(st.session_state["user_name"])}</h2><p>{safe(st.session_state["user_email"])}</p>', unsafe_allow_html=True)
        st.metric("Previous orders", len(bookings or []))
        st.metric("Saved gigs", len(saved or []))
    with right:
        st.text_input("Name", value=st.session_state["user_name"], disabled=True)
        st.text_input("Account email", value=st.session_state["user_email"], disabled=True)
        st.text_area("Bio", value="Profile editing will be enabled when client profile fields are added to the API.", disabled=True)


def render_client_settings() -> None:
    st.markdown('<div class="eyebrow">Workspace preferences</div><h1>Settings</h1><p>Control the presentation of your client workspace.</p>', unsafe_allow_html=True)
    st.checkbox("Use light theme", value=st.session_state["theme"] == "light", key="client_light_theme")
    desired_theme = "light" if st.session_state["client_light_theme"] else "dark"
    if desired_theme != st.session_state["theme"]:
        st.session_state["theme"] = desired_theme
        st.rerun()
    st.caption("Account and notification persistence are not exposed by the current backend.")


def render_creator_settings() -> None:
    st.markdown('<div class="eyebrow">Workspace preferences</div><h1>Settings</h1><p>Control the presentation of your creator workspace.</p>', unsafe_allow_html=True)
    st.checkbox("Use light theme", value=st.session_state["theme"] == "light", key="creator_light_theme")
    desired_theme = "light" if st.session_state["creator_light_theme"] else "dark"
    if desired_theme != st.session_state["theme"]:
        st.session_state["theme"] = desired_theme
        st.rerun()
    st.caption("Account and notification persistence are not exposed by the current backend.")


def render_creator_workspace() -> None:
    st.sidebar.markdown('<div class="wordmark"><span class="mark">T</span>TheHub</div>', unsafe_allow_html=True)
    st.sidebar.caption(f"Creator account · {st.session_state['user_name']}")
    creator_pages = ["Dashboard", "My Gigs", "Create Gig", "Orders", "Messages", "Earnings", "Analytics", "Profile", "Settings"]
    page_lookup = {"Dashboard": "creator_dashboard", "My Gigs": "creator_gigs", "Create Gig": "creator_create", "Orders": "creator_orders", "Messages": "creator_messages", "Earnings": "creator_earnings", "Analytics": "creator_analytics", "Profile": "creator_profile", "Settings": "creator_settings"}
    current = next((label for label, page in page_lookup.items() if page == st.session_state["page"]), "Dashboard")
    selected = st.sidebar.radio("Creator workspace", creator_pages, index=creator_pages.index(current))
    st.session_state["page"] = page_lookup[selected]
    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state.update(logged_in=False, user_role="", user_name="", user_email="", page="home")
        st.rerun()
    page = st.session_state["page"]
    if page == "creator_dashboard": render_creator_home()
    elif page == "creator_gigs": render_creator_gigs()
    elif page == "creator_create": render_creator_create()
    elif page == "creator_edit": render_creator_edit()
    elif page == "creator_orders": render_creator_orders()
    elif page == "creator_messages": render_creator_messages()
    elif page == "creator_earnings": render_creator_earnings()
    elif page == "creator_analytics": render_creator_analytics()
    elif page == "creator_profile": render_creator_profile()
    else: render_creator_settings()


def render_client_workspace() -> None:
    st.sidebar.markdown('<div class="wordmark"><span class="mark">T</span>TheHub</div>', unsafe_allow_html=True)
    st.sidebar.caption(f"Client account · {st.session_state['user_name']}")
    client_pages = ["Home", "Explore Gigs", "Categories", "My Orders", "Messages", "Saved Gigs", "My Profile", "Settings"]
    page_lookup = {"Home": "client_home", "Explore Gigs": "client_explore", "Categories": "client_explore", "My Orders": "client_orders", "Messages": "client_messages", "Saved Gigs": "client_saved", "My Profile": "client_profile", "Settings": "client_settings"}
    current = next((label for label, page in page_lookup.items() if page == st.session_state["page"]), "Home")
    selected = st.sidebar.radio("Client workspace", client_pages, index=client_pages.index(current))
    st.session_state["page"] = page_lookup[selected]
    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state.update(logged_in=False, user_role="", user_name="", user_email="", page="home")
        st.rerun()
    page = st.session_state["page"]
    if page == "client_home": render_client_home()
    elif page == "client_explore": render_client_explore()
    elif page == "client_gig": render_client_gig_detail()
    elif page == "client_orders": render_client_orders()
    elif page == "client_saved": render_client_saved()
    elif page == "client_messages": render_client_messages()
    elif page == "client_profile": render_client_profile()
    else: render_client_settings()


apply_styles()
render_theme_control()
if st.session_state["logged_in"]:
    if st.session_state.get("user_role") == "creator":
        render_creator_workspace()
    else:
        render_client_workspace()
elif st.session_state["page"] == "login":
    render_login()
elif st.session_state["page"] == "explore":
    render_explore()
elif st.session_state["page"] == "gig":
    render_gig_detail()
else:
    render_home()
