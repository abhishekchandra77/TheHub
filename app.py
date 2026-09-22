"""
TheHub — Creator Gig Marketplace (Streamlit frontend)
Works against server.py on http://localhost:8000/api
"""
import base64
import os
from html import escape
from typing import Any, Optional

import requests
import streamlit as st

API_BASE = os.getenv("API_URL", "http://localhost:8000/api")
PAGE_SIZE = 24
CATEGORIES = ["All", "Video & UGC", "Design & Graphics", "Writing & Translation", "Tech & AI", "Marketing", "Music & Audio", "Photography"]

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

DEMO_ACCOUNTS = {
    "creator@thehub.com": ("creator123", "creator", "Alex Rivera"),
    "maya@thehub.com": ("creator123", "creator", "Maya Chen"),
    "dev@thehub.com": ("creator123", "creator", "Dev Patel"),
    "client@thehub.com": ("client123", "client", "Ava Johnson"),
    "brand@acme.com": ("client123", "client", "Acme Brand"),
}

st.set_page_config(
    page_title="TheHub | Creator marketplace",
    page_icon="T",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DEFAULTS = {
    "theme": "light",
    "logged_in": False,
    "page": "home",
    "user_role": "",
    "user_name": "",
    "user_email": "",
    "selected_gig": None,
    "selected_order": None,
    "editing_gig": None,
    "flash_message": None,
    "delete_gig_id": None,
}
for k, v in DEFAULTS.items():
    st.session_state.setdefault(k, v)


# ---------------- API helpers ----------------

@st.cache_resource(show_spinner=False)
def http_session() -> requests.Session:
    return requests.Session()


def api_request(method: str, path: str, **kwargs: Any) -> tuple[Optional[Any], Optional[str]]:
    try:
        timeout = kwargs.pop("timeout", 6)
        r = http_session().request(method, f"{API_BASE}{path}", timeout=timeout, **kwargs)
        if r.ok:
            if r.status_code == 204 or not r.content:
                return {}, None
            try:
                return r.json(), None
            except ValueError:
                return {}, None
        try:
            detail = r.json().get("detail", "")
        except Exception:
            detail = ""
        return None, f"Request failed ({r.status_code}){': ' + str(detail) if detail else ''}."
    except requests.RequestException:
        return None, "The marketplace service is offline. Start the API on port 8000."


@st.cache_data(ttl=10, show_spinner=False)
def cached_get(path: str, params: tuple = ()) -> tuple[Optional[Any], Optional[str]]:
    return api_request("GET", path, params=dict(params))


def clear_cache():
    cached_get.clear()


def safe(v: Any) -> str:
    return escape(str(v))


def navigate(page: str) -> None:
    st.session_state["page"] = page
    st.rerun()


def flash(kind: str, message: str) -> None:
    st.session_state["flash_message"] = (kind, message)


def render_flash() -> None:
    msg = st.session_state.pop("flash_message", None)
    if not msg:
        return
    kind, text = msg
    if kind == "success":
        st.success(text)
    elif kind == "error":
        st.error(text)
    else:
        st.info(text)


# ---------------- Styles ----------------

def apply_styles() -> None:
    dark = st.session_state.get("theme") == "dark"
    c = {
        "bg": "#0c1424" if dark else "#f5f7fb",
        "surface": "#121e31" if dark else "#ffffff",
        "surface2": "#18283d" if dark else "#edf2f8",
        "text": "#f4f7fb" if dark else "#101827",
        "muted": "#a5b3c7" if dark else "#65748a",
        "line": "#2b3c55" if dark else "#dce3ed",
        "accent": "#5b5cf0",
        "accent2": "#746eff",
        "shadow": "rgba(4,14,30,.15)" if not dark else "rgba(0,0,0,.30)",
    }
    st.markdown(f"""
        <style>
        :root {{
            --bg:{c['bg']}; --surface:{c['surface']}; --surface-2:{c['surface2']};
            --text:{c['text']}; --muted:{c['muted']}; --line:{c['line']};
            --accent:{c['accent']}; --accent-2:{c['accent2']}; --shadow:{c['shadow']};
        }}
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
            background:var(--bg); color:var(--text); font-family:'DM Sans', sans-serif;
        }}
        [data-testid="stHeader"], [data-testid="stToolbar"] {{ visibility:hidden; height:0; }}
        .block-container {{ width:100%; max-width:1280px; padding:1rem clamp(1rem,4vw,3rem) 4rem; margin:0 auto; }}
        h1,h2,h3,h4 {{ color:var(--text) !important; font-family:'Manrope', sans-serif !important; letter-spacing:-.03em; }}
        p, label, [data-testid="stCaptionContainer"] {{ color:var(--muted); }}
        .nav-shell {{ display:flex; align-items:center; gap:1rem; padding:.65rem .9rem; margin-bottom:2rem;
            background:var(--surface); border:1px solid var(--line); border-radius:18px;
            box-shadow:0 8px 30px var(--shadow); }}
        .wordmark {{ color:var(--text); white-space:nowrap; font:800 1.38rem 'Manrope', sans-serif; letter-spacing:-.05em; }}
        .mark {{ display:inline-grid; place-items:center; width:29px; height:29px; margin-right:.42rem;
            color:white; background:linear-gradient(135deg,var(--accent),#9d71ff); border-radius:9px;
            font:800 .95rem 'Manrope', sans-serif; }}
        .eyebrow {{ color:var(--accent); font-size:.71rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; }}
        .hero {{ display:grid; grid-template-columns:minmax(0,1.08fr) minmax(320px,.92fr); gap:2rem;
            min-height:460px; padding:clamp(2rem,5vw,4rem); overflow:hidden;
            border:1px solid var(--line); border-radius:28px;
            background:radial-gradient(circle at 78% 20%, rgba(116,110,255,.16), transparent 31%),
                       linear-gradient(135deg,var(--surface),var(--surface-2));
            box-shadow:0 28px 70px var(--shadow); }}
        .hero h1 {{ max-width:700px; margin:.8rem 0 1.15rem; font-size:clamp(2.5rem,5.5vw,4.8rem); line-height:1.02; }}
        .hero h1 span {{ color:var(--accent); }}
        .hero-lead {{ max-width:590px; margin:0 0 1.8rem; font-size:1.08rem; line-height:1.7; }}
        .hero-note {{ color:var(--muted); font-size:.78rem; }}
        .hero-art {{ position:relative; min-height:320px; }}
        .stack-card {{ position:absolute; display:flex; flex-direction:column; justify-content:space-between;
            width:190px; height:130px; padding:1rem; border:1px solid rgba(255,255,255,.36);
            border-radius:18px; color:#151d31; background:linear-gradient(135deg,#fff,#e5eaff);
            box-shadow:0 28px 45px rgba(18,28,70,.25); }}
        .stack-card small {{ color:#67728b; font-weight:700; letter-spacing:.06em; text-transform:uppercase; font-size:.65rem; }}
        .stack-card strong {{ font:800 1.05rem 'Manrope', sans-serif; }}
        .stack-card.one {{ top:8%; left:14%; transform:rotate(-9deg); }}
        .stack-card.two {{ top:33%; right:4%; transform:rotate(8deg); background:linear-gradient(135deg,#e7e4ff,#cfd3ff); }}
        .stack-card.three {{ bottom:3%; left:22%; transform:rotate(5deg); background:linear-gradient(135deg,#e1fff4,#c4f2e5); }}
        .section {{ padding-top:4rem; }}
        .section-head {{ display:flex; align-items:end; justify-content:space-between; gap:1rem; margin-bottom:1.35rem; }}
        .section-head h2 {{ margin:.35rem 0 0; font-size:clamp(1.6rem,3vw,2.3rem); }}
        .section-head p {{ max-width:460px; margin:0; text-align:right; line-height:1.55; }}
        .category-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:1rem; }}
        .category-card {{ min-height:170px; padding:1.2rem; border:1px solid var(--line); border-radius:18px;
            background:var(--surface); box-shadow:0 10px 30px var(--shadow); transition:transform .2s; }}
        .category-card:hover {{ transform:translateY(-6px); border-color:var(--accent); }}
        .category-icon {{ display:grid; place-items:center; width:42px; height:42px; margin-bottom:1.2rem;
            border-radius:13px; font-weight:800; color:#fff; background:linear-gradient(135deg,var(--accent),#9a76ff); }}
        .category-icon.coral {{ background:linear-gradient(135deg,#f27d71,#e74f8c); }}
        .category-icon.mint {{ background:linear-gradient(135deg,#20ae9b,#55c978); }}
        .category-icon.blue {{ background:linear-gradient(135deg,#4286f4,#32c3db); }}
        .category-icon.gold {{ background:linear-gradient(135deg,#e19a3f,#e6c35c); }}
        .category-card h3 {{ margin:0 0 .45rem; font-size:1rem; }}
        .category-card p {{ margin:0; font-size:.84rem; line-height:1.5; }}
        .gig-card {{ display:flex; min-height:330px; flex-direction:column; overflow:hidden;
            border:1px solid var(--line); border-radius:18px; background:var(--surface);
            box-shadow:0 10px 30px var(--shadow); transition:transform .25s, box-shadow .25s; }}
        .gig-card:hover {{ transform:translateY(-6px); box-shadow:0 22px 44px var(--shadow); }}
        .gig-visual {{ display:flex; align-items:end; height:120px; padding:1rem; color:white;
            background:linear-gradient(135deg,#313b76,#8c75e9); }}
        .gig-visual.coral {{ background:linear-gradient(135deg,#7d354f,#f28b70); }}
        .gig-visual.mint {{ background:linear-gradient(135deg,#145968,#44c7a0); }}
        .gig-visual.blue {{ background:linear-gradient(135deg,#174a78,#4fc8df); }}
        .gig-visual.gold {{ background:linear-gradient(135deg,#8a6122,#e6c35c); }}
        .visual-word {{ opacity:.92; font:800 1.35rem 'Manrope', sans-serif; letter-spacing:-.04em; }}
        .gig-body {{ padding:1.1rem; }}
        .gig-meta {{ display:flex; align-items:center; justify-content:space-between; gap:.6rem;
            color:var(--muted); font-size:.77rem; }}
        .tag {{ display:inline-block; padding:.28rem .6rem; color:var(--accent);
            background:color-mix(in srgb, var(--accent) 11%, transparent); border-radius:99px;
            font-size:.7rem; font-weight:700; }}
        .gig-card h3 {{ margin:.7rem 0 .45rem; font-size:1rem; line-height:1.35; }}
        .gig-card p {{ min-height:44px; margin:0; font-size:.84rem; line-height:1.5; }}
        .gig-footer {{ display:flex; align-items:center; justify-content:space-between; padding:0 1.1rem 1.1rem; margin-top:auto; }}
        .avatar {{ display:inline-grid; place-items:center; width:30px; height:30px; margin-right:.45rem;
            color:#fff; background:linear-gradient(135deg,#111b35,#6475a6); border-radius:50%;
            font-size:.7rem; font-weight:700; }}
        .creator-line {{ display:flex; align-items:center; color:var(--muted); font-size:.78rem; }}
        .price {{ color:var(--text); font:800 1.05rem 'Manrope', sans-serif; }}
        .metric {{ padding:1.15rem; border:1px solid var(--line); border-radius:15px;
            background:var(--surface); box-shadow:0 9px 25px var(--shadow); }}
        .metric-label {{ color:var(--muted); font-size:.76rem; font-weight:600; letter-spacing:.04em; text-transform:uppercase; }}
        .metric-value {{ color:var(--text); margin-top:.35rem; font:800 1.7rem 'Manrope', sans-serif; }}
        .preview {{ padding:1.3rem; border:1px dashed var(--line); border-radius:17px; background:var(--surface-2); }}
        .status-pill {{ display:inline-block; padding:.3rem .8rem; border-radius:99px; font-size:.72rem; font-weight:700; }}
        .s-Pending {{ background:#fff3cd; color:#856404; }}
        .s-Accepted {{ background:#d1ecf1; color:#0c5460; }}
        .s-InProgress {{ background:#cce5ff; color:#004085; }}
        .s-Delivered {{ background:#e2d9f3; color:#4b2e83; }}
        .s-RevisionRequested {{ background:#ffe5d0; color:#8a4b08; }}
        .s-Completed {{ background:#d4edda; color:#155724; }}
        .s-Declined, .s-Cancelled {{ background:#f8d7da; color:#721c24; }}
        .timeline {{ display:flex; gap:.4rem; align-items:center; margin:.5rem 0 1rem; flex-wrap:wrap; }}
        .timeline-step {{ padding:.35rem .8rem; border-radius:99px; font-size:.72rem; font-weight:700;
            background:var(--surface-2); color:var(--muted); border:1px solid var(--line); }}
        .timeline-step.done {{ background:var(--accent); color:white; border-color:var(--accent); }}
        .timeline-step.current {{ background:color-mix(in srgb, var(--accent) 20%, transparent);
            color:var(--accent); border-color:var(--accent); }}
        .cta {{ display:flex; align-items:center; justify-content:space-between; gap:2rem;
            overflow:hidden; margin-top:4rem; padding:3rem clamp(1.4rem,4vw,4rem); border-radius:24px;
            background:linear-gradient(120deg,#252a67,#5750c5 60%,#8670ed); color:white; }}
        .cta h2, .cta p {{ color:white !important; }}
        .cta h2 {{ margin:.45rem 0 .6rem; font-size:clamp(1.6rem,2.8vw,2.4rem); }}
        .cta p {{ max-width:510px; margin:0; opacity:.85; }}
        .footer {{ display:grid; grid-template-columns:2fr repeat(3,1fr); gap:2rem;
            margin-top:4rem; padding-top:2rem; border-top:1px solid var(--line);
            color:var(--muted); font-size:.82rem; }}
        .footer strong {{ color:var(--text); font:800 1.2rem 'Manrope', sans-serif; }}
        .footer h4 {{ margin:0 0 .7rem; font-size:.8rem; }}
        .footer p {{ margin:.3rem 0; }}
        .deliverable {{ padding:1rem; border:1px solid var(--line); border-radius:12px;
            background:var(--surface-2); margin-bottom:.6rem; }}
        .deliverable h4 {{ margin:.1rem 0 .4rem; font-size:.95rem; }}
        .stButton > button, .stFormSubmitButton > button {{
            min-height:2.5rem; border:1px solid var(--line); border-radius:10px;
            background:var(--surface); color:var(--text); font-weight:700;
            transition:transform .15s, border-color .15s, background .15s; }}
        .stButton > button:hover, .stFormSubmitButton > button:hover {{
            transform:translateY(-1px); border-color:var(--accent); color:var(--accent); }}
        .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
            color:white; border-color:var(--accent); background:var(--accent); }}
        .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {{
            color:white; background:var(--accent-2); }}
        input, textarea, [data-baseweb="select"] > div {{
            background:var(--surface) !important; color:var(--text) !important;
            border-color:var(--line) !important; }}
        [data-testid="stSidebar"] {{ background:var(--surface); border-right:1px solid var(--line); }}
        @media (max-width:900px) {{
            .hero {{ grid-template-columns:1fr; }}
            .hero-art {{ display:none; }}
            .category-grid, .gig-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
        }}
        @media (max-width:620px) {{
            .block-container {{ padding:1rem 1rem 3rem; }}
            .category-grid, .gig-grid {{ grid-template-columns:1fr; }}
            .cta {{ display:block; padding:2rem 1.3rem; }}
            .footer {{ grid-template-columns:1fr 1fr; }}
        }}
        </style>
    """, unsafe_allow_html=True)


# ---------------- Shared UI ----------------

def category_class(category: str) -> str:
    for name, _, _, color in CATEGORY_CARDS:
        if name == category:
            return color
    mapping = {
        "Video & UGC": "coral",
        "Design & Graphics": "mint",
        "Writing & Translation": "blue",
        "Tech & AI": "violet",
    }
    return mapping.get(category, "violet")


def status_class(status: str) -> str:
    return "s-" + status.replace(" ", "")


def render_nav(authenticated: bool = False) -> None:
    cols = st.columns([1.6, 1, 1, 1.05, 1.2, 1.1, 1.1] if not authenticated else [1.6, 1, 1, 1, 1.2])
    with cols[0]:
        st.markdown('<div class="nav-shell"><div class="wordmark"><span class="mark">T</span>TheHub</div></div>',
                    unsafe_allow_html=True)
    links = [(1, "Home", "home"), (2, "Explore", "explore")]
    for i, label, page in links:
        with cols[i]:
            if st.button(label, key=f"nav_{label}", use_container_width=True):
                navigate(page)
    if not authenticated:
        with cols[3]:
            if st.button("Become a Creator", key="nav_become", use_container_width=True):
                navigate("login")
        with cols[4]:
            if st.button("Login", key="nav_login", use_container_width=True):
                navigate("login")
        with cols[5]:
            if st.button("Sign Up", key="nav_signup", type="primary", use_container_width=True):
                navigate("login")
        with cols[6]:
            if st.button("Post a Gig", key="nav_post", use_container_width=True):
                navigate("login")


def render_footer() -> None:
    st.markdown("""
        <footer class="footer">
            <div><strong>TheHub</strong><p>A more human marketplace for ambitious work.</p></div>
            <div><h4>Marketplace</h4><p>Explore Gigs</p><p>Categories</p></div>
            <div><h4>For creators</h4><p>Post a Gig</p><p>How It Works</p></div>
            <div><h4>Support</h4><p>Privacy</p><p>Terms</p></div>
        </footer>
    """, unsafe_allow_html=True)


def render_gig_card(gig: dict, key_prefix: str, on_click_page: str = "gig") -> None:
    category = safe(gig.get("category", "Creator service"))
    title = safe(gig.get("title", "Untitled gig"))
    creator = safe(gig.get("creator_name", "Creator"))
    description = safe(gig.get("description", ""))[:160]
    initials = "".join(p[0] for p in creator.split()[:2]).upper() or "C"
    color = category_class(gig.get("category", ""))
    rating = gig.get("rating") or 0
    review_count = gig.get("review_count") or 0
    rating_text = f"★ {rating:.1f} ({review_count})" if review_count else "New"
    st.markdown(f"""
        <div class="gig-card">
            <div class="gig-visual {color}"><span class="visual-word">{category}</span></div>
            <div class="gig-body">
                <div class="gig-meta"><span class="tag">{category}</span><span>{rating_text}</span></div>
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
            <div class="gig-footer">
                <span class="creator-line"><span class="avatar">{initials}</span>{creator}</span>
                <span class="price">From ${float(gig.get('rate', 0)):.0f}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("View gig", key=f"{key_prefix}_{gig['id']}", use_container_width=True):
        st.session_state["selected_gig"] = gig
        navigate(on_click_page)


def render_metric(label: str, value: Any) -> None:
    st.markdown(
        f'<div class="metric"><div class="metric-label">{safe(label)}</div>'
        f'<div class="metric-value">{safe(value)}</div></div>',
        unsafe_allow_html=True,
    )


def render_status_pill(status: str) -> str:
    return f'<span class="status-pill {status_class(status)}">{safe(status)}</span>'


# ---------------- Public pages ----------------

def render_home() -> None:
    render_nav()
    render_flash()
    st.markdown("""
        <section class="hero">
            <div>
                <div class="eyebrow">The creator marketplace for modern teams</div>
                <h1>Turn Your Skills Into <span>Opportunities.</span></h1>
                <p class="hero-lead">Discover talented creators, order their services, and collaborate end-to-end on TheHub.</p>
                <span class="hero-note">A thoughtful network for work with a point of view.</span>
            </div>
            <div class="hero-art">
                <div class="stack-card one"><small>Creator profile</small><strong>Visual identity</strong></div>
                <div class="stack-card two"><small>New opportunity</small><strong>AI workflow</strong></div>
                <div class="stack-card three"><small>Live project</small><strong>Launch campaign</strong></div>
            </div>
        </section>
    """, unsafe_allow_html=True)

    s1, s2, s3 = st.columns([2.4, 1.25, .85])
    with s1:
        search = st.text_input("Search", placeholder="What are you looking for?", label_visibility="collapsed", key="home_search")
    with s2:
        category = st.selectbox("Category", CATEGORIES, label_visibility="collapsed", key="home_category")
    with s3:
        if st.button("Search", type="primary", use_container_width=True):
            st.session_state["explore_search"] = search
            st.session_state["category_filter"] = category
            navigate("explore")

    explore_col, sell_col = st.columns(2)
    with explore_col:
        if st.button("Explore Gigs", type="primary", use_container_width=True):
            navigate("explore")
    with sell_col:
        if st.button("Start Selling", use_container_width=True):
            navigate("login")

    # Categories
    st.markdown('<section class="section"><div class="section-head"><div>'
                '<div class="eyebrow">Browse by expertise</div><h2>Find the right specialist</h2>'
                '</div><p>Explore a focused network of people who make ambitious work happen.</p></div>',
                unsafe_allow_html=True)
    for row_start in range(0, len(CATEGORY_CARDS), 4):
        columns = st.columns(4)
        for col, (name, icon, copy, color) in zip(columns, CATEGORY_CARDS[row_start:row_start + 4]):
            with col:
                st.markdown(
                    f'<div class="category-card"><div class="category-icon {color}">{icon}</div>'
                    f'<h3>{name}</h3><p>{copy}</p></div>',
                    unsafe_allow_html=True,
                )
                if st.button("Explore", key=f"home_cat_{name}", use_container_width=True):
                    st.session_state["category_filter"] = CATEGORY_API_MAP.get(name, name)
                    navigate("explore")
    st.markdown('</section>', unsafe_allow_html=True)

    # Featured gigs
    st.markdown('<section class="section"><div class="section-head"><div>'
                '<div class="eyebrow">Fresh on TheHub</div><h2>Explore what creators are offering</h2>'
                '</div><p>Real services from the marketplace, ready for your next brief.</p></div>',
                unsafe_allow_html=True)
    gigs, err = cached_get("/gigs", (("limit", "6"), ("sort_by", "newest")))
    if err:
        st.warning(err)
    elif gigs:
        for row_start in range(0, min(len(gigs), 6), 3):
            columns = st.columns(3)
            for col, gig in zip(columns, gigs[row_start:row_start + 3]):
                with col:
                    render_gig_card(gig, "featured")
    st.markdown('</section>', unsafe_allow_html=True)

    # CTA
    st.markdown('<section class="cta"><div>'
                '<div class="eyebrow" style="color:#b8b9ff">For creators</div>'
                '<h2>Your Skill Could Be Someone\'s Next Solution.</h2>'
                '<p>Create your first gig and put your skills in front of people who need them.</p>'
                '</div>', unsafe_allow_html=True)
    if st.button("Create Your Gig", key="creator_cta", type="primary"):
        navigate("login")
    st.markdown('</section>', unsafe_allow_html=True)
    render_footer()


def render_explore() -> None:
    render_nav()
    render_flash()
    st.markdown('<div class="section-head"><div><div class="eyebrow">The marketplace</div>'
                '<h1>Explore Gigs</h1><p>Compare services from creators ready to help you move faster.</p>'
                '</div></div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([2, 1.2, 1, 1.2])
    with c1:
        search = st.text_input("Search", value=st.session_state.pop("explore_search", ""),
                               placeholder="Try branding or automation")
    with c2:
        default_cat = st.session_state.pop("category_filter", "All")
        category = st.selectbox("Category", CATEGORIES,
                                index=CATEGORIES.index(default_cat) if default_cat in CATEGORIES else 0)
    with c3:
        max_price = st.number_input("Max price", min_value=0, value=0, step=25, help="0 for any price.")
    with c4:
        sort_label = st.selectbox("Sort by", ["Newest", "Price: Low to High", "Price: High to Low", "Top rated"])

    params = {"limit": str(PAGE_SIZE),
              "sort_by": {"Newest": "newest", "Price: Low to High": "cheapest",
                          "Price: High to Low": "priciest", "Top rated": "rating"}[sort_label]}
    if search.strip():
        params["search"] = search.strip()
    if category != "All":
        params["category"] = CATEGORY_API_MAP.get(category, category)

    gigs, err = cached_get("/gigs", tuple(sorted(params.items())))
    if err:
        st.error(err)
        return
    if max_price:
        gigs = [g for g in gigs if float(g.get("rate", 0)) <= max_price]
    st.caption(f"{len(gigs)} service(s) available")
    if not gigs:
        st.info("No gigs match these filters.")
        return
    for row_start in range(0, len(gigs), 3):
        columns = st.columns(3)
        for col, gig in zip(columns, gigs[row_start:row_start + 3]):
            with col:
                render_gig_card(gig, "explore")


def render_public_gig() -> None:
    render_nav()
    render_flash()
    gig = st.session_state.get("selected_gig")
    if not gig:
        navigate("explore")
    latest, _ = cached_get(f"/gigs/{gig['id']}")
    gig = latest or gig

    st.markdown(f'<div class="eyebrow">{safe(gig["category"])}</div>'
                f'<h1>{safe(gig["title"])}</h1>'
                f'<p>Created by <strong>{safe(gig["creator_name"])}</strong></p>',
                unsafe_allow_html=True)

    left, right = st.columns([1.7, 1])
    with left:
        st.markdown(f'<div class="preview">'
                    f'<h3>About this gig</h3><p>{safe(gig["description"])}</p>'
                    f'<h4>Deliverables</h4><p>{safe(gig.get("deliverables") or "To be confirmed with the creator.")}</p>'
                    f'<h4>Delivery time</h4><p>{safe(gig.get("delivery_time") or "To be agreed")}</p>'
                    f'<div class="price">Starting at ${float(gig["rate"]):.2f}</div></div>',
                    unsafe_allow_html=True)
        reviews, _ = cached_get(f"/gigs/{gig['id']}/reviews")
        if reviews:
            st.markdown("### Reviews")
            for r in reviews[:5]:
                st.markdown(f"**{'★' * int(r['rating'])}{'☆' * (5 - int(r['rating']))}** — {safe(r['comment'] or 'No comment')}")
                st.caption(f"— {safe(r['client_name'])}")
    with right:
        if not st.session_state["logged_in"]:
            st.info("Log in as a client to place an order.")
            if st.button("Login to order", type="primary", use_container_width=True):
                navigate("login")
        elif st.session_state["user_role"] != "client":
            st.info("Switch to a client account to place orders.")
        else:
            with st.form(f"order_form_{gig['id']}"):
                st.subheader("Place an order")
                requirements = st.text_area("Project brief", placeholder="Describe what you need...")
                delivery_date = st.text_input("Preferred delivery date", placeholder="2026-10-15")
                amount = st.number_input("Offer (USD)", min_value=1.0,
                                         value=float(gig.get("rate", 0) or 1), step=5.0)
                submitted = st.form_submit_button("Send order request", type="primary", use_container_width=True)
                if submitted:
                    if not requirements.strip():
                        st.error("Add a project brief.")
                    else:
                        payload = {
                            "gig_id": gig["id"],
                            "client_name": st.session_state["user_name"],
                            "client_email": st.session_state["user_email"],
                            "requirements": requirements.strip(),
                            "delivery_date": delivery_date.strip() or None,
                            "amount": float(amount),
                        }
                        _, err = api_request("POST", "/orders", json=payload)
                        if err:
                            st.error(err)
                        else:
                            clear_cache()
                            flash("success", f"✓ Order sent to {gig['creator_name']}.")
                            navigate("client_orders")
    if st.button("← Back"):
        navigate("explore")


def render_login() -> None:
    render_nav()
    render_flash()
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown('<div class="eyebrow">Welcome to TheHub</div>'
                    '<h1>Bring your next idea to life.</h1>'
                    '<p class="hero-lead">Sign in with a demo account to explore the full workflow.</p>',
                    unsafe_allow_html=True)
    with right:
        st.markdown('<div class="preview">', unsafe_allow_html=True)
        st.subheader("Sign in")
        role = st.radio("I am a", ["Creator", "Client"], horizontal=True)
        email = st.text_input("Email", placeholder="creator@thehub.com")
        password = st.text_input("Password", type="password")
        if st.button("Continue", type="primary", use_container_width=True):
            account = DEMO_ACCOUNTS.get(email.strip().lower())
            if account and account[0] == password and account[1] == role.lower():
                st.session_state.update(
                    logged_in=True,
                    user_role=account[1],
                    user_name=account[2],
                    user_email=email.strip().lower(),
                    page="creator_dashboard" if account[1] == "creator" else "client_home",
                )
                st.rerun()
            else:
                st.error("Incorrect credentials or role mismatch.")
        st.caption("Demo accounts")
        st.code("creator@thehub.com / creator123\nmaya@thehub.com / creator123\nclient@thehub.com / client123\nbrand@acme.com / client123")
        st.markdown('</div>', unsafe_allow_html=True)


# ---------------- Creator workspace ----------------

CREATOR_PAGES = ["Dashboard", "My Gigs", "Create Gig", "Orders", "Gig Analytics",
                 "Messages", "Earnings", "Reviews", "Profile", "Settings"]
CREATOR_PAGE_MAP = {
    "Dashboard": "creator_dashboard",
    "My Gigs": "creator_gigs",
    "Create Gig": "creator_create",
    "Orders": "creator_orders",
    "Gig Analytics": "creator_analytics",
    "Messages": "creator_messages",
    "Earnings": "creator_earnings",
    "Reviews": "creator_reviews",
    "Profile": "creator_profile",
    "Settings": "creator_settings",
}


def render_creator_dashboard() -> None:
    data, err = cached_get("/creator/dashboard", (("creator_email", st.session_state["user_email"]),))
    if err:
        st.error(err)
        return
    st.markdown('<div class="eyebrow">Creator workspace</div>'
                f'<h1>Welcome back, {safe(st.session_state["user_name"].split()[0])}.</h1>'
                '<p>Your storefront, orders, and earnings at a glance.</p>',
                unsafe_allow_html=True)

    cols = st.columns(4)
    with cols[0]: render_metric("Active Gigs", f"{data['active_gigs']} / {data['total_gigs']}")
    with cols[1]: render_metric("Pending Orders", data["pending_orders"])
    with cols[2]: render_metric("Completed", data["completed_orders"])
    with cols[3]: render_metric("Total Earnings", f"${data['total_earnings']:,.0f}")

    cols = st.columns(4)
    with cols[0]: render_metric("Total Orders", data["total_orders"])
    with cols[1]: render_metric("In Progress", data["active_orders"])
    with cols[2]: render_metric("Gig Views", data["total_views"])
    with cols[3]: render_metric("Avg Rating", f"{data['avg_rating']:.2f} ★" if data["avg_rating"] else "—")

    st.markdown("### Recent orders")
    orders, err = cached_get("/orders", (("actor_email", st.session_state["user_email"]),
                                         ("actor_role", "creator"), ("limit", "6")))
    if err:
        st.warning(err)
    elif not orders:
        st.info("No orders yet. Share your gigs to attract clients.")
    else:
        for o in orders:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1.4, 1])
                with c1:
                    st.markdown(f"**#{o['id']} · {safe(o['gig_title'])}**")
                    st.caption(f"Client: {safe(o['client_name'])} · Amount: ${float(o['amount']):.2f}")
                with c2:
                    st.markdown(render_status_pill(o["status"]), unsafe_allow_html=True)
                with c3:
                    if st.button("Open", key=f"cd_open_{o['id']}", use_container_width=True):
                        st.session_state["selected_order"] = o
                        navigate("creator_order_detail")


def render_creator_gigs() -> None:
    st.markdown('<div class="eyebrow">Creator catalog</div><h1>My Gigs</h1>'
                '<p>Manage the services you offer on TheHub.</p>', unsafe_allow_html=True)
    gigs, err = cached_get("/creator/gigs", (("creator_email", st.session_state["user_email"]),))
    if err:
        st.error(err)
        return
    if not gigs:
        st.info("You have not published a gig yet.")
        if st.button("Create your first gig", type="primary"):
            navigate("creator_create")
        return
    for gig in gigs:
        with st.container(border=True):
            c1, c2, c3 = st.columns([2.6, 1.2, 1.4])
            with c1:
                st.markdown(f"### {safe(gig['title'])}")
                st.caption(f"{safe(gig['category'])} · Status: {safe(gig.get('status', 'Active'))}")
                st.write(safe(gig["description"])[:220])
            with c2:
                render_metric("Price", f"${float(gig['rate']):.0f}")
                st.caption(f"Views: {gig.get('views', 0)} · Rating: {gig.get('rating') or '—'}")
            with c3:
                if st.button("View", key=f"cg_view_{gig['id']}", use_container_width=True):
                    st.session_state["selected_gig"] = gig
                    navigate("gig")
                if st.button("Edit", key=f"cg_edit_{gig['id']}", use_container_width=True):
                    st.session_state["editing_gig"] = gig
                    navigate("creator_edit")
                if st.button("Delete", key=f"cg_del_{gig['id']}", use_container_width=True):
                    st.session_state["delete_gig_id"] = gig["id"]
                    st.rerun()
                if st.session_state.get("delete_gig_id") == gig["id"]:
                    st.warning("Delete permanently?")
                    d1, d2 = st.columns(2)
                    with d1:
                        if st.button("Confirm", key=f"cg_del_ok_{gig['id']}", type="primary"):
                            _, e = api_request("DELETE", f"/gigs/{gig['id']}",
                                               params={"owner_email": st.session_state["user_email"]})
                            if e: st.error(e)
                            else:
                                st.session_state["delete_gig_id"] = None
                                clear_cache()
                                st.rerun()
                    with d2:
                        if st.button("Cancel", key=f"cg_del_no_{gig['id']}"):
                            st.session_state["delete_gig_id"] = None
                            st.rerun()


def render_creator_create() -> None:
    st.markdown('<div class="eyebrow">Creator tools</div><h1>Post a Gig</h1>'
                '<p>Give clients a clear reason to choose you.</p>', unsafe_allow_html=True)
    left, right = st.columns([1.15, .85])
    with left:
        with st.form("post_gig_form", clear_on_submit=True):
            creator = st.text_input("Creator name", value=st.session_state.get("user_name", ""))
            title = st.text_input("Service title")
            category = st.selectbox("Category", CATEGORIES[1:])
            rate = st.number_input("Starting price (USD)", min_value=1.0, value=75.0, step=5.0)
            deliverables = st.text_input("Deliverables", placeholder="e.g. 3 concepts, source files")
            delivery_time = st.text_input("Delivery time", placeholder="e.g. 3 days")
            skills = st.text_input("Skills", placeholder="React, Figma, SEO")
            thumbnail_url = st.text_input("Optional thumbnail URL", placeholder="https://...")
            description = st.text_area("What will you deliver?")
            submitted = st.form_submit_button("Publish gig", type="primary", use_container_width=True)
            if submitted:
                if not creator.strip() or not title.strip() or not description.strip():
                    st.error("Fill in creator name, title, and description.")
                else:
                    payload = {
                        "creator_name": creator.strip(),
                        "owner_email": st.session_state["user_email"],
                        "title": title.strip(),
                        "category": category,
                        "rate": float(rate),
                        "description": description.strip(),
                        "deliverables": deliverables.strip(),
                        "delivery_time": delivery_time.strip(),
                        "skills": skills.strip(),
                        "thumbnail_url": thumbnail_url.strip(),
                    }
                    _, e = api_request("POST", "/gigs", json=payload)
                    if e:
                        st.error(e)
                    else:
                        clear_cache()
                        flash("success", "✓ Gig is live on TheHub.")
                        navigate("creator_gigs")
    with right:
        st.markdown("#### Live preview")
        st.markdown(
            f'<div class="preview"><span class="tag">{safe(category if "category" in locals() else "Video & UGC")}</span>'
            f'<h3>{safe(title if "title" in locals() and title else "Your service title")}</h3>'
            f'<div class="creator-line">By {safe(creator if "creator" in locals() else st.session_state["user_name"])}</div>'
            f'<p>{safe(description if "description" in locals() and description else "Your service description appears here.")}</p>'
            f'<div class="price">From ${float(rate) if "rate" in locals() else 75:.0f}</div></div>',
            unsafe_allow_html=True,
        )


def render_creator_edit() -> None:
    gig = st.session_state.get("editing_gig")
    if not gig:
        navigate("creator_gigs")
    st.markdown('<div class="eyebrow">Creator catalog</div><h1>Edit Gig</h1>'
                '<p>Keep your listing accurate.</p>', unsafe_allow_html=True)
    with st.form(f"edit_gig_{gig['id']}"):
        title = st.text_input("Gig title", value=gig.get("title", ""))
        cat_opts = CATEGORIES[1:]
        category = st.selectbox("Category", cat_opts,
                                index=cat_opts.index(gig.get("category")) if gig.get("category") in cat_opts else 0)
        description = st.text_area("Description", value=gig.get("description", ""))
        deliverables = st.text_input("Deliverables", value=gig.get("deliverables", "") or "")
        delivery_time = st.text_input("Delivery time", value=gig.get("delivery_time", "") or "")
        skills = st.text_input("Skills", value=gig.get("skills", "") or "")
        thumbnail_url = st.text_input("Thumbnail URL", value=gig.get("thumbnail_url", "") or "")
        rate = st.number_input("Price", min_value=1.0, value=float(gig.get("rate", 75)), step=5.0)
        status = st.selectbox("Status", ["Active", "Paused", "Draft"],
                              index=["Active", "Paused", "Draft"].index(gig.get("status", "Active"))
                              if gig.get("status", "Active") in ["Active", "Paused", "Draft"] else 0)
        submitted = st.form_submit_button("Save changes", type="primary")
        if submitted:
            payload = {
                "owner_email": st.session_state["user_email"],
                "title": title.strip(),
                "category": category,
                "description": description.strip(),
                "deliverables": deliverables.strip(),
                "delivery_time": delivery_time.strip(),
                "skills": skills.strip(),
                "thumbnail_url": thumbnail_url.strip(),
                "rate": float(rate),
                "status": status,
            }
            _, e = api_request("PATCH", f"/gigs/{gig['id']}", json=payload)
            if e:
                st.error(e)
            else:
                clear_cache()
                st.session_state["editing_gig"] = None
                flash("success", "✓ Gig updated.")
                navigate("creator_gigs")
    if st.button("Back to My Gigs"):
        navigate("creator_gigs")


def render_creator_orders() -> None:
    st.markdown('<div class="eyebrow">Order management</div><h1>Orders</h1>'
                '<p>Accept, work on, and deliver every client project.</p>', unsafe_allow_html=True)
    filter_status = st.selectbox("Filter by status",
                                 ["All"] + ["Pending", "Accepted", "In Progress", "Delivered",
                                            "Revision Requested", "Completed", "Declined", "Cancelled"])
    params = [("actor_email", st.session_state["user_email"]), ("actor_role", "creator"), ("limit", "100")]
    if filter_status != "All":
        params.append(("status", filter_status))
    orders, err = cached_get("/orders", tuple(params))
    if err:
        st.error(err)
        return
    if not orders:
        st.info("No orders yet.")
        return
    for o in orders:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1.4, 1])
            with c1:
                st.markdown(f"### #{o['id']} · {safe(o['gig_title'])}")
                st.caption(f"Client: {safe(o['client_name'])} · Amount: ${float(o['amount']):.2f}")
                st.write(safe(o["requirements"])[:220])
            with c2:
                st.markdown(render_status_pill(o["status"]), unsafe_allow_html=True)
                if o.get("rejection_reason"):
                    st.caption(f"Reason: {safe(o['rejection_reason'])}")
            with c3:
                if st.button("Open", key=f"co_open_{o['id']}", type="primary", use_container_width=True):
                    st.session_state["selected_order"] = o
                    navigate("creator_order_detail")


def render_creator_order_detail() -> None:
    order = st.session_state.get("selected_order")
    if not order:
        navigate("creator_orders")
    data, err = cached_get(f"/orders/{order['id']}")
    if err:
        st.error(err)
        return
    order = data
    st.markdown(f'<div class="eyebrow">Order #{order["id"]}</div>'
                f'<h1>{safe(order["gig_title"])}</h1>'
                f'<p>Client: <strong>{safe(order["client_name"])}</strong> · '
                f'Amount: <strong>${float(order["amount"]):.2f}</strong></p>',
                unsafe_allow_html=True)
    st.markdown(render_status_pill(order["status"]), unsafe_allow_html=True)

    # Timeline
    steps = ["Pending", "Accepted", "In Progress", "Delivered", "Completed"]
    st.markdown('<div class="timeline">' + "".join(
        f'<span class="timeline-step {"done" if order["status"] == s else ""}">{s}</span>' for s in steps
    ) + '</div>', unsafe_allow_html=True)

    if order["status"] == "Declined" and order.get("rejection_reason"):
        st.error(f"Declined — reason: {order['rejection_reason']}")
    if order["status"] == "Revision Requested":
        st.warning("Client requested a revision.")

    left, right = st.columns([1.4, 1])
    with left:
        st.markdown("#### Project brief")
        st.write(order["requirements"])
        if order.get("delivery_date"):
            st.caption(f"Requested delivery: {order['delivery_date']}")

        st.markdown("#### Uploaded work")
        if order.get("deliverables"):
            for d in order["deliverables"]:
                with st.container(border=True):
                    st.markdown(f"**{safe(d['title'])}**")
                    if d.get("description"):
                        st.write(safe(d["description"]))
                    if d.get("file_url"):
                        if d["file_url"].startswith("data:"):
                            st.info("📎 File attached (data URL). Download by copying the source.")
                            with st.expander("Show data URL"):
                                st.code(d["file_url"][:300] + "...")
                        else:
                            st.markdown(f"[🔗 Open attachment]({d['file_url']})")
                    st.caption(f"Uploaded {safe(d['created_at'][:19])}")
        else:
            st.info("No work uploaded yet.")
    with right:
        st.markdown("#### Actions")
        if order["status"] == "Pending":
            if st.button("Accept order", type="primary", use_container_width=True):
                _, e = api_request("PATCH", f"/orders/{order['id']}/status",
                                   json={"actor_email": st.session_state["user_email"],
                                         "actor_role": "creator", "status": "Accepted"})
                if e: st.error(e)
                else:
                    clear_cache()
                    flash("success", "✓ Order accepted.")
                    st.rerun()
            with st.expander("Decline"):
                reason = st.text_input("Reason for declining", key=f"decline_{order['id']}")
                if st.button("Confirm decline", key=f"decline_ok_{order['id']}"):
                    _, e = api_request("PATCH", f"/orders/{order['id']}/status",
                                       json={"actor_email": st.session_state["user_email"],
                                             "actor_role": "creator", "status": "Declined",
                                             "rejection_reason": reason.strip()})
                    if e: st.error(e)
                    else:
                        clear_cache()
                        flash("success", "Order declined.")
                        st.rerun()
        elif order["status"] == "Accepted":
            if st.button("Start work", type="primary", use_container_width=True):
                _, e = api_request("PATCH", f"/orders/{order['id']}/status",
                                   json={"actor_email": st.session_state["user_email"],
                                         "actor_role": "creator", "status": "In Progress"})
                if e: st.error(e)
                else:
                    clear_cache()
                    st.rerun()
        elif order["status"] == "Revision Requested":
            if st.button("Resume work", type="primary", use_container_width=True):
                _, e = api_request("PATCH", f"/orders/{order['id']}/status",
                                   json={"actor_email": st.session_state["user_email"],
                                         "actor_role": "creator", "status": "In Progress"})
                if e: st.error(e)
                else:
                    clear_cache()
                    st.rerun()

    if order["status"] in ("In Progress", "Revision Requested"):
        st.markdown("### Upload work")
        with st.form(f"upload_{order['id']}"):
            d_title = st.text_input("Deliverable title", placeholder="e.g. Final brand kit")
            d_desc = st.text_area("Description", placeholder="What did you deliver?")
            d_url = st.text_input("Link (optional)", placeholder="https://drive.google.com/...")
            up = st.file_uploader("Or attach a file (max 2MB)",
                                  type=["png", "jpg", "jpeg", "gif", "pdf", "zip", "txt", "md", "mp4"])
            submit = st.form_submit_button("Upload deliverable", type="primary", use_container_width=True)
            if submit:
                if not d_title.strip():
                    st.error("Add a title.")
                else:
                    file_url = d_url.strip()
                    if up is not None:
                        if up.size > 2 * 1024 * 1024:
                            st.error("File too large (2MB max). Use a link instead.")
                            file_url = ""
                            up = None
                        else:
                            b64 = base64.b64encode(up.getvalue()).decode()
                            file_url = f"data:{up.type};base64,{b64}"
                    if not file_url:
                        st.error("Provide a link or attach a file.")
                    else:
                        payload = {"creator_email": st.session_state["user_email"],
                                   "title": d_title.strip(),
                                   "description": d_desc.strip(),
                                   "file_url": file_url}
                        _, e = api_request("POST", f"/orders/{order['id']}/deliverables", json=payload)
                        if e:
                            st.error(e)
                        else:
                            clear_cache()
                            flash("success", "✓ Deliverable uploaded.")
                            st.rerun()

    if order["status"] == "In Progress" and order.get("deliverables"):
        if st.button("Mark as Delivered", type="primary", use_container_width=True):
            _, e = api_request("PATCH", f"/orders/{order['id']}/status",
                               json={"actor_email": st.session_state["user_email"],
                                     "actor_role": "creator", "status": "Delivered"})
            if e: st.error(e)
            else:
                clear_cache()
                flash("success", "✓ Marked as delivered.")
                st.rerun()

    st.markdown("#### Messages with client")
    msgs, _ = cached_get("/messages", (("user_email", st.session_state["user_email"]),
                                       ("order_id", str(order["id"]))))
    if msgs:
        for m in msgs:
            who = "You" if m["sender_email"] == st.session_state["user_email"] else "Client"
            st.markdown(f"**{who}:** {safe(m['message'])}")
    new_msg = st.text_input("Send a message", key=f"msg_{order['id']}")
    if st.button("Send", key=f"msg_send_{order['id']}"):
        if new_msg.strip():
            _, e = api_request("POST", "/messages", json={
                "sender_email": st.session_state["user_email"],
                "receiver_email": order["client_email"],
                "message": new_msg.strip(),
                "order_id": order["id"],
            })
            if e: st.error(e)
            else:
                clear_cache()
                st.rerun()

    if st.button("← Back to orders"):
        navigate("creator_orders")


def render_creator_analytics() -> None:
    st.markdown('<div class="eyebrow">Performance</div><h1>Gig Analytics</h1>'
                '<p>Per-gig breakdown of orders, revenue, and engagement.</p>', unsafe_allow_html=True)
    data, err = cached_get("/creator/dashboard", (("creator_email", st.session_state["user_email"]),))
    if err:
        st.error(err)
        return
    per_gig = data.get("per_gig", [])
    if not per_gig:
        st.info("Publish a gig to see analytics.")
        return
    for g in per_gig:
        with st.container(border=True):
            st.markdown(f"### {safe(g['title'])}")
            st.caption(f"{safe(g['category'])} · Status: {safe(g['status'])}")
            c = st.columns(5)
            with c[0]: render_metric("Views", g["views"])
            with c[1]: render_metric("Orders", g["orders"])
            with c[2]: render_metric("Completed", g["completed"])
            with c[3]: render_metric("Revenue", f"${g['revenue']:,.0f}")
            with c[4]: render_metric("Rating", f"{g['rating']:.1f} ★" if g["review_count"] else "—")


def render_creator_messages() -> None:
    st.markdown('<div class="eyebrow">Communication</div><h1>Messages</h1>'
                '<p>Conversations with your clients.</p>', unsafe_allow_html=True)
    msgs, err = cached_get("/messages", (("user_email", st.session_state["user_email"]),))
    if err:
        st.error(err)
        return
    if not msgs:
        st.info("No messages yet. Conversations start when you contact clients on an order.")
    for m in msgs or []:
        with st.container(border=True):
            st.caption(f"{safe(m['sender_email'])} → {safe(m['receiver_email'])} · {safe(m['created_at'][:19])}")
            st.write(safe(m["message"]))


def render_creator_earnings() -> None:
    st.markdown('<div class="eyebrow">Financial overview</div><h1>Earnings</h1>'
                '<p>Track your revenue across orders.</p>', unsafe_allow_html=True)
    data, err = cached_get("/creator/earnings", (("creator_email", st.session_state["user_email"]),))
    if err:
        st.error(err)
        return
    cols = st.columns(4)
    with cols[0]: render_metric("Total Earnings", f"${data['total_earnings']:,.2f}")
    with cols[1]: render_metric("Completed", f"${data['completed_earnings']:,.2f}")
    with cols[2]: render_metric("Pending", f"${data['pending_earnings']:,.2f}")
    with cols[3]: render_metric("Avg Order", f"${data['average_order_value']:,.2f}")
    st.caption("Earnings are computed from real orders in the marketplace.")


def render_creator_reviews() -> None:
    st.markdown('<div class="eyebrow">Reputation</div><h1>Reviews</h1>'
                '<p>What clients say about your work.</p>', unsafe_allow_html=True)
    reviews, err = cached_get("/creator/reviews", (("creator_email", st.session_state["user_email"]),))
    if err:
        st.error(err)
        return
    if not reviews:
        st.info("No reviews yet. Complete orders to receive feedback.")
        return
    for r in reviews:
        with st.container(border=True):
            st.markdown(f"**{'★' * int(r['rating'])}{'☆' * (5 - int(r['rating']))}** — {safe(r['gig_title'])}")
            if r.get("comment"):
                st.write(safe(r["comment"]))
            st.caption(f"— {safe(r['client_name'])} · {safe(r['created_at'][:19])}")


def render_creator_profile() -> None:
    prof, err = cached_get("/creator/profile", (("creator_email", st.session_state["user_email"]),
                                                 ("creator_name", st.session_state["user_name"])))
    if err:
        st.error(err)
        return
    st.markdown('<div class="eyebrow">Creator identity</div><h1>Profile</h1>'
                '<p>Keep the profile clients see up to date.</p>', unsafe_allow_html=True)
    left, right = st.columns([1, 2])
    with left:
        st.markdown(f'<div class="avatar" style="width:76px;height:76px;font-size:1.4rem;margin-bottom:1rem">'
                    f'{safe(st.session_state["user_name"][:2].upper())}</div>'
                    f'<h2>{safe(st.session_state["user_name"])}</h2>'
                    f'<p>{safe(st.session_state["user_email"])}</p>', unsafe_allow_html=True)
    with right:
        with st.form("creator_profile_form"):
            name = st.text_input("Creator name", value=prof.get("creator_name", st.session_state["user_name"]))
            username = st.text_input("Username", value=prof.get("username", ""))
            bio = st.text_area("Bio", value=prof.get("bio", ""))
            skills = st.text_input("Skills", value=prof.get("skills", ""))
            categories = st.text_input("Categories", value=prof.get("categories", ""))
            portfolio = st.text_input("Portfolio URL", value=prof.get("portfolio", ""))
            avatar_url = st.text_input("Avatar URL", value=prof.get("avatar_url", ""))
            submitted = st.form_submit_button("Save profile", type="primary")
            if submitted:
                payload = {
                    "creator_email": st.session_state["user_email"],
                    "creator_name": name.strip(),
                    "username": username.strip(),
                    "bio": bio.strip(),
                    "skills": skills.strip(),
                    "categories": categories.strip(),
                    "portfolio": portfolio.strip(),
                    "avatar_url": avatar_url.strip(),
                }
                _, e = api_request("PUT", "/creator/profile", json=payload)
                if e:
                    st.error(e)
                else:
                    st.session_state["user_name"] = name.strip()
                    clear_cache()
                    flash("success", "✓ Profile saved.")
                    st.rerun()


def render_creator_settings() -> None:
    st.markdown('<div class="eyebrow">Preferences</div><h1>Settings</h1>', unsafe_allow_html=True)
    light = st.checkbox("Use light theme", value=st.session_state["theme"] == "light",
                        key="creator_light_theme")
    desired = "light" if light else "dark"
    if desired != st.session_state["theme"]:
        st.session_state["theme"] = desired
        st.rerun()
    st.caption("More account settings will be added in a future release.")


def render_creator_workspace() -> None:
    st.sidebar.markdown('<div class="wordmark"><span class="mark">T</span>TheHub</div>', unsafe_allow_html=True)
    st.sidebar.caption(f"Creator · {st.session_state['user_name']}")
    current_label = next((l for l, p in CREATOR_PAGE_MAP.items() if p == st.session_state["page"]), "Dashboard")
    selected = st.sidebar.radio("Workspace", CREATOR_PAGES, index=CREATOR_PAGES.index(current_label))
    st.session_state["page"] = CREATOR_PAGE_MAP[selected]
    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state.update(logged_in=False, user_role="", user_name="", user_email="", page="home")
        st.rerun()

    page = st.session_state["page"]
    {
        "creator_dashboard": render_creator_dashboard,
        "creator_gigs": render_creator_gigs,
        "creator_create": render_creator_create,
        "creator_edit": render_creator_edit,
        "creator_orders": render_creator_orders,
        "creator_order_detail": render_creator_order_detail,
        "creator_analytics": render_creator_analytics,
        "creator_messages": render_creator_messages,
        "creator_earnings": render_creator_earnings,
        "creator_reviews": render_creator_reviews,
        "creator_profile": render_creator_profile,
        "creator_settings": render_creator_settings,
    }.get(page, render_creator_dashboard)()
    render_flash()


# ---------------- Client workspace ----------------

CLIENT_PAGES = ["Home", "Explore Gigs", "My Orders", "Saved Gigs", "Messages", "Profile", "Settings"]
CLIENT_PAGE_MAP = {
    "Home": "client_home",
    "Explore Gigs": "client_explore",
    "My Orders": "client_orders",
    "Saved Gigs": "client_saved",
    "Messages": "client_messages",
    "Profile": "client_profile",
    "Settings": "client_settings",
}


def render_client_home() -> None:
    st.markdown('<div class="eyebrow">Client marketplace</div>'
                f'<h1>Hi {safe(st.session_state["user_name"].split()[0])}, what do you need help with?</h1>'
                '<p>Find independent talent for the work that matters next.</p>',
                unsafe_allow_html=True)
    s1, s2 = st.columns([4, 1])
    with s1:
        search = st.text_input("Search", placeholder="Search for services, creators, or skills...",
                               label_visibility="collapsed", key="client_search_box")
    with s2:
        if st.button("Search", type="primary", use_container_width=True):
            st.session_state["client_search"] = search
            navigate("client_explore")

    data, _ = cached_get("/client/dashboard", (("client_email", st.session_state["user_email"]),))
    if data:
        cols = st.columns(5)
        with cols[0]: render_metric("Orders", data["total_orders"])
        with cols[1]: render_metric("Active", data["active_orders"])
        with cols[2]: render_metric("Completed", data["completed_orders"])
        with cols[3]: render_metric("Saved Gigs", data["saved_gigs"])
        with cols[4]: render_metric("Total Spent", f"${data['total_spent']:,.0f}")

    st.markdown('<section class="section"><div class="section-head"><div>'
                '<div class="eyebrow">Start here</div><h2>Popular categories</h2>'
                '</div><p>Explore a focused network of specialists.</p></div>',
                unsafe_allow_html=True)
    for row_start in range(0, len(CATEGORY_CARDS), 4):
        cols = st.columns(4)
        for col, (name, icon, copy, color) in zip(cols, CATEGORY_CARDS[row_start:row_start + 4]):
            with col:
                st.markdown(f'<div class="category-card"><div class="category-icon {color}">{icon}</div>'
                            f'<h3>{name}</h3><p>{copy}</p></div>', unsafe_allow_html=True)
                if st.button("Browse", key=f"cc_{name}", use_container_width=True):
                    st.session_state["client_category"] = CATEGORY_API_MAP.get(name, name)
                    navigate("client_explore")
    st.markdown('</section>', unsafe_allow_html=True)

    st.markdown('<section class="section"><div class="section-head"><div>'
                '<div class="eyebrow">Fresh from creators</div><h2>Recommended for you</h2>'
                '</div></div>', unsafe_allow_html=True)
    gigs, err = cached_get("/gigs", (("limit", "6"), ("sort_by", "rating")))
    if err:
        st.warning(err)
    elif gigs:
        for row_start in range(0, min(6, len(gigs)), 3):
            cols = st.columns(3)
            for col, gig in zip(cols, gigs[row_start:row_start + 3]):
                with col:
                    render_gig_card(gig, "client_home", "client_gig")
    st.markdown('</section>', unsafe_allow_html=True)


def render_client_explore() -> None:
    st.markdown('<div class="eyebrow">Marketplace</div><h1>Explore Gigs</h1>'
                '<p>Search and compare real services from creators on TheHub.</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([2, 1.2, 1, 1.25])
    with c1:
        search = st.text_input("Search", value=st.session_state.pop("client_search", ""),
                               placeholder="Try branding or automation")
    with c2:
        saved_cat = st.session_state.pop("client_category", "All")
        category = st.selectbox("Category", CATEGORIES,
                                index=CATEGORIES.index(saved_cat) if saved_cat in CATEGORIES else 0)
    with c3:
        max_price = st.number_input("Max price", min_value=0, value=0, step=25, help="0 for any price.")
    with c4:
        sort_label = st.selectbox("Sort by", ["Newest", "Price: Low to High", "Price: High to Low", "Top rated"])

    params = {"limit": str(PAGE_SIZE),
              "sort_by": {"Newest": "newest", "Price: Low to High": "cheapest",
                          "Price: High to Low": "priciest", "Top rated": "rating"}[sort_label]}
    if search.strip(): params["search"] = search.strip()
    if category != "All": params["category"] = CATEGORY_API_MAP.get(category, category)

    gigs, err = cached_get("/gigs", tuple(sorted(params.items())))
    saved, _ = cached_get("/client/saved-gigs", (("client_email", st.session_state["user_email"]),))
    if err:
        st.error(err)
        return
    if max_price:
        gigs = [g for g in gigs if float(g.get("rate", 0)) <= max_price]
    saved_ids = {g["id"] for g in (saved or [])}
    st.caption(f"{len(gigs)} gig(s) available")
    if not gigs:
        st.info("No gigs match your filters.")
        return
    for row_start in range(0, len(gigs), 3):
        cols = st.columns(3)
        for col, gig in zip(cols, gigs[row_start:row_start + 3]):
            with col:
                render_gig_card(gig, "client_explore", "client_gig")
                is_saved = gig["id"] in saved_ids
                if st.button("Saved ❤" if is_saved else "Save", key=f"save_{gig['id']}", use_container_width=True):
                    if is_saved:
                        api_request("DELETE", f"/client/saved-gigs/{gig['id']}",
                                    params={"client_email": st.session_state["user_email"]})
                    else:
                        api_request("POST", f"/client/saved-gigs/{gig['id']}",
                                    params={"client_email": st.session_state["user_email"]})
                    clear_cache()
                    st.rerun()


def render_client_gig() -> None:
    render_flash()
    gig = st.session_state.get("selected_gig")
    if not gig:
        navigate("client_explore")
    latest, _ = cached_get(f"/gigs/{gig['id']}")
    gig = latest or gig
    saved, _ = cached_get("/client/saved-gigs", (("client_email", st.session_state["user_email"]),))
    saved_ids = {g["id"] for g in (saved or [])}

    st.markdown(f'<div class="eyebrow">{safe(gig["category"])}</div>'
                f'<h1>{safe(gig["title"])}</h1>'
                f'<p>By <strong>{safe(gig["creator_name"])}</strong></p>', unsafe_allow_html=True)

    left, right = st.columns([1.7, 1])
    with left:
        rating = gig.get("rating") or 0
        rc = gig.get("review_count") or 0
        rating_txt = f"{rating:.1f} ★ ({rc} reviews)" if rc else "No reviews yet"
        st.markdown(f'<div class="preview">'
                    f'<h3>About this gig</h3><p>{safe(gig["description"])}</p>'
                    f'<h4>Deliverables</h4><p>{safe(gig.get("deliverables") or "To be confirmed with the creator.")}</p>'
                    f'<h4>Delivery time</h4><p>{safe(gig.get("delivery_time") or "To be agreed")}</p>'
                    f'<p><strong>{rating_txt}</strong></p>'
                    f'<div class="price">Starting at ${float(gig["rate"]):.2f}</div></div>',
                    unsafe_allow_html=True)
        reviews, _ = cached_get(f"/gigs/{gig['id']}/reviews")
        if reviews:
            st.markdown("### Reviews")
            for r in reviews:
                st.markdown(f"**{'★' * int(r['rating'])}{'☆' * (5 - int(r['rating']))}** — {safe(r['comment'] or 'No comment')}")
                st.caption(f"— {safe(r['client_name'])}")

    with right:
        if st.button("Saved ❤" if gig["id"] in saved_ids else "Save gig", use_container_width=True):
            if gig["id"] in saved_ids:
                api_request("DELETE", f"/client/saved-gigs/{gig['id']}",
                            params={"client_email": st.session_state["user_email"]})
            else:
                api_request("POST", f"/client/saved-gigs/{gig['id']}",
                            params={"client_email": st.session_state["user_email"]})
            clear_cache()
            st.rerun()

        with st.form(f"client_order_{gig['id']}"):
            st.subheader("Place an order")
            requirements = st.text_area("Project brief")
            delivery_date = st.text_input("Preferred delivery date", placeholder="2026-10-15")
            amount = st.number_input("Offer (USD)", min_value=1.0,
                                     value=float(gig.get("rate", 0) or 1), step=5.0)
            submitted = st.form_submit_button("Send order request", type="primary", use_container_width=True)
            if submitted:
                if not requirements.strip():
                    st.error("Add a project brief.")
                else:
                    payload = {
                        "gig_id": gig["id"],
                        "client_name": st.session_state["user_name"],
                        "client_email": st.session_state["user_email"],
                        "requirements": requirements.strip(),
                        "delivery_date": delivery_date.strip() or None,
                        "amount": float(amount),
                    }
                    _, e = api_request("POST", "/orders", json=payload)
                    if e:
                        st.error(e)
                    else:
                        clear_cache()
                        flash("success", f"✓ Order sent to {gig['creator_name']}.")
                        navigate("client_orders")
    if st.button("← Back to explore"):
        navigate("client_explore")


def render_client_orders() -> None:
    st.markdown('<div class="eyebrow">My purchases</div><h1>My Orders</h1>'
                '<p>Track every order from brief to delivery.</p>', unsafe_allow_html=True)
    orders, err = cached_get("/orders", (("actor_email", st.session_state["user_email"]),
                                         ("actor_role", "client"), ("limit", "100")))
    if err:
        st.error(err)
        return
    if not orders:
        st.info("No orders yet. Explore gigs to start.")
        return
    for o in orders:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1.4, 1])
            with c1:
                st.markdown(f"### #{o['id']} · {safe(o['gig_title'])}")
                st.caption(f"Creator: {safe(o['creator_name'])} · Amount: ${float(o['amount']):.2f}")
            with c2:
                st.markdown(render_status_pill(o["status"]), unsafe_allow_html=True)
            with c3:
                if st.button("Open", key=f"cl_open_{o['id']}", type="primary", use_container_width=True):
                    st.session_state["selected_order"] = o
                    navigate("client_order_detail")


def render_client_order_detail() -> None:
    order = st.session_state.get("selected_order")
    if not order:
        navigate("client_orders")
    data, err = cached_get(f"/orders/{order['id']}")
    if err:
        st.error(err)
        return
    order = data
    st.markdown(f'<div class="eyebrow">Order #{order["id"]}</div>'
                f'<h1>{safe(order["gig_title"])}</h1>'
                f'<p>Creator: <strong>{safe(order["creator_name"])}</strong> · '
                f'Amount: <strong>${float(order["amount"]):.2f}</strong></p>',
                unsafe_allow_html=True)
    st.markdown(render_status_pill(order["status"]), unsafe_allow_html=True)

    steps = ["Pending", "Accepted", "In Progress", "Delivered", "Completed"]
    st.markdown('<div class="timeline">' + "".join(
        f'<span class="timeline-step {"done" if order["status"] == s else ""}">{s}</span>' for s in steps
    ) + '</div>', unsafe_allow_html=True)

    if order["status"] == "Declined" and order.get("rejection_reason"):
        st.error(f"Declined — reason: {order['rejection_reason']}")

    st.markdown("#### Project brief")
    st.write(order["requirements"])

    st.markdown("#### Delivered work")
    if order.get("deliverables"):
        for d in order["deliverables"]:
            with st.container(border=True):
                st.markdown(f"**{safe(d['title'])}**")
                if d.get("description"):
                    st.write(safe(d["description"]))
                if d.get("file_url"):
                    if d["file_url"].startswith("data:"):
                        try:
                            header, b64 = d["file_url"].split(",", 1)
                            mime = header.split(";")[0].split(":")[1]
                            ext = mime.split("/")[1].split("+")[0]
                            st.download_button("⬇ Download file", base64.b64decode(b64),
                                               file_name=f"deliverable_{d['id']}.{ext}",
                                               key=f"dl_{d['id']}")
                        except Exception:
                            st.info("File attached (data URL).")
                    else:
                        st.markdown(f"[🔗 Open attachment]({d['file_url']})")
                st.caption(f"Uploaded {safe(d['created_at'][:19])}")
    else:
        st.info("No work uploaded yet.")

    # Client actions
    if order["status"] == "Delivered":
        st.markdown("#### Approve or request revision")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Approve & complete", type="primary", use_container_width=True):
                _, e = api_request("PATCH", f"/orders/{order['id']}/status",
                                   json={"actor_email": st.session_state["user_email"],
                                         "actor_role": "client", "status": "Completed"})
                if e: st.error(e)
                else:
                    clear_cache()
                    flash("success", "✓ Order completed.")
                    st.rerun()
        with c2:
            if st.button("Request revision", use_container_width=True):
                _, e = api_request("PATCH", f"/orders/{order['id']}/status",
                                   json={"actor_email": st.session_state["user_email"],
                                         "actor_role": "client", "status": "Revision Requested"})
                if e: st.error(e)
                else:
                    clear_cache()
                    flash("success", "Revision requested.")
                    st.rerun()

    # Review
    if order["status"] == "Completed" and not order.get("review"):
        st.markdown("#### Leave a review")
        with st.form(f"review_{order['id']}"):
            rating = st.slider("Rating", 1, 5, 5)
            comment = st.text_area("Comment")
            submitted = st.form_submit_button("Submit review", type="primary")
            if submitted:
                payload = {"client_email": st.session_state["user_email"],
                           "client_name": st.session_state["user_name"],
                           "rating": int(rating),
                           "comment": comment.strip()}
                _, e = api_request("POST", f"/orders/{order['id']}/review", json=payload)
                if e: st.error(e)
                else:
                    clear_cache()
                    flash("success", "✓ Review submitted.")
                    st.rerun()
    elif order.get("review"):
        r = order["review"]
        st.info(f"You rated this order {'★' * int(r['rating'])}{'☆' * (5 - int(r['rating']))}")

    # Messaging
    st.markdown("#### Messages with creator")
    msgs, _ = cached_get("/messages", (("user_email", st.session_state["user_email"]),
                                       ("order_id", str(order["id"]))))
    if msgs:
        for m in msgs:
            who = "You" if m["sender_email"] == st.session_state["user_email"] else "Creator"
            st.markdown(f"**{who}:** {safe(m['message'])}")
    new_msg = st.text_input("Send a message", key=f"cmsg_{order['id']}")
    if st.button("Send", key=f"cmsg_send_{order['id']}"):
        if new_msg.strip():
            _, e = api_request("POST", "/messages", json={
                "sender_email": st.session_state["user_email"],
                "receiver_email": order["creator_email"],
                "message": new_msg.strip(),
                "order_id": order["id"],
            })
            if e: st.error(e)
            else:
                clear_cache()
                st.rerun()

    if st.button("← Back to orders"):
        navigate("client_orders")


def render_client_saved() -> None:
    st.markdown('<div class="eyebrow">Shortlist</div><h1>Saved Gigs</h1>', unsafe_allow_html=True)
    saved, err = cached_get("/client/saved-gigs", (("client_email", st.session_state["user_email"]),))
    if err:
        st.error(err)
        return
    if not saved:
        st.info("You have not saved any gigs yet.")
        return
    for row_start in range(0, len(saved), 3):
        cols = st.columns(3)
        for col, gig in zip(cols, saved[row_start:row_start + 3]):
            with col:
                render_gig_card(gig, "saved", "client_gig")
                if st.button("Remove", key=f"rm_{gig['id']}", use_container_width=True):
                    api_request("DELETE", f"/client/saved-gigs/{gig['id']}",
                                params={"client_email": st.session_state["user_email"]})
                    clear_cache()
                    st.rerun()


def render_client_messages() -> None:
    st.markdown('<div class="eyebrow">Communication</div><h1>Messages</h1>', unsafe_allow_html=True)
    msgs, err = cached_get("/messages", (("user_email", st.session_state["user_email"]),))
    if err:
        st.error(err)
        return
    if not msgs:
        st.info("No messages yet.")
    for m in msgs or []:
        with st.container(border=True):
            st.caption(f"{safe(m['sender_email'])} → {safe(m['receiver_email'])} · {safe(m['created_at'][:19])}")
            st.write(safe(m["message"]))


def render_client_profile() -> None:
    st.markdown('<div class="eyebrow">Your account</div><h1>My Profile</h1>', unsafe_allow_html=True)
    data, _ = cached_get("/client/dashboard", (("client_email", st.session_state["user_email"]),))
    left, right = st.columns([1, 2])
    with left:
        st.markdown(f'<div class="avatar" style="width:76px;height:76px;font-size:1.4rem;margin-bottom:1rem">'
                    f'{safe(st.session_state["user_name"][:2].upper())}</div>'
                    f'<h2>{safe(st.session_state["user_name"])}</h2>'
                    f'<p>{safe(st.session_state["user_email"])}</p>', unsafe_allow_html=True)
    with right:
        st.text_input("Name", value=st.session_state["user_name"], disabled=True)
        st.text_input("Email", value=st.session_state["user_email"], disabled=True)
        if data:
            st.metric("Orders", data["total_orders"])
            st.metric("Total Spent", f"${data['total_spent']:,.2f}")


def render_client_settings() -> None:
    st.markdown('<div class="eyebrow">Preferences</div><h1>Settings</h1>', unsafe_allow_html=True)
    light = st.checkbox("Use light theme", value=st.session_state["theme"] == "light",
                        key="client_light_theme")
    desired = "light" if light else "dark"
    if desired != st.session_state["theme"]:
        st.session_state["theme"] = desired
        st.rerun()


def render_client_workspace() -> None:
    st.sidebar.markdown('<div class="wordmark"><span class="mark">T</span>TheHub</div>', unsafe_allow_html=True)
    st.sidebar.caption(f"Client · {st.session_state['user_name']}")
    current_label = next((l for l, p in CLIENT_PAGE_MAP.items() if p == st.session_state["page"]), "Home")
    selected = st.sidebar.radio("Workspace", CLIENT_PAGES, index=CLIENT_PAGES.index(current_label))
    st.session_state["page"] = CLIENT_PAGE_MAP[selected]
    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state.update(logged_in=False, user_role="", user_name="", user_email="", page="home")
        st.rerun()

    page = st.session_state["page"]
    {
        "client_home": render_client_home,
        "client_explore": render_client_explore,
        "client_gig": render_client_gig,
        "client_orders": render_client_orders,
        "client_order_detail": render_client_order_detail,
        "client_saved": render_client_saved,
        "client_messages": render_client_messages,
        "client_profile": render_client_profile,
        "client_settings": render_client_settings,
    }.get(page, render_client_home)()
    render_flash()


# ---------------- Main ----------------

apply_styles()

if st.session_state["logged_in"]:
    if st.session_state["user_role"] == "creator":
        render_creator_workspace()
    else:
        render_client_workspace()
else:
    page = st.session_state["page"]
    if page == "login":
        render_login()
    elif page == "explore":
        render_explore()
    elif page == "gig":
        render_public_gig()
    else:
        render_home()