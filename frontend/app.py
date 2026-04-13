"""
FitLog — Dark Luxury Fitness Tracker
Whoop × Strava aesthetic: electric green on obsidian.
"""

from __future__ import annotations

import streamlit as st
import httpx
from datetime import date, timedelta
from collections import defaultdict

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import streamlit_antd_components as sac  # noqa: F401
    HAS_SAC = True
except ImportError:
    HAS_SAC = False

import os
import _ai_fab

# ── Config ────────────────────────────────────────────────────

API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="FitLog",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme CSS ─────────────────────────────────────────────────

DARK_THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg:        #0A0A0A;
  --surface:   #141414;
  --surface2:  #1A1A1A;
  --border:    #1E1E1E;
  --border2:   #2A2A2A;
  --accent:    #00FF87;
  --accent2:   #00C2FF;
  --danger:    #FF6B6B;
  --warning:   #FFB347;
  --text:      #FFFFFF;
  --muted:     #9CA3AF;
  --r:         12px;
  --r-sm:      8px;
  --shadow:    0 4px 24px rgba(0,0,0,0.6);
  --glow:      0 0 20px rgba(0,255,135,0.25);
}

* { font-family: 'Inter', -apple-system, sans-serif; box-sizing: border-box; }

/* ── App background ── */
.stApp {
  background: var(--bg) !important;
  min-height: 100vh;
}
.main, [data-testid="block-container"] { background: transparent !important; }
.main .block-container { padding-top: 1.25rem; max-width: 1200px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"],
[data-testid="stSidebar"] > div:first-child {
  background: #0D0D0D !important;
  border-right: 1px solid var(--border) !important;
}

/* ── Cards ── */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 1.25rem;
  margin-bottom: 1rem;
  box-shadow: var(--shadow);
}
.card-accent { border-left: 3px solid var(--accent); }

/* ── KPI card ── */
.kpi-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r);
  padding: 1.25rem 1rem;
  border-top: 2px solid var(--accent);
  box-shadow: var(--shadow);
}
.kpi-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 0.4rem;
}
.kpi-value {
  font-size: 1.65rem;
  font-weight: 800;
  color: var(--accent);
  line-height: 1.1;
}
.kpi-sub {
  font-size: 0.75rem;
  color: var(--muted);
  margin-top: 0.25rem;
}

/* ── Welcome banner ── */
.welcome-box {
  background: linear-gradient(135deg, #0D2B1A 0%, #0A0A0A 100%);
  border: 1px solid rgba(0,255,135,0.2);
  border-radius: var(--r);
  padding: 1.75rem 2rem;
  margin-bottom: 1.25rem;
  box-shadow: 0 4px 32px rgba(0,255,135,0.08);
}
.welcome-box h2 {
  margin: 0 0 0.35rem 0;
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text) !important;
}
.welcome-box p { margin: 0; color: var(--muted); font-size: 0.9rem; }

/* ── Workout cards ── */
.workout-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-sm);
  padding: 1rem;
  margin-bottom: 0.6rem;
  transition: border-color 0.2s;
}
.workout-card:hover { border-color: rgba(0,255,135,0.35); }
.workout-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.35rem;
}
.workout-card-title { font-weight: 600; color: var(--text); font-size: 0.95rem; }
.workout-card-badge {
  background: rgba(0,255,135,0.12);
  color: var(--accent);
  border-radius: 6px;
  padding: 0.15rem 0.5rem;
  font-size: 0.72rem;
  font-weight: 600;
}
.workout-card-detail { font-size: 0.82rem; color: var(--muted); }

/* ── Activity feed ── */
.activity-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.7rem;
  background: var(--surface2);
  border-radius: var(--r-sm);
  margin-bottom: 0.45rem;
  border: 1px solid var(--border);
}
.activity-icon {
  width: 34px; height: 34px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; flex-shrink: 0;
}
.activity-icon.workout  { background: rgba(0,255,135,0.12); }
.activity-icon.nutrition { background: rgba(0,194,255,0.12); }
.activity-title { font-size: 0.875rem; font-weight: 500; color: var(--text); }
.activity-time  { font-size: 0.73rem; color: var(--muted); }

/* ── Macro progress bar ── */
.macro-row {
  margin-bottom: 0.85rem;
}
.macro-row-header {
  display: flex; justify-content: space-between;
  font-size: 0.8rem; font-weight: 500; color: var(--muted);
  margin-bottom: 0.3rem;
}
.macro-bar {
  height: 6px; background: var(--border2);
  border-radius: 3px; overflow: hidden;
}
.macro-bar-fill { height: 100%; border-radius: 3px; transition: width 0.5s ease; }

/* ── Chat bubbles (sidebar AI) ── */
.chat-row-user { display: flex; flex-direction: column; align-items: flex-end; margin-bottom: 0.4rem; }
.chat-row-ai   { display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 0.4rem; }
.chat-lbl-user { font-size: 0.68rem; font-weight: 600; color: var(--accent); margin-bottom: 0.15rem; padding-right: 0.2rem; }
.chat-lbl-ai   { font-size: 0.68rem; font-weight: 600; color: var(--accent2); margin-bottom: 0.15rem; padding-left: 0.2rem; }
.chat-bbl {
  max-width: 90%; padding: 0.5rem 0.75rem;
  border-radius: 10px; font-size: 0.84rem; line-height: 1.5;
}
.chat-bbl-user {
  background: var(--accent); color: #0A0A0A;
  border-bottom-right-radius: 3px; font-weight: 500;
}
.chat-bbl-ai {
  background: var(--surface2); color: var(--text);
  border: 1px solid var(--border2); border-bottom-left-radius: 3px;
}

/* ── Buttons ── */
.stButton > button {
  background: var(--accent) !important;
  color: #0A0A0A !important;
  border: none !important;
  border-radius: var(--r-sm) !important;
  font-weight: 700 !important;
  font-size: 0.875rem !important;
  padding: 0.5rem 1.25rem !important;
  transition: all 0.2s !important;
  box-shadow: 0 2px 12px rgba(0,255,135,0.25) !important;
}
.stButton > button:hover {
  background: #00E87A !important;
  box-shadow: 0 4px 20px rgba(0,255,135,0.45) !important;
  transform: translateY(-1px) !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border-color: var(--border2) !important;
  border-radius: var(--r-sm) !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px rgba(0,255,135,0.15) !important;
}
.stSelectbox > div > div {
  background: var(--surface2) !important;
  border-color: var(--border2) !important;
  color: var(--text) !important;
}
.stTextArea textarea {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border-color: var(--border2) !important;
  border-radius: var(--r-sm) !important;
}
.stDateInput input {
  background: var(--surface2) !important;
  color: var(--text) !important;
  border-color: var(--border2) !important;
}

/* ── Form container ── */
[data-testid="stForm"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  padding: 1rem !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--surface) !important;
  border-radius: var(--r-sm) !important;
  padding: 5px !important; gap: 10px !important;
  border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: var(--r-sm) !important;
  font-weight: 500 !important; font-size: 0.875rem !important;
  color: var(--muted) !important; background: transparent !important;
  padding: 0.4rem 1.1rem !important;
  letter-spacing: 0.01em !important;
}
.stTabs [aria-selected="true"] {
  background: var(--accent) !important;
  color: #0A0A0A !important; font-weight: 700 !important;
}

/* ── Sidebar: collapse nav item wrapper gaps ── */
section[data-testid="stSidebar"] .stButton {
  margin-bottom: 0 !important;
}
/* Collapse the stMarkdown wrapper around active nav items */
section[data-testid="stSidebar"] .stMarkdown:has([data-nav-active]) {
  margin-bottom: 0 !important;
  padding: 0 !important;
}
section[data-testid="stSidebar"] .stMarkdown:has([data-nav-active]) > div {
  margin-bottom: 0 !important;
  padding: 0 !important;
}
section[data-testid="stSidebar"] .stButton > button {
  width: 100% !important;
  display: flex !important;
  align-items: center !important;
  justify-content: flex-start !important;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  border-radius: 8px !important;
  padding: 0.55rem 0.9rem !important;
  font-size: 0.83rem !important;
  font-weight: 400 !important;
  letter-spacing: 0.01em !important;
  color: #6B7280 !important;
  transition: background 0.15s, color 0.15s !important;
  transform: none !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255,255,255,0.05) !important;
  color: #D1D5DB !important;
  box-shadow: none !important;
  transform: none !important;
}
/* ── Sidebar sign-out button ── */
section[data-testid="stSidebar"] .stButton:last-child > button {
  color: #4B5563 !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
  margin-top: 0.25rem !important;
}
section[data-testid="stSidebar"] .stButton:last-child > button:hover {
  background: rgba(255,107,107,0.07) !important;
  color: var(--danger) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
}
[data-testid="stExpander"] summary { color: var(--text) !important; }

/* ── Metric widget ── */
[data-testid="metric-container"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  padding: 1rem !important;
}
[data-testid="stMetricLabel"] > div { color: var(--muted) !important; }
[data-testid="stMetricValue"] > div { color: var(--accent) !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { background: var(--surface) !important; }

/* ── Slider ── */
.stSlider [role="slider"] { background: var(--accent) !important; }

/* ── Text ── */
h1, h2, h3, h4, h5, h6 { color: var(--text) !important; }
.stMarkdown p, .stMarkdown li { color: var(--text); }
label { color: var(--muted) !important; }
.stCaption, [data-testid="stCaptionContainer"] { color: var(--muted) !important; }
.stRadio label, .stCheckbox label { color: var(--text) !important; }
.stAlert { border-radius: var(--r) !important; }
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Login ── */
.login-wrap { max-width: 420px; margin: 0 auto; padding: 2rem; }
.login-logo {
  width: 64px; height: 64px;
  background: var(--accent);
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  font-size: 32px; margin: 0 auto 1rem;
  box-shadow: 0 4px 24px rgba(0,255,135,0.35);
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,255,135,0.4); }

/* ── Chart legend pill ── */
.chart-legend { display: flex; gap: .5rem; align-items: center; margin-bottom: .5rem; flex-wrap: wrap; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.legend-label { font-size: .71rem; color: var(--muted); font-weight: 500; }

/* ── Progress ring / section improvements ── */
.card:hover { border-color: rgba(255,255,255,0.08); }
.card-accent:hover { border-left-color: var(--accent); }

/* ── KPI card polish ── */
.kpi-card {
  position: relative; overflow: hidden;
}
.kpi-card::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(255,255,255,0.015) 0%, transparent 100%);
  pointer-events: none;
}

/* ── Welcome box typography ── */
.welcome-box h2 { letter-spacing: -.02em; }

/* ── Activity item polish ── */
.activity-item:hover { border-color: rgba(255,255,255,0.08); background: var(--surface); }

/* ── Section header rule ── */
.section-rule {
  display: flex; align-items: center; gap: .5rem; margin-bottom: .75rem;
}
.section-rule::after {
  content: ''; flex: 1; height: 1px; background: var(--border);
}

/* ════════════════════════════════════════
   MY PROGRESS — animated analytics layer
   ════════════════════════════════════════ */
@keyframes ringReveal {
  from { stroke-dashoffset: var(--dash-len); }
  to   { stroke-dashoffset: 0; }
}
@keyframes fitSlideUp {
  from { opacity:0; transform:translateY(18px); }
  to   { opacity:1; transform:translateY(0);    }
}
@keyframes fitPulseGlow {
  0%,100% { box-shadow: 0 0 8px rgba(255,179,71,.1); }
  50%      { box-shadow: 0 0 26px rgba(255,179,71,.45); }
}
@keyframes barReveal {
  from { width: 0 !important; }
}

/* ── Score cockpit ── */
.score-cockpit {
  background: linear-gradient(135deg,#0D1F15 0%,#0A0A0A 55%,#0A0A1F 100%);
  border: 1px solid rgba(0,255,135,.16);
  border-radius: 16px;
  padding: 1.75rem 2rem;
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 2.5rem;
  flex-wrap: wrap;
  box-shadow: 0 8px 48px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.03);
  animation: fitSlideUp .5s ease both;
}
.score-ring-wrap { flex-shrink:0; }
.score-ring-wrap svg { display:block; }
.score-ring-label {
  font-size:.6rem; font-weight:700; letter-spacing:.1em;
  text-transform:uppercase; color:var(--muted);
  text-align:center; margin-top:.4rem;
}
.motivation-box { flex:1; min-width:180px; }
.motivation-grade {
  font-size:3.75rem; font-weight:900; line-height:1;
  letter-spacing:-.04em; margin-bottom:.2rem;
}
.motivation-text { font-size:.84rem; color:var(--muted); line-height:1.55; }

/* ── Streak badge ── */
.streak-badge {
  display:inline-flex; align-items:center; gap:.35rem;
  background:rgba(255,179,71,.1); border:1px solid rgba(255,179,71,.25);
  border-radius:20px; padding:.28rem .7rem;
  font-size:.78rem; font-weight:700; color:#FFB347;
  margin-bottom:.7rem;
  animation: fitPulseGlow 2.5s ease-in-out infinite;
}

/* ── Ring cards ── */
.ring-card {
  background:var(--surface); border:1px solid var(--border);
  border-radius:14px; padding:1.1rem .85rem;
  display:flex; flex-direction:column; align-items:center; gap:.4rem;
  transition:border-color .2s, transform .2s, box-shadow .2s;
  animation:fitSlideUp .4s ease both;
}
.ring-card:hover {
  border-color:rgba(0,255,135,.28);
  transform:translateY(-3px);
  box-shadow:0 8px 28px rgba(0,0,0,.5);
}
.ring-card-label {
  font-size:.63rem; font-weight:700;
  text-transform:uppercase; letter-spacing:.09em; color:var(--muted);
}
.ring-card-sub { font-size:.66rem; color:var(--muted); text-align:center; }

/* ── Performance bars ── */
.perf-bar-row { margin-bottom:1rem; }
.perf-bar-header {
  display:flex; justify-content:space-between; align-items:baseline;
  margin-bottom:.4rem;
}
.perf-bar-name { font-size:.85rem; font-weight:600; color:var(--text); }
.perf-bar-pct  { font-size:.85rem; font-weight:700; }
.perf-bar-track {
  height:12px; background:var(--border2); border-radius:6px; overflow:hidden;
}
.perf-bar-fill {
  height:100%; border-radius:6px;
  animation:barReveal .75s cubic-bezier(.34,1.56,.64,1) both;
}

/* ── Section divider ── */
.progress-hdr {
  display:flex; align-items:center; gap:.75rem; margin-bottom:1rem; margin-top:.25rem;
}
.progress-hdr-line { flex:1; height:1px; background:var(--border); }
.progress-hdr-text {
  font-size:.65rem; font-weight:700; color:var(--muted);
  text-transform:uppercase; letter-spacing:.09em; white-space:nowrap;
}

/* ── Empty state ── */
.empty-state {
  text-align:center; padding:2.5rem 1rem;
  animation:fitSlideUp .4s ease both;
}
.empty-state-icon { font-size:2.5rem; margin-bottom:.75rem; }
.empty-state-title { font-size:1rem; font-weight:700; color:var(--text); margin-bottom:.35rem; }
.empty-state-sub { font-size:.82rem; color:var(--muted); }
</style>
"""

st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────

_DEFAULTS: dict = {
    "logged_in": False, "token": None, "user": None,
    "selected_profile_id": None, "selected_profile_name": None,
    "active_section": "Dashboard", "chat_messages": [],
    "initial_load_done": False, "ai_nutrition": None,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

_SECTIONS = ["Dashboard", "Workouts", "Nutrition", "My Progress", "Wellness", "Profile"]

# ── API helpers ───────────────────────────────────────────────

@st.cache_resource
def _client() -> httpx.Client:
    return httpx.Client(base_url=API_BASE, timeout=15.0)


def _headers() -> dict:
    t = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {t}"} if t else {}


def _get(path: str, params: dict | None = None):
    try:
        r = _client().get(path, params=params, headers=_headers())
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []


def _post(path: str, json: dict):
    try:
        r = _client().post(path, json=json, headers=_headers())
        return r.json() if r.status_code in (200, 201) else None
    except Exception:
        return None


def _delete(path: str) -> bool:
    try:
        return _client().delete(path, headers=_headers()).status_code == 204
    except Exception:
        return False


def _put(path: str, json: dict):
    try:
        r = _client().put(path, json=json, headers=_headers())
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def api_login(email: str, pw: str):
    try:
        r = _client().post("/auth/login", json={"email": email, "password": pw})
        if r.status_code == 200:
            return r.json()
        st.error(r.json().get("detail", "Invalid credentials"))
    except Exception as e:
        st.error(f"Connection error: {e}")
    return None


def api_register(email: str, pw: str, name: str):
    try:
        r = _client().post("/auth/register", json={"email": email, "password": pw, "name": name})
        if r.status_code == 201:
            return r.json()
        st.error(r.json().get("detail", "Registration failed"))
    except Exception as e:
        st.error(f"Connection error: {e}")
    return None


@st.cache_data(ttl=300)
def get_profiles(token: str): return _get("/profile/") or []

@st.cache_data(ttl=300)
def get_exercises(token: str): return _get("/exercises/") or []

@st.cache_data(ttl=60)
def get_workout_logs(token: str, pid: str = ""): return _get("/logs/", {"limit": 50, "profile_id": pid} if pid else {"limit": 50}) or []

@st.cache_data(ttl=60)
def get_macros(token: str, pid: str = ""): return _get("/macros/", {"limit": 50, "profile_id": pid} if pid else {"limit": 50}) or []

@st.cache_data(ttl=300)
def get_protein_target(token: str, pid: str): return _get(f"/profile/{pid}/protein-target")

@st.cache_data(ttl=60)
def get_sleep(token: str, pid: str = ""): return _get("/sleep/", {"limit": 30, "profile_id": pid} if pid else {"limit": 30}) or []

@st.cache_data(ttl=60)
def get_hydration(token: str, pid: str = ""): return _get("/hydration/", {"limit": 30, "profile_id": pid} if pid else {"limit": 30}) or []

@st.cache_data(ttl=60)
def get_body_metrics(token: str, pid: str = ""): return _get("/body-metrics/", {"limit": 30, "profile_id": pid} if pid else {"limit": 30}) or []

@st.cache_data(ttl=60)
def get_recovery(token: str, pid: str = ""): return _get("/recovery/", {"limit": 30, "profile_id": pid} if pid else {"limit": 30}) or []

@st.cache_data(ttl=60)
def get_steps(token: str, pid: str = ""): return _get("/steps/", {"limit": 90, "profile_id": pid} if pid else {"limit": 90}) or []

@st.cache_data(ttl=60)
def get_goals(token: str, pid: str): return _get(f"/profile/{pid}/goals") or {}

@st.cache_data(ttl=120)
def get_analytics_workouts(token: str, pid: str): return _get("/logs/", {"limit": 500, "profile_id": pid}) or []

@st.cache_data(ttl=120)
def get_analytics_macros(token: str, pid: str): return _get("/macros/", {"limit": 500, "profile_id": pid}) or []

@st.cache_data(ttl=120)
def get_analytics_metrics(token: str, pid: str): return _get("/body-metrics/", {"limit": 500, "profile_id": pid}) or []

@st.cache_data(ttl=120)
def get_analytics_steps(token: str, pid: str): return _get("/steps/", {"limit": 200, "profile_id": pid}) or []


def _create(endpoint: str, data: dict, clear_fn=None):
    r = _post(endpoint, data)
    if r and clear_fn:
        clear_fn()
    return r


# ── UI helpers ────────────────────────────────────────────────

def _kpi(label: str, value: str, sub: str = "", accent: str = "var(--accent)") -> None:
    st.markdown(f"""
    <div class="kpi-card" style="border-top-color:{accent};">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value" style="color:{accent};">{value}</div>
      {"" if not sub else f'<div class="kpi-sub">{sub}</div>'}
    </div>""", unsafe_allow_html=True)


def _section_hdr(title: str) -> None:
    st.markdown(
        f'<div style="font-size:0.72rem; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.07em; margin-bottom:0.75rem;">{title}</div>',
        unsafe_allow_html=True,
    )


def _macro_bar(label: str, val: float, target: float, color: str) -> None:
    pct = min(100, int(val / target * 100)) if target > 0 else 0
    st.markdown(f"""
    <div class="macro-row">
      <div class="macro-row-header">
        <span>{label}</span>
        <span>{val:.0f} / {target:.0f}g &nbsp;·&nbsp; {pct}%</span>
      </div>
      <div class="macro-bar"><div class="macro-bar-fill" style="width:{pct}%;background:{color};"></div></div>
    </div>""", unsafe_allow_html=True)


def _workout_card(name: str, detail: str, date_str: str) -> None:
    st.markdown(f"""
    <div class="workout-card">
      <div class="workout-card-header">
        <span class="workout-card-title">{name}</span>
        <span class="workout-card-badge">{date_str}</span>
      </div>
      <div class="workout-card-detail">{detail}</div>
    </div>""", unsafe_allow_html=True)


def _dark_chart(fig, height: int = 270) -> None:
    if not HAS_PLOTLY:
        return
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.015)",
        margin=dict(l=4, r=4, t=18, b=4),
        height=height,
        font=dict(color="#9CA3AF", family="Inter, sans-serif", size=11),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            tickfont=dict(size=10, color="#6B7280"),
            tickangle=-35,
            showgrid=False,
            linecolor="rgba(255,255,255,0.06)",
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.06)",
            tickfont=dict(size=10, color="#6B7280"),
            zeroline=False,
            linecolor="rgba(255,255,255,0.06)",
        ),
        bargap=0.28,
        hoverlabel=dict(
            bgcolor="#1A1A1A",
            bordercolor="#2A2A2A",
            font=dict(color="#FFFFFF", size=12, family="Inter, sans-serif"),
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.0,
            xanchor="right", x=1,
            font=dict(size=10), bgcolor="rgba(0,0,0,0)",
        ),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def _goal_color(val: float, target: float) -> str:
    """3-tier color: green = met, amber = within 25%, red = far below."""
    if target <= 0:
        return "#00FF87"
    pct = val / target
    if pct >= 0.97:
        return "#00FF87"
    elif pct >= 0.70:
        return "#FFB347"
    else:
        return "#FF6B6B"


def _chart_legend(met_label: str = "Goal met", partial_label: str = "Within 30%", miss_label: str = "Below target") -> None:
    st.markdown(
        f'<div class="chart-legend">'
        f'<span class="legend-dot" style="background:#00FF87;"></span><span class="legend-label">{met_label}</span>'
        f'<span class="legend-dot" style="background:#FFB347;margin-left:.25rem;"></span><span class="legend-label">{partial_label}</span>'
        f'<span class="legend-dot" style="background:#FF6B6B;margin-left:.25rem;"></span><span class="legend-label">{miss_label}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _ring_card(label: str, pct: float, val_str: str, sub: str, color: str, delay: str = "0s") -> str:
    """Animated SVG radial-progress ring card for a KPI metric."""
    r, circ = 40, 251.33
    filled = min(pct / 100.0, 1.0) * circ
    gap    = max(circ - filled, 0.01)
    return (
        f'<div class="ring-card" style="animation-delay:{delay};">'
        f'<div class="ring-card-label">{label}</div>'
        f'<svg width="96" height="96" viewBox="0 0 96 96" style="overflow:visible;">'
        f'<circle cx="48" cy="48" r="{r}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="8"/>'
        f'<circle cx="48" cy="48" r="{r}" fill="none" stroke="{color}" stroke-width="8"'
        f' stroke-linecap="round" stroke-dasharray="{filled:.2f} {gap:.2f}"'
        f' transform="rotate(-90 48 48)"'
        f' style="--dash-len:{filled:.2f};animation:ringReveal 0.85s cubic-bezier(0.34,1.56,0.64,1) {delay} both;'
        f'filter:drop-shadow(0 0 5px {color}55);"/>'
        f'<text x="48" y="44" text-anchor="middle" dominant-baseline="middle"'
        f' fill="{color}" font-size="15" font-weight="800" font-family="Inter,sans-serif">{int(pct)}%</text>'
        f'<text x="48" y="59" text-anchor="middle" dominant-baseline="middle"'
        f' fill="#6B7280" font-size="8" font-family="Inter,sans-serif">{val_str}</text>'
        f'</svg>'
        f'<div class="ring-card-sub">{sub}</div>'
        f'</div>'
    )


def _score_cockpit_html(score: int, grade: str, grade_color: str, motivation: str, streak: int) -> str:
    """Large SVG score ring + grade + motivation banner."""
    r, circ = 50, 314.16
    filled = score / 100.0 * circ
    gap    = max(circ - filled, 0.01)
    streak_html = (
        f'<div class="streak-badge">🔥 {streak}-day streak</div>'
        if streak > 0 else ''
    )
    return (
        f'<div class="score-cockpit">'
        f'<div class="score-ring-wrap">'
        f'<svg width="138" height="138" viewBox="0 0 138 138" style="overflow:visible;">'
        f'<circle cx="69" cy="69" r="{r}" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="10"/>'
        f'<circle cx="69" cy="69" r="{r}" fill="none" stroke="{grade_color}" stroke-width="10"'
        f' stroke-linecap="round" stroke-dasharray="{filled:.2f} {gap:.2f}"'
        f' transform="rotate(-90 69 69)"'
        f' style="--dash-len:{filled:.2f};animation:ringReveal 1.1s cubic-bezier(0.34,1.56,0.64,1) 0.1s both;'
        f'filter:drop-shadow(0 0 14px {grade_color}60);"/>'
        f'<text x="69" y="62" text-anchor="middle" dominant-baseline="middle"'
        f' fill="{grade_color}" font-size="30" font-weight="900" font-family="Inter,sans-serif">{score}</text>'
        f'<text x="69" y="80" text-anchor="middle" dominant-baseline="middle"'
        f' fill="#4B5563" font-size="9.5" font-family="Inter,sans-serif">out of 100</text>'
        f'</svg>'
        f'<div class="score-ring-label">Performance Score</div>'
        f'</div>'
        f'<div class="motivation-box">'
        f'{streak_html}'
        f'<div class="motivation-grade" style="color:{grade_color};">{grade}</div>'
        f'<div style="font-size:.7rem;font-weight:700;color:var(--muted);letter-spacing:.07em;'
        f'text-transform:uppercase;margin-bottom:.35rem;">Performance Grade</div>'
        f'<div class="motivation-text">{motivation}</div>'
        f'</div>'
        f'</div>'
    )


# ── Login page ────────────────────────────────────────────────

def show_login():
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; margin-bottom:2rem;">
      <div class="login-logo" style="font-family:'Inter',sans-serif;font-size:22px;font-weight:800;letter-spacing:-1px;">FL</div>
      <h1 style="margin:0; font-size:1.75rem; font-weight:800;">FitLog</h1>
      <p style="margin:0.4rem 0 0; color:var(--muted); font-size:0.9rem;">Professional Fitness &amp; Nutrition Tracker</p>
    </div>""", unsafe_allow_html=True)

    tab_in, tab_up = st.tabs(["Sign In", "Create Account"])

    with tab_in:
        with st.form("login"):
            email = st.text_input("Email", placeholder="you@email.com")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In", use_container_width=True):
                if email and pw:
                    r = api_login(email.strip(), pw)
                    if r:
                        st.session_state.update(logged_in=True, token=r.get("access_token", ""), user=r.get("user", {}))
                        st.rerun()
                else:
                    st.error("Please fill in all fields")

    with tab_up:
        with st.form("register"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            pw = st.text_input("Password", type="password", placeholder="Min 8 characters")
            pw2 = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Create Account", use_container_width=True):
                if not (name and email and pw):
                    st.error("Please fill in all fields")
                elif pw != pw2:
                    st.error("Passwords don't match")
                elif len(pw) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    r = api_register(email.strip(), pw, name.strip())
                    if r:
                        st.session_state.update(logged_in=True, token=r.get("access_token", ""), user=r.get("user", {}))
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ── Dashboard ─────────────────────────────────────────────────

def show_dashboard():
    token = st.session_state.token
    pid = str(st.session_state.selected_profile_id or "")
    user_name = (st.session_state.user or {}).get("name", "Athlete")
    profile_name = st.session_state.get("selected_profile_name", "")
    profiles = get_profiles(token)

    st.markdown(f"""
    <div class="welcome-box">
      <h2>Welcome back, {user_name}</h2>
      <p>{"Profile: " + profile_name if profile_name else "Select a profile to start tracking"}</p>
    </div>""", unsafe_allow_html=True)

    # ── Onboarding — new user with no profiles ────────────────
    if not profiles:
        st.markdown("""
        <div class="card card-accent" style="padding:1.5rem;">
          <div style="font-size:1rem;font-weight:700;color:var(--text);margin-bottom:.4rem;">Get started in 3 steps</div>
          <div style="color:var(--muted);font-size:.85rem;">FitLog needs a profile before it can track anything.</div>
        </div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown('<div class="kpi-card"><div class="kpi-label">Step 1</div><div class="kpi-value" style="font-size:.95rem;">Create Profile</div><div class="kpi-sub">Set your weight, height, age and goal</div></div>', unsafe_allow_html=True)
            if st.button("Go to Profile", key="onboard_1", use_container_width=True):
                st.session_state.active_section = "Profile"; st.rerun()
        with c2:
            st.markdown('<div class="kpi-card"><div class="kpi-label">Step 2</div><div class="kpi-value" style="font-size:.95rem;color:var(--accent2);">Set Goals</div><div class="kpi-sub">Personalize daily targets for steps, calories, protein</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown('<div class="kpi-card"><div class="kpi-label">Step 3</div><div class="kpi-value" style="font-size:.95rem;color:var(--warning);">Start Logging</div><div class="kpi-sub">Track workouts, meals, wellness metrics</div></div>', unsafe_allow_html=True)
        return

    # ── Goals discoverability hint ────────────────────────────
    if pid:
        u_goals_d = get_goals(token, pid)
        if not any(u_goals_d.get(k) for k in ["daily_steps", "weekly_workouts", "daily_calories", "daily_protein_g"]):
            st.markdown("""
            <div class="card" style="border-left:3px solid var(--warning);padding:.75rem 1.1rem;margin-bottom:.75rem;">
              <span style="color:var(--warning);font-weight:600;font-size:.8rem;">Tip</span>
              <span style="color:var(--muted);font-size:.8rem;"> — Your targets are auto-computed from your profile. Set custom goals in <strong style="color:var(--text);">Profile → Edit Goals</strong>.</span>
            </div>""", unsafe_allow_html=True)

    workouts = get_workout_logs(token, pid)
    macros   = get_macros(token, pid)
    today    = str(date.today())
    week_start = date.today() - timedelta(days=date.today().weekday())

    today_workouts = [w for w in workouts if w.get("log_date") == today]
    week_workouts  = [w for w in workouts if w.get("log_date", "") >= str(week_start)]
    today_macros   = [m for m in macros if m.get("entry_date") == today]
    today_cals     = sum(m.get("calories", 0) for m in today_macros)

    streak = 0
    all_dates = {w.get("log_date") for w in workouts} | {m.get("entry_date") for m in macros}
    check = date.today()
    while str(check) in all_dates:
        streak += 1
        check -= timedelta(days=1)

    last_w = workouts[0] if workouts else None

    k1, k2, k3, k4 = st.columns(4)
    with k1: _kpi("Today's Calories", f"{today_cals:.0f}", "kcal consumed")
    with k2: _kpi("Workouts This Week", str(len(week_workouts)), "sessions logged", "#00C2FF")
    with k3: _kpi("Current Streak", f"{streak}d", "consecutive days", "#FFB347")
    with k4: _kpi("Last Workout", last_w.get("exercise_name", "—")[:14] if last_w else "—", last_w.get("log_date", "") if last_w else "No workouts yet", "#FF6B6B")

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="card card-accent">', unsafe_allow_html=True)
        _section_hdr("Recent Activity")
        items = []
        for w in workouts[:4]:
            items.append({"type": "workout", "title": w.get("exercise_name", "Workout"),
                          "detail": f"{w.get('sets',0)}×{w.get('reps',0)} @ {w.get('weight_kg',0)}kg",
                          "date": w.get("log_date", "")})
        for m in macros[:4]:
            items.append({"type": "nutrition", "title": f"{m.get('calories',0):.0f} kcal",
                          "detail": f"P:{m.get('protein_g',0):.0f}g · C:{m.get('carbs_g',0):.0f}g · F:{m.get('fat_g',0):.0f}g",
                          "date": m.get("entry_date", "")})
        items.sort(key=lambda x: x["date"], reverse=True)
        if items:
            for it in items[:6]:
                lbl = "W" if it["type"] == "workout" else "N"
                css = it["type"]
                st.markdown(f"""
                <div class="activity-item">
                  <div class="activity-icon {css}" style="font-size:.7rem;font-weight:700;color:var(--accent);letter-spacing:.02em;">{lbl}</div>
                  <div style="flex:1;">
                    <div class="activity-title">{it["title"]}</div>
                    <div class="activity-time">{it["detail"]} · {it["date"]}</div>
                  </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No activity yet. Start logging!")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        _section_hdr("Quick Actions")
        if st.button("+ Log Workout", key="quick_workout", use_container_width=True):
            st.session_state.active_section = "Workouts"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("+ Log Meal", key="quick_meal", use_container_width=True):
            st.session_state.active_section = "Nutrition"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # Today's macro snapshot — targets from profile TDEE + user goal overrides
        target_data = get_protein_target(token, pid) if pid else None
        protein_target = float((target_data or {}).get("protein_g", 150))
        if pid:
            p_obj_d = next((p for p in profiles if str(p.get("id")) == pid), {})
            w_kg_d  = float(p_obj_d.get("weight_kg") or 75)
            h_cm_d  = float(p_obj_d.get("height_cm") or 175)
            age_d   = int(p_obj_d.get("age") or 30)
            gen_d   = (p_obj_d.get("gender") or "male").lower()
            tdee_d  = (10 * w_kg_d + 6.25 * h_cm_d - 5 * age_d + (5 if gen_d == "male" else -161)) * 1.55
            carbs_target = round(tdee_d * 0.45 / 4)
            fat_target   = round(tdee_d * 0.30 / 9)
            u_goals_m = get_goals(token, pid)
            if u_goals_m.get("daily_protein_g"):
                protein_target = float(u_goals_m["daily_protein_g"])
        else:
            carbs_target, fat_target = 250, 70

        total_protein = sum(m.get("protein_g", 0) for m in today_macros)
        total_carbs   = sum(m.get("carbs_g", 0)   for m in today_macros)
        total_fat     = sum(m.get("fat_g", 0)      for m in today_macros)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        _section_hdr("Today's Macros")
        _macro_bar("Protein", total_protein, protein_target or 150, "var(--accent)")
        _macro_bar("Carbs",   total_carbs,   carbs_target, "var(--accent2)")
        _macro_bar("Fat",     total_fat,     fat_target,   "var(--warning)")
        st.markdown("</div>", unsafe_allow_html=True)


# ── Workouts ──────────────────────────────────────────────────

_COMMON_EXERCISES = [
    {"name": "Barbell Squat",       "category": "strength", "muscle_group": "legs",      "description": "King of compound movements — quads, glutes, hamstrings."},
    {"name": "Bench Press",         "category": "strength", "muscle_group": "chest",     "description": "Horizontal push. Primary chest and tricep builder."},
    {"name": "Deadlift",            "category": "strength", "muscle_group": "back",      "description": "Full-body compound. Builds posterior chain strength."},
    {"name": "Pull-up",             "category": "strength", "muscle_group": "back",      "description": "Bodyweight vertical pull. Excellent for lat width."},
    {"name": "Overhead Press",      "category": "strength", "muscle_group": "shoulders", "description": "Vertical push. Builds shoulder mass and triceps."},
    {"name": "Romanian Deadlift",   "category": "strength", "muscle_group": "legs",      "description": "Hip-hinge movement. Targets hamstrings and glutes."},
    {"name": "Incline Bench Press", "category": "strength", "muscle_group": "chest",     "description": "Upper chest emphasis. Dumbbell or barbell."},
    {"name": "Dumbbell Row",        "category": "strength", "muscle_group": "back",      "description": "Unilateral back exercise. Builds thickness and balance."},
    {"name": "Lat Pulldown",        "category": "strength", "muscle_group": "back",      "description": "Cable vertical pull. Great lat builder."},
    {"name": "Leg Press",           "category": "strength", "muscle_group": "legs",      "description": "Machine compound for quads and glutes."},
    {"name": "Dumbbell Curl",       "category": "strength", "muscle_group": "arms",      "description": "Isolation for biceps. Alternating or simultaneous."},
    {"name": "Tricep Pushdown",     "category": "strength", "muscle_group": "arms",      "description": "Cable isolation for all three tricep heads."},
    {"name": "Hip Thrust",          "category": "strength", "muscle_group": "glutes",    "description": "Barbell glute isolation. Best glute activator."},
    {"name": "Plank",               "category": "strength", "muscle_group": "core",      "description": "Isometric core stabiliser. Hold for time."},
    {"name": "Running",             "category": "cardio",   "muscle_group": "full-body", "description": "Steady-state or interval cardio."},
]


def _seed_exercises(token: str) -> int:
    """Seed the common exercise library for a user who has none. Returns count added."""
    added = 0
    for ex in _COMMON_EXERCISES:
        if _post("/exercises/", ex):
            added += 1
    if added:
        get_exercises.clear()
    return added


def show_workouts():
    token = st.session_state.token
    pid = str(st.session_state.selected_profile_id or "")

    exercises = get_exercises(token)
    if not exercises:
        # Silently seed common exercises for new users.
        # No spinner — avoids breaking tab/form widget state on first render.
        _seed_exercises(token)
        exercises = get_exercises(token)

    tab_log, tab_hist, tab_ex = st.tabs(["Log Workout", "History", "Exercises"])

    with tab_log:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        _section_hdr("Log New Workout")
        if not exercises:
            st.info("Your exercise library is empty. Go to the **Exercises** tab to load common exercises first.")
        else:
            ex_opts = {f"{e['name']} ({e.get('muscle_group','')})": e["id"] for e in exercises}
            with st.form("log_workout"):
                col1, col2 = st.columns([2, 1])
                with col1: sel = st.selectbox("Exercise", list(ex_opts.keys()))
                with col2: w_date = st.date_input("Date", date.today())
                c1, c2, c3 = st.columns(3)
                with c1: sets = st.number_input("Sets", 1, 100, 3)
                with c2: reps = st.number_input("Reps", 1, 1000, 10)
                with c3: weight = st.number_input("Weight (kg)", 0.0, 1000.0, 0.0, 2.5)
                notes = st.text_input("Notes", placeholder="How did it feel?")
                if st.form_submit_button("Log Workout", use_container_width=True):
                    r = _create("/logs/", {
                        "profile_id": pid, "exercise_id": ex_opts[sel],
                        "log_date": str(w_date), "sets": int(sets), "reps": int(reps),
                        "weight_kg": float(weight), "notes": notes or None,
                    }, get_workout_logs.clear)
                    if r:
                        st.success("Workout logged!")
                        st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_hist:
        workouts = get_workout_logs(token, pid)
        if not workouts:
            st.info("No workouts yet. Start training!")
            return
        by_date = defaultdict(list)
        for w in workouts:
            by_date[w.get("log_date", "")].append(w)
        for d in sorted(by_date.keys(), reverse=True)[:15]:
            logs = by_date[d]
            with st.expander(f"{d} — {len(logs)} exercise{'s' if len(logs)!=1 else ''}"):
                for idx, log in enumerate(logs):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1:
                        st.markdown(f"**{log.get('exercise_name','Exercise')}**")
                        if log.get("notes"): st.caption(log["notes"][:60])
                    with c2:
                        st.caption(f"{log['sets']} × {log['reps']} @ {log['weight_kg']}kg")
                    with c3:
                        if st.button("×", key=f"del_log_{log['id']}_{idx}"):
                            if _delete(f"/logs/{log['id']}"):
                                get_workout_logs.clear()
                                st.rerun()

    with tab_ex:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        _section_hdr(f"Exercise Library — {len(exercises)} exercises")

        if not exercises:
            st.markdown(
                '<div style="color:var(--muted);font-size:.85rem;margin-bottom:.75rem;">'
                'Your library is empty. Load the standard exercises to get started.</div>',
                unsafe_allow_html=True,
            )
            if st.button("Load Common Exercises", use_container_width=True):
                with st.spinner("Adding exercises..."):
                    added = _seed_exercises(token)
                if added:
                    st.success(f"Added {added} exercises!")
                    st.rerun()
                else:
                    st.error("Could not add exercises — is the backend running?")
        else:
            st.markdown("---")
            cat_groups: dict = {}
            for e in sorted(exercises, key=lambda x: (x.get("category",""), x.get("muscle_group",""), x["name"])):
                cat = e.get("category", "other").title()
                cat_groups.setdefault(cat, []).append(e)

            for cat, exs in cat_groups.items():
                st.markdown(f"**{cat}** — {len(exs)} exercise{'s' if len(exs)!=1 else ''}")
                for idx, e in enumerate(exs):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1:
                        st.markdown(f"**{e['name']}**")
                        if e.get("description"):
                            st.caption(e["description"][:60])
                    with c2:
                        st.caption(e.get("muscle_group","").replace("-", " ").title())
                    with c3:
                        if st.button("×", key=f"del_ex_{e['id']}_{idx}"):
                            if _delete(f"/exercises/{e['id']}"):
                                get_exercises.clear()
                                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        # Add custom exercise
        with st.expander("+ Add Custom Exercise"):
            with st.form("add_exercise"):
                ex_name = st.text_input("Exercise Name", placeholder="e.g., Cable Fly")
                c1, c2 = st.columns(2)
                with c1:
                    ex_cat = st.selectbox("Category", ["strength", "cardio", "flexibility", "sports"])
                with c2:
                    ex_muscle = st.selectbox("Muscle Group", [
                        "chest", "back", "legs", "shoulders", "arms",
                        "core", "glutes", "full-body", "other"
                    ])
                ex_desc = st.text_area("Description (optional)", height=60)
                if st.form_submit_button("Add Exercise"):
                    if not ex_name.strip():
                        st.error("Exercise name is required.")
                    else:
                        r = _create("/exercises/", {
                            "name": ex_name.strip(),
                            "category": ex_cat,
                            "muscle_group": ex_muscle,
                            "description": ex_desc.strip() or None,
                        }, get_exercises.clear)
                        if r:
                            st.success(f"Added '{r['name']}'!")
                            get_exercises.clear()
                            st.rerun()
                        else:
                            st.error("Failed to add exercise. Check the backend is running.")


# ── Nutrition ─────────────────────────────────────────────────

def show_nutrition():
    token = st.session_state.token
    pid = str(st.session_state.selected_profile_id or "")

    tab_log, tab_hist = st.tabs(["Log Meal", "History"])

    with tab_log:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        mode = st.radio("Entry mode", ["Manual", "AI Analysis"], horizontal=True)

        if mode == "Manual":
            _section_hdr("Log Your Meal")
            with st.form("log_nutrition"):
                m_date = st.date_input("Date", date.today())
                c1, c2 = st.columns(2)
                with c1:
                    cals = st.number_input("Calories", 0, 20000, 500)
                    prot = st.number_input("Protein (g)", 0, 1000, 30)
                with c2:
                    carbs = st.number_input("Carbs (g)", 0, 2000, 60)
                    fat   = st.number_input("Fat (g)", 0, 1000, 15)
                notes = st.text_input("Description", placeholder="e.g., Chicken & rice")
                if st.form_submit_button("Log Meal", use_container_width=True):
                    r = _create("/macros/", {
                        "profile_id": pid, "entry_date": str(m_date),
                        "calories": float(cals), "protein_g": float(prot),
                        "carbs_g": float(carbs), "fat_g": float(fat),
                        "notes": notes or None,
                    }, get_macros.clear)
                    if r:
                        st.success("Meal logged!")
                        st.rerun()
        else:
            _section_hdr("AI Meal Analysis")
            food_desc = st.text_area("What did you eat?", placeholder="Grilled chicken breast, brown rice, broccoli", height=80)
            ai_date = st.date_input("Date", date.today(), key="ai_date")
            if st.button("Analyze with AI", use_container_width=True):
                if not food_desc or len(food_desc) < 3:
                    st.error("Please describe your meal")
                else:
                    with st.spinner("Analyzing..."):
                        try:
                            r = _client().post("/macros/analyze-food", json={"food_description": food_desc}, headers=_headers(), timeout=30.0)
                            if r.status_code == 200:
                                st.session_state.ai_nutrition = r.json()
                                st.session_state.ai_nutrition_date = str(ai_date)
                                st.session_state.ai_nutrition_desc = food_desc
                                st.rerun()
                            else:
                                st.error(f"Analysis failed: {r.json().get('detail','Error')}")
                        except Exception as e:
                            st.error(f"Error: {e}")

            data = st.session_state.get("ai_nutrition")
            if data:
                st.markdown("---")
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric("Calories", f"{data['calories']:.0f}")
                with c2: st.metric("Protein", f"{data['protein_g']:.1f}g")
                with c3: st.metric("Carbs",   f"{data['carbs_g']:.1f}g")
                with c4: st.metric("Fat",     f"{data['fat_g']:.1f}g")
                if data.get("analysis"): st.info(f"💭 {data['analysis']}")
                if st.button("Save Entry", use_container_width=True):
                    r = _create("/macros/", {
                        "profile_id": pid, "entry_date": st.session_state.ai_nutrition_date,
                        "calories": data["calories"], "protein_g": data["protein_g"],
                        "carbs_g": data["carbs_g"], "fat_g": data["fat_g"],
                        "notes": st.session_state.get("ai_nutrition_desc","")[:100],
                    }, get_macros.clear)
                    if r:
                        st.success("Saved!")
                        st.session_state.ai_nutrition = None
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    with tab_hist:
        macros = get_macros(token, pid)
        if not macros:
            st.info("No meals logged yet.")
            return
        by_date = defaultdict(list)
        for m in macros:
            by_date[m.get("entry_date", "")].append(m)
        for d in sorted(by_date.keys(), reverse=True)[:15]:
            entries = by_date[d]
            total_c = sum(e.get("calories", 0) for e in entries)
            with st.expander(f"{d} — {total_c:.0f} kcal ({len(entries)} meal{'s' if len(entries)!=1 else ''})"):
                for idx, e in enumerate(entries):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    with c1:
                        st.markdown(f"**{e.get('calories',0):.0f} kcal**")
                        if e.get("notes"): st.caption(e["notes"][:60])
                    with c2:
                        st.caption(f"P:{e.get('protein_g',0):.0f}g · C:{e.get('carbs_g',0):.0f}g · F:{e.get('fat_g',0):.0f}g")
                    with c3:
                        if st.button("×", key=f"del_mac_{e['id']}_{idx}"):
                            if _delete(f"/macros/{e['id']}"):
                                get_macros.clear()
                                st.rerun()


# ── My Progress / Analytics ───────────────────────────────────

def show_my_progress():
    if not HAS_PLOTLY:
        st.warning("Install plotly to view analytics: `pip install plotly`")
        return
    token = st.session_state.token
    pid   = str(st.session_state.selected_profile_id or "")
    if not pid:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-state-icon">📊</div>'
            '<div class="empty-state-title">No profile selected</div>'
            '<div class="empty-state-sub">Create a profile to unlock your performance score and analytics.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Create Profile", key="prog_create_profile", use_container_width=False):
            st.session_state.active_section = "Profile"
            st.rerun()
        return

    profile_name = st.session_state.get("selected_profile_name", "")
    workouts     = get_analytics_workouts(token, pid)
    metrics      = get_analytics_metrics(token, pid)
    macros       = get_analytics_macros(token, pid)
    step_data    = get_analytics_steps(token, pid)
    profile_list = get_profiles(token)
    today        = date.today()

    def _pd(v) -> date | None:
        try:
            return date.fromisoformat(str(v)) if v else None
        except Exception:
            return None

    # ── Derive targets ────────────────────────────────────────
    profile_obj = next((p for p in profile_list if p.get("id") == pid), {})
    weight_kg  = float(profile_obj.get("weight_kg") or 75)
    height_cm  = float(profile_obj.get("height_cm") or 175)
    age        = int(profile_obj.get("age") or 30)
    gender     = (profile_obj.get("gender") or "male").lower()
    goal       = (profile_obj.get("goal") or "fit").lower()
    bmr        = 10 * weight_kg + 6.25 * height_cm - 5 * age + (5 if gender == "male" else -161)
    tdee       = bmr * 1.55
    auto_cal     = round(tdee + (300 if goal == "muscle" else -500 if goal == "weight_loss" else 0))
    auto_protein = round(weight_kg * (2.0 if goal == "muscle" else 1.6))

    user_goals       = get_goals(token, pid)
    steps_target     = int(user_goals.get("daily_steps") or 10000)
    freq_target      = int(user_goals.get("weekly_workouts") or 4)
    cal_target       = int(user_goals.get("daily_calories") or auto_cal)
    protein_target_g = float(user_goals.get("daily_protein_g") or auto_protein)

    # ── Streak (always all-time, not range-dependent) ─────────
    streak = 0
    all_dates = {w.get("log_date") for w in workouts} | {m.get("entry_date") for m in macros}
    chk = today
    while str(chk) in all_dates:
        streak += 1; chk -= timedelta(days=1)

    # ── Time range selector (drives everything below) ─────────
    rc, _ = st.columns([3, 2])
    with rc:
        range_opt = st.radio(
            "Time range",
            ["1 week", "2 weeks", "1 month", "3 months", "Custom"],
            horizontal=True, index=2, key="progress_range",
        )

    if range_opt == "Custom":
        cc1, cc2, _ = st.columns([1, 1, 2])
        with cc1:
            custom_start = st.date_input("From", value=today - timedelta(days=29),
                                         max_value=today, key="progress_custom_start")
        with cc2:
            custom_end = st.date_input("To", value=today,
                                       max_value=today, key="progress_custom_end")
        if custom_start > custom_end:
            st.warning("Start date must be before end date.")
            custom_start = custom_end
        range_start = custom_start
        range_end   = custom_end
        range_days  = (custom_end - custom_start).days + 1
    else:
        range_days  = {"1 week": 7, "2 weeks": 14, "1 month": 30, "3 months": 90}[range_opt]
        range_start = today - timedelta(days=range_days - 1)
        range_end   = today

    # ── Metrics for the selected range ───────────────────────
    range_macros   = [m for m in macros    if range_start <= (_pd(m.get("entry_date")) or date.min) <= range_end]
    range_steps    = [s for s in step_data if range_start <= (_pd(s.get("entry_date")) or date.min) <= range_end]
    range_workouts = [w for w in workouts  if range_start <= (_pd(w.get("log_date"))   or date.min) <= range_end]

    avg_cals  = sum(m.get("calories",  0) for m in range_macros) / max(len(range_macros), 1) if range_macros else 0.0
    avg_prot  = sum(m.get("protein_g", 0) for m in range_macros) / max(len(range_macros), 1) if range_macros else 0.0
    avg_steps = sum(s.get("steps",     0) for s in range_steps)  / max(len(range_steps),  1) if range_steps  else 0.0

    # Workout frequency: sessions per week over the range
    weeks_in_range      = max(range_days / 7, 1)
    avg_workouts_per_wk = len(range_workouts) / weeks_in_range

    # ── Score calculation (range-based) ──────────────────────
    step_pct = min(100, int(avg_steps / steps_target * 100)) if steps_target and range_steps else 0
    cal_pct  = max(0, 100 - int(abs(avg_cals - cal_target) / max(cal_target, 1) * 100)) if avg_cals else 0
    prot_pct = min(100, int(avg_prot / protein_target_g * 100)) if protein_target_g and avg_prot else 0
    freq_pct = min(100, int(avg_workouts_per_wk / max(freq_target, 1) * 100))
    score    = min(100, int((step_pct + cal_pct + prot_pct + freq_pct) / 4) + min(streak, 10))

    if score >= 85:   grade, grade_color = "A", "#00FF87"
    elif score >= 70: grade, grade_color = "B", "#00C2FF"
    elif score >= 55: grade, grade_color = "C", "#FFB347"
    elif score >= 35: grade, grade_color = "D", "#FF8C00"
    else:             grade, grade_color = "F", "#FF6B6B"

    motivation = {
        "A": "Elite performance. You're crushing every goal — stay relentless.",
        "B": "Strong work. Tighten one metric to break into elite territory.",
        "C": "Building momentum. Consistency now means visible results in weeks.",
        "D": "Every logged entry counts. Keep showing up — progress compounds.",
        "F": "Today is the best time to start. One log changes everything.",
    }.get(grade, "Keep pushing forward.")

    # ── Score Cockpit ─────────────────────────────────────────
    st.markdown(_score_cockpit_html(score, grade, grade_color, motivation, streak), unsafe_allow_html=True)

    # ── Ring Cards ────────────────────────────────────────────
    range_label = range_opt if range_opt != "Custom" else "Custom range"
    st.markdown(
        f'<div class="progress-hdr"><div class="progress-hdr-text">Goal Tracking — {range_label}</div>'
        f'<div class="progress-hdr-line"></div></div>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(_ring_card(
            "Steps", step_pct,
            f"{avg_steps:,.0f} avg/day" if range_steps else "No data",
            f"Goal {steps_target:,}/day", "#00FF87", "0s",
        ), unsafe_allow_html=True)
    with c2:
        st.markdown(_ring_card(
            "Calories", cal_pct,
            f"{avg_cals:,.0f} kcal avg" if avg_cals else "No data",
            f"Target {cal_target:,} kcal", "#00C2FF", "0.07s",
        ), unsafe_allow_html=True)
    with c3:
        st.markdown(_ring_card(
            "Protein", prot_pct,
            f"{avg_prot:.0f}g avg/day" if avg_prot else "No data",
            f"Target {protein_target_g:.0f}g/day", "#FFB347", "0.14s",
        ), unsafe_allow_html=True)
    with c4:
        sessions_label = f"{len(range_workouts)} sessions"
        st.markdown(_ring_card(
            "Workouts", freq_pct,
            sessions_label,
            f"Goal {freq_target}×/wk avg",
            "#00FF87" if freq_pct >= 100 else "#FF6B6B", "0.21s",
        ), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Performance Bars ─────────────────────────────────────
    st.markdown('<div class="card card-accent">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="progress-hdr"><div class="progress-hdr-text">Performance Breakdown — {range_label}</div>'
        f'<div class="progress-hdr-line"></div></div>',
        unsafe_allow_html=True,
    )

    def _perf_bar(name: str, pct: int, val_label: str, color: str, delay: str) -> None:
        capped = min(pct, 100)
        st.markdown(
            f'<div class="perf-bar-row">'
            f'<div class="perf-bar-header">'
            f'<span class="perf-bar-name">{name}</span>'
            f'<span class="perf-bar-pct" style="color:{color};">{pct}%'
            f'&nbsp;<span style="font-size:.75rem;color:var(--muted);font-weight:400;">{val_label}</span></span>'
            f'</div>'
            f'<div class="perf-bar-track">'
            f'<div class="perf-bar-fill" style="width:{capped}%;background:{color};animation-delay:{delay};"></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    _perf_bar("Steps",
              step_pct,
              f"{avg_steps:,.0f} / {steps_target:,} avg/day" if range_steps else "No data yet — log in Wellness",
              "#00FF87", "0s")
    _perf_bar("Calorie accuracy",
              cal_pct,
              f"{avg_cals:,.0f} / {cal_target:,} kcal avg/day" if avg_cals else "No data yet — log in Nutrition",
              "#00C2FF", "0.06s")
    _perf_bar("Protein intake",
              prot_pct,
              f"{avg_prot:.0f}g / {protein_target_g:.0f}g avg/day" if avg_prot else "No data yet — log in Nutrition",
              "#FFB347", "0.12s")
    _perf_bar("Workout frequency",
              freq_pct,
              f"{len(range_workouts)} sessions · {avg_workouts_per_wk:.1f}/wk avg vs goal {freq_target}/wk",
              "#00FF87" if freq_pct >= 100 else "#FF6B6B", "0.18s")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # ── 2×2 Charts ────────────────────────────────────────────
    st.markdown(
        '<div class="progress-hdr"><div class="progress-hdr-text">Goal vs Actual</div>'
        '<div class="progress-hdr-line"></div></div>',
        unsafe_allow_html=True,
    )

    row1_l, row1_r = st.columns(2)

    x_range = [str(range_start), str(range_end)]

    with row1_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        _section_hdr(f"Steps — Goal {steps_target:,}/day")
        sd = sorted(
            [s for s in step_data if range_start <= (_pd(s.get("entry_date")) or date.min) <= range_end],
            key=lambda x: _pd(x.get("entry_date")) or date.min,
        )
        if sd:
            sdates = [str(_pd(s["entry_date"])) for s in sd]
            svals  = [s.get("steps", 0) for s in sd]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sdates, y=svals, mode="lines+markers", name="Steps",
                line=dict(color="#00FF87", width=2, shape="spline", smoothing=0.5),
                marker=dict(size=6, color=[_goal_color(v, steps_target) for v in svals],
                            line=dict(width=1.5, color="#0A0A0A")),
                fill="tozeroy", fillcolor="rgba(0,255,135,0.06)",
                hovertemplate="<b>%{x}</b><br>Steps: <b>%{y:,}</b><br>Goal: " + f"{steps_target:,}" + "<extra></extra>",
            ))
            fig.add_hline(y=steps_target, line=dict(color="rgba(0,255,135,0.45)", dash="dot", width=1.5),
                          annotation_text=f"goal {steps_target:,}", annotation_font_color="#6B7280",
                          annotation_font_size=9, annotation_position="top right")
            fig.update_xaxes(range=x_range)
            fig.update_yaxes(tickformat=",")
            _dark_chart(fig, 260)
        else:
            st.markdown('<div class="empty-state" style="padding:1.5rem;"><div class="empty-state-icon">👟</div>'
                        '<div class="empty-state-sub">Log steps in <strong>Wellness → Steps</strong></div></div>',
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with row1_r:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        _section_hdr(f"Calories — Target {cal_target:,} kcal/day")
        cal_sorted = sorted(
            [m for m in macros if range_start <= (_pd(m.get("entry_date")) or date.min) <= range_end],
            key=lambda x: _pd(x.get("entry_date")) or date.min,
        )
        if cal_sorted:
            cdates = [str(_pd(m["entry_date"])) for m in cal_sorted]
            cvals  = [m.get("calories", 0) for m in cal_sorted]
            def _cal_color(v):
                dev = abs(v - cal_target) / max(cal_target, 1)
                return "#00C2FF" if dev <= 0.10 else "#FFB347" if dev <= 0.25 else "#FF6B6B"
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=cdates, y=cvals, mode="lines+markers", name="Calories",
                line=dict(color="#00C2FF", width=2, shape="spline", smoothing=0.5),
                marker=dict(size=6, color=[_cal_color(v) for v in cvals],
                            line=dict(width=1.5, color="#0A0A0A")),
                fill="tozeroy", fillcolor="rgba(0,194,255,0.06)",
                hovertemplate="<b>%{x}</b><br>Calories: <b>%{y:,.0f} kcal</b><br>Target: " + f"{cal_target:,} kcal" + "<extra></extra>",
            ))
            fig.add_hline(y=cal_target, line=dict(color="rgba(0,194,255,0.45)", dash="dot", width=1.5),
                          annotation_text=f"target {cal_target:,}", annotation_font_color="#6B7280",
                          annotation_font_size=9, annotation_position="top right")
            fig.update_xaxes(range=x_range)
            fig.update_yaxes(tickformat=",")
            _dark_chart(fig, 260)
        else:
            st.markdown('<div class="empty-state" style="padding:1.5rem;"><div class="empty-state-icon">🥗</div>'
                        '<div class="empty-state-sub">Log meals in <strong>Nutrition</strong></div></div>',
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    row2_l, row2_r = st.columns(2)

    with row2_l:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        _section_hdr(f"Protein — Target {protein_target_g:.0f}g/day")
        prot_sorted = sorted(
            [m for m in macros if range_start <= (_pd(m.get("entry_date")) or date.min) <= range_end],
            key=lambda x: _pd(x.get("entry_date")) or date.min,
        )
        if prot_sorted:
            pdates = [str(_pd(m["entry_date"])) for m in prot_sorted]
            pvals  = [m.get("protein_g", 0) for m in prot_sorted]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=pdates, y=pvals, mode="lines+markers", name="Protein",
                line=dict(color="#FFB347", width=2, shape="spline", smoothing=0.5),
                marker=dict(size=6, color=[_goal_color(v, protein_target_g) for v in pvals],
                            line=dict(width=1.5, color="#0A0A0A")),
                fill="tozeroy", fillcolor="rgba(255,179,71,0.06)",
                hovertemplate="<b>%{x}</b><br>Protein: <b>%{y:.0f}g</b><br>Target: " + f"{protein_target_g:.0f}g" + "<extra></extra>",
            ))
            fig.add_hline(y=protein_target_g, line=dict(color="rgba(255,179,71,0.45)", dash="dot", width=1.5),
                          annotation_text=f"target {protein_target_g:.0f}g", annotation_font_color="#6B7280",
                          annotation_font_size=9, annotation_position="top right")
            fig.update_xaxes(range=x_range)
            _dark_chart(fig, 260)
        else:
            st.markdown('<div class="empty-state" style="padding:1.5rem;"><div class="empty-state-icon">💪</div>'
                        '<div class="empty-state-sub">Log meals in <strong>Nutrition</strong> to track protein</div></div>',
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with row2_r:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        _section_hdr(f"Workout Frequency — Goal {freq_target}×/week")
        freq: dict[str, int] = {}
        for w in workouts:
            d = _pd(w.get("log_date"))
            if not d or not (range_start <= d <= range_end): continue
            wk = (d - timedelta(days=d.weekday())).strftime("%d %b")
            freq[wk] = freq.get(wk, 0) + 1
        weeks = sorted(freq.items())
        if weeks:
            wlabels = [wk[0] for wk in weeks]
            wcounts = [wk[1] for wk in weeks]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=wlabels, y=wcounts, mode="lines+markers", name="Sessions",
                line=dict(color="#00FF87", width=2, shape="spline", smoothing=0.4),
                marker=dict(size=8, color=[_goal_color(v, freq_target) for v in wcounts],
                            line=dict(width=1.5, color="#0A0A0A")),
                fill="tozeroy", fillcolor="rgba(0,255,135,0.06)",
                hovertemplate="<b>Week of %{x}</b><br>Sessions: <b>%{y}</b><br>Goal: " + str(freq_target) + "/week<extra></extra>",
            ))
            fig.add_hline(y=freq_target, line=dict(color="rgba(0,255,135,0.45)", dash="dot", width=1.5),
                          annotation_text=f"goal {freq_target}×", annotation_font_color="#6B7280",
                          annotation_font_size=9, annotation_position="top right")
            fig.update_yaxes(dtick=1, tickformat="d")
            _dark_chart(fig, 260)
        else:
            st.markdown('<div class="empty-state" style="padding:1.5rem;"><div class="empty-state-icon">🏋️</div>'
                        '<div class="empty-state-sub">Log workouts to see weekly frequency</div></div>',
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Weight trend ──────────────────────────────────────────
    sorted_metrics = sorted(
        [m for m in metrics if m.get("weight_kg") and
         range_start <= (_pd(m.get("entry_date")) or date.min) <= range_end],
        key=lambda x: _pd(x.get("entry_date")) or date.min,
    )
    if sorted_metrics:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        _section_hdr("Body Weight Trend")
        wdates = [str(_pd(m["entry_date"])) for m in sorted_metrics]
        wvals  = [m["weight_kg"] for m in sorted_metrics]
        w_min  = min(wvals); w_max = max(wvals)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=wdates, y=wvals, mode="lines+markers", name="Weight",
            line=dict(color="#00FF87", width=2.5, shape="spline", smoothing=0.6),
            marker=dict(size=6, color="#00FF87", line=dict(width=1.5, color="#0A0A0A")),
            fill="tozeroy", fillcolor="rgba(0,255,135,0.05)",
            hovertemplate="<b>%{x}</b><br>Weight: <b>%{y:.1f} kg</b><extra></extra>",
        ))
        fig.add_hline(y=weight_kg, line=dict(color="rgba(255,179,71,0.35)", dash="dot", width=1.5),
                      annotation_text=f"profile {weight_kg:.1f} kg", annotation_font_color="#6B7280",
                      annotation_font_size=9, annotation_position="top right")
        fig.add_annotation(x=wdates[wvals.index(w_min)], y=w_min, text=f"low {w_min:.1f}kg",
                           showarrow=False, font=dict(size=9, color="#FF6B6B"), yshift=-14)
        fig.add_annotation(x=wdates[wvals.index(w_max)], y=w_max, text=f"high {w_max:.1f}kg",
                           showarrow=False, font=dict(size=9, color="#00FF87"), yshift=12)
        fig.update_xaxes(range=x_range)
        _dark_chart(fig, 220)
        st.markdown("</div>", unsafe_allow_html=True)


# ── Wellness ──────────────────────────────────────────────────

def show_wellness():
    token = st.session_state.token
    pid = str(st.session_state.selected_profile_id or "")

    t_hydra, t_body, t_steps = st.tabs(["Hydration", "Body Metrics", "Steps"])

    with t_hydra:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        _section_hdr("Log Water")
        with st.form("log_hydra"):
            h_date = st.date_input("Date", date.today(), key="h_date")
            h_ml   = st.number_input("Water (ml)", 0, 20000, 500, 250)
            h_note = st.text_input("Notes", key="h_note")
            if st.form_submit_button("Log Water", use_container_width=True):
                r = _create("/hydration/", {"profile_id": pid, "entry_date": str(h_date),
                    "water_ml": float(h_ml), "notes": h_note or None}, get_hydration.clear)
                if r: st.success("Logged!"); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        entries = get_hydration(token, pid)
        by_date = defaultdict(list)
        for e in entries:
            by_date[e.get("entry_date","")].append(e)
        for d in sorted(by_date.keys(), reverse=True)[:8]:
            total = sum(e.get("water_ml",0) for e in by_date[d])
            with st.expander(f"{d} — {total:.0f} ml"):
                for idx, e in enumerate(by_date[d]):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    with c1: st.markdown(f"**{e.get('water_ml',0):.0f} ml**")
                    with c2:
                        if e.get("notes"): st.caption(e["notes"][:50])
                    with c3:
                        if st.button("×", key=f"del_h_{e['id']}_{idx}"):
                            if _delete(f"/hydration/{e['id']}"): get_hydration.clear(); st.rerun()

    with t_body:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        _section_hdr("Log Body Metrics")
        with st.form("log_bm"):
            b_date = st.date_input("Date", date.today(), key="b_date")
            c1, c2 = st.columns(2)
            with c1:
                b_w  = st.number_input("Weight (kg)", 0.0, 500.0, 0.0, 0.1)
                b_bf = st.number_input("Body Fat %", 0.0, 100.0, 0.0, 0.5)
            with c2:
                b_wa = st.number_input("Waist (cm)", 0.0, 300.0, 0.0, 0.5)
                b_hr = st.number_input("Resting HR", 0, 250, 0)
            if st.form_submit_button("Log Metrics", use_container_width=True):
                r = _create("/body-metrics/", {"profile_id": pid, "entry_date": str(b_date),
                    "weight_kg": float(b_w) if b_w>0 else None, "body_fat_pct": float(b_bf) if b_bf>0 else None,
                    "waist_cm": float(b_wa) if b_wa>0 else None, "resting_hr": int(b_hr) if b_hr>0 else None}, get_body_metrics.clear)
                if r: st.success("Logged!"); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        for idx, e in enumerate(get_body_metrics(token, pid)[:10]):
            parts = [f"{e['weight_kg']:.1f}kg" if e.get("weight_kg") else "",
                     f"{e['body_fat_pct']:.1f}%BF" if e.get("body_fat_pct") else "",
                     f"{e['waist_cm']:.0f}cm" if e.get("waist_cm") else ""]
            c1, c2, c3 = st.columns([2, 3, 1])
            with c1: st.markdown(f"**{e.get('entry_date','')}**")
            with c2: st.caption(" · ".join(p for p in parts if p) or "No data")
            with c3:
                if st.button("×", key=f"del_bm_{e['id']}_{idx}"):
                    if _delete(f"/body-metrics/{e['id']}"): get_body_metrics.clear(); st.rerun()

    with t_steps:
        _STEPS_GOAL = int(get_goals(token, pid).get("daily_steps") or 10000) if pid else 10000
        st.markdown('<div class="card">', unsafe_allow_html=True)
        _section_hdr("Log Daily Steps")
        with st.form("log_steps"):
            st_date = st.date_input("Date", date.today(), key="st_date")
            c1, c2 = st.columns(2)
            with c1:
                st_steps = st.number_input("Steps", 0, 100000, 8000, 500)
                st_dist  = st.number_input("Distance (km, optional)", 0.0, 200.0, 0.0, 0.1)
            with c2:
                st_mins  = st.number_input("Active Minutes (optional)", 0, 1440, 0)
                st_note  = st.text_input("Notes", key="st_note")
            if st.form_submit_button("Log Steps", use_container_width=True):
                r = _create("/steps/", {
                    "profile_id": pid, "entry_date": str(st_date),
                    "steps": int(st_steps),
                    "distance_km": float(st_dist) if st_dist > 0 else None,
                    "active_minutes": int(st_mins) if st_mins > 0 else None,
                    "notes": st_note or None,
                }, get_steps.clear)
                if r: st.success("Logged!"); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        entries = get_steps(token, pid)[:14]
        if entries:
            for idx, e in enumerate(entries):
                pct = min(100, int(e.get("steps", 0) / _STEPS_GOAL * 100))
                bar_color = "#00FF87" if pct >= 100 else ("#FFB347" if pct >= 70 else "#FF6B6B")
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                with c1: st.markdown(f"**{e.get('entry_date','')}**")
                with c2: st.caption(f"{e.get('steps',0):,} steps  ({pct}% of goal)")
                with c3:
                    st.markdown(
                        f'<div style="height:4px;background:#1E1E1E;border-radius:2px;margin-top:.6rem;">'
                        f'<div style="height:100%;width:{pct}%;background:{bar_color};border-radius:2px;"></div></div>',
                        unsafe_allow_html=True,
                    )
                with c4:
                    if st.button("×", key=f"del_st_{e['id']}_{idx}"):
                        if _delete(f"/steps/{e['id']}"): get_steps.clear(); st.rerun()
        else:
            st.info("No steps logged yet. Start tracking your daily movement!")


# ── Profile ───────────────────────────────────────────────────

def show_profile():
    token = st.session_state.token
    user  = st.session_state.user or {}

    st.markdown('<div class="card">', unsafe_allow_html=True)
    _section_hdr("Your Account")
    st.markdown(f"""
    <div style="text-align:center; padding:1rem 0;">
      <div style="width:72px;height:72px;background:rgba(0,255,135,0.12);border:2px solid var(--accent);
           border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:2rem;margin:0 auto 0.75rem;">👤</div>
      <h3 style="margin:0;color:var(--text);">{user.get("name","User")}</h3>
      <p style="margin:0.2rem 0 0;color:var(--muted);">{user.get("email","")}</p>
    </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    _section_hdr("Fitness Profiles")
    profiles = get_profiles(token)
    if profiles:
        for p in profiles:
            is_sel = str(p.get("id")) == str(st.session_state.selected_profile_id)
            border = "border:2px solid var(--accent);background:rgba(0,255,135,0.06);" if is_sel else "border:1px solid var(--border);background:var(--surface2);"
            st.markdown(f"""
            <div style="{border}border-radius:var(--r-sm);padding:0.85rem 1rem;margin-bottom:0.5rem;">
              <strong style="color:var(--text);">{p.get("name","Unnamed")}</strong>
              {"<span style='float:right;color:var(--accent);font-size:0.8rem;font-weight:600;'>✓ Active</span>" if is_sel else ""}
            </div>""", unsafe_allow_html=True)
            if not is_sel and st.button(f"Select '{p.get('name','')}'", key=f"sel_{p['id']}"):
                st.session_state.selected_profile_id   = p["id"]
                st.session_state.selected_profile_name = p.get("name","")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("+ Create New Profile"):
        with st.form("create_profile"):
            pname  = st.text_input("Profile Name", placeholder="e.g., Bulk Phase")
            c1, c2 = st.columns(2)
            with c1:
                weight = st.number_input("Weight (kg)", 30.0, 300.0, 75.0, 0.5)
                age    = st.number_input("Age", 10, 120, 25)
            with c2:
                height = st.number_input("Height (cm)", 100.0, 250.0, 175.0, 0.5)
                gender = st.selectbox("Gender", ["male", "female", "other"])
            goal = st.selectbox("Goal", ["muscle","weight_loss","maintenance","endurance","strength","general_health"],
                format_func=lambda x: {"muscle":"Build Muscle","weight_loss":"Lose Weight","maintenance":"Maintain","endurance":"Endurance","strength":"Strength & Power","general_health":"General Health"}.get(x,x))
            if st.form_submit_button("Create Profile"):
                r = _create("/profile/", {"name": pname, "weight_kg": float(weight), "height_cm": float(height),
                    "age": int(age), "gender": gender, "goal": goal}, get_profiles.clear)
                if r:
                    st.success("Profile created!")
                    get_profiles.clear()
                    st.session_state.selected_profile_id   = r["id"]
                    st.session_state.selected_profile_name = r.get("name","")
                    st.rerun()

    # Goals editor — only shown when a profile is active
    active_pid = str(st.session_state.selected_profile_id or "")
    if active_pid:
        active_name = st.session_state.get("selected_profile_name", "Active Profile")

        # Compute auto targets for display hints
        profiles_g = get_profiles(token)
        p_obj_g = next((p for p in profiles_g if str(p.get("id")) == active_pid), {})
        w_kg_g  = float(p_obj_g.get("weight_kg") or 75)
        h_cm_g  = float(p_obj_g.get("height_cm") or 175)
        age_g   = int(p_obj_g.get("age") or 30)
        gen_g   = (p_obj_g.get("gender") or "male").lower()
        goal_g  = (p_obj_g.get("goal") or "fit").lower()
        tdee_g  = (10 * w_kg_g + 6.25 * h_cm_g - 5 * age_g + (5 if gen_g == "male" else -161)) * 1.55
        auto_cal_g  = round(tdee_g + (300 if goal_g == "muscle" else -500 if goal_g == "weight_loss" else 0))
        auto_prot_g = round(w_kg_g * (2.0 if goal_g == "muscle" else 1.6))

        with st.expander(f"Edit Goals — {active_name}"):
            g = get_goals(token, active_pid)
            with st.form("goals_form"):
                _section_hdr("Daily Targets")
                gc1, gc2 = st.columns(2)
                with gc1:
                    g_steps = st.number_input(
                        "Daily Steps",
                        min_value=0, max_value=100000,
                        value=int(g.get("daily_steps") or 10000),
                        step=500,
                    )
                    g_water = st.number_input(
                        "Daily Water (ml)",
                        min_value=0, max_value=10000,
                        value=int(g.get("daily_water_ml") or 2000),
                        step=100,
                    )
                    override_cals = st.checkbox(
                        "Set custom calorie target",
                        value=bool(g.get("daily_calories")),
                        help=f"Auto-computed from your TDEE: ~{auto_cal_g} kcal/day",
                    )
                    g_cals = st.number_input(
                        f"Daily Calories (kcal)  —  auto: {auto_cal_g}",
                        min_value=500, max_value=20000,
                        value=int(g.get("daily_calories") or auto_cal_g),
                        step=50,
                        disabled=not override_cals,
                    )
                with gc2:
                    g_wk = st.number_input(
                        "Workouts per Week",
                        min_value=0, max_value=14,
                        value=int(g.get("weekly_workouts") or 4),
                        step=1,
                    )
                    override_prot = st.checkbox(
                        "Set custom protein target",
                        value=bool(g.get("daily_protein_g")),
                        help=f"Auto-computed from body weight × goal multiplier: ~{auto_prot_g}g/day",
                    )
                    g_prot = st.number_input(
                        f"Daily Protein (g)  —  auto: {auto_prot_g}g",
                        min_value=10.0, max_value=500.0,
                        value=float(g.get("daily_protein_g") or float(auto_prot_g)),
                        step=5.0,
                        disabled=not override_prot,
                    )
                if st.form_submit_button("Save Goals"):
                    payload: dict = {
                        "daily_steps": g_steps,
                        "weekly_workouts": g_wk,
                        "daily_water_ml": float(g_water),
                    }
                    if override_cals:
                        payload["daily_calories"] = g_cals
                    if override_prot:
                        payload["daily_protein_g"] = g_prot
                    r = _put(f"/profile/{active_pid}/goals", payload)
                    if r:
                        get_goals.clear()
                        st.success("Goals saved.")


# ── AI Coach FAB ──────────────────────────────────────────────

def show_ai_fab() -> None:
    """Delegate to the extracted AI FAB module to keep app.py under 800 lines."""
    token = st.session_state.get("token", "") or ""
    pid   = str(st.session_state.get("selected_profile_id") or "")
    _ai_fab.render(token, pid)


# ── Main app shell ────────────────────────────────────────────

def show_main_app():
    token    = st.session_state.token
    profiles = get_profiles(token)
    pnames   = {p.get("name","Unnamed"): p for p in profiles}

    with st.sidebar:
        user_name = (st.session_state.user or {}).get("name", "Athlete")
        st.markdown(f"""
        <div style="padding:0.5rem 0 1.25rem 0;">
          <div style="display:flex;align-items:center;gap:.65rem;margin-bottom:.5rem;">
            <div style="width:36px;height:36px;background:#00FF87;border-radius:9px;
                 display:flex;align-items:center;justify-content:center;
                 font-size:13px;font-weight:800;color:#0A0A0A;letter-spacing:-.5px;
                 flex-shrink:0;box-shadow:0 2px 12px rgba(0,255,135,.3);">FL</div>
            <span style="font-size:1.15rem;font-weight:800;color:#fff;letter-spacing:-.02em;">FitLog</span>
          </div>
          <div style="font-size:.78rem;color:#6B7280;">{user_name}</div>
        </div>""", unsafe_allow_html=True)

        if pnames:
            pname_list = list(pnames.keys())
            sel_name   = st.session_state.get("selected_profile_name", "")
            if not sel_name or sel_name not in pname_list:
                sel_name = pname_list[0]
                st.session_state.selected_profile_id   = pnames[sel_name]["id"]
                st.session_state.selected_profile_name = sel_name
            cur_index = pname_list.index(sel_name)
            chosen    = st.selectbox("Active Profile", pname_list, index=cur_index)
            if chosen and pnames[chosen]["id"] != st.session_state.get("selected_profile_id"):
                st.session_state.selected_profile_id   = pnames[chosen]["id"]
                st.session_state.selected_profile_name = chosen
                st.rerun()
        else:
            st.caption("No profiles — create one in Profile")

        st.markdown(
            '<hr style="border:none;border-top:1px solid #1E1E1E;margin:1rem 0 0.5rem;">',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div style="font-size:.62rem;font-weight:700;color:#374151;letter-spacing:.1em;'
            'text-transform:uppercase;padding:0 0.5rem;margin-bottom:.3rem;">Menu</div>',
            unsafe_allow_html=True,
        )

        cur = st.session_state.get("active_section", "Dashboard")

        NAV_ICONS = {
            "Dashboard":   ("◈", "Dashboard"),
            "Workouts":    ("◉", "Workouts"),
            "Nutrition":   ("◎", "Nutrition"),
            "My Progress": ("◐", "Progress"),
            "Wellness":    ("◌", "Wellness"),
            "Profile":     ("◍", "Profile"),
        }

        for sec, (icon, label) in NAV_ICONS.items():
            if sec == cur:
                st.markdown(
                    f'<div data-nav-active style="display:flex;align-items:center;gap:.55rem;'
                    f'padding:.52rem .9rem;border-radius:8px;'
                    f'background:rgba(0,255,135,0.09);">'
                    f'<span style="font-size:.72rem;color:#00FF87;">{icon}</span>'
                    f'<span style="font-size:.83rem;font-weight:600;color:#00FF87;">{label}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button(f"{icon}  {label}", key=f"nav_{sec}", use_container_width=True):
                    st.session_state.active_section = sec
                    st.rerun()

        st.markdown(
            '<hr style="border:none;border-top:1px solid #1E1E1E;margin:.5rem 0 .3rem;">',
            unsafe_allow_html=True,
        )
        if st.button("Sign Out", key="signout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

    section = st.session_state.get("active_section", "Dashboard")
    if   section == "Workouts":    show_workouts()
    elif section == "Nutrition":   show_nutrition()
    elif section == "My Progress": show_my_progress()
    elif section == "Wellness":    show_wellness()
    elif section == "Profile":     show_profile()
    else:                          show_dashboard()

    show_ai_fab()

    st.markdown('<div style="text-align:center;padding:2rem 0 1rem;color:#374151;font-size:.78rem;">FitLog · Professional Fitness Tracking</div>', unsafe_allow_html=True)


# ── Entry ─────────────────────────────────────────────────────

if st.session_state.get("logged_in") and st.session_state.get("token"):
    show_main_app()
else:
    show_login()
