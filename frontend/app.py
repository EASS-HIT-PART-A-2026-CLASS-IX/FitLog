"""
FitLog Frontend – Professional Fitness Tracking Dashboard
Complete fitness tracking with authentication and AI coaching
"""
import streamlit as st
import httpx
from datetime import date
import json
from functools import lru_cache

# Configuration
API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")

st.set_page_config(
    page_title="FitLog",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🎨 MATERIAL DESIGN 3 - Professional Google-Style Theme
st.markdown("""
    <style>
    /* ═══════════════════════════════════════════════════════════════
       MATERIAL DESIGN 3 COLOR SYSTEM (Google Modern Design)
       ═══════════════════════════════════════════════════════════════ */
    
    :root {
        /* Primary Colors - Brand Identity */
        --md-primary: #6750a4;      /* Purple - Main brand color */
        --md-primary-container: #eaddff;
        --md-on-primary: #ffffff;
        
        /* Secondary Colors - Supporting brand color */
        --md-secondary: #625b71;    /* Taupe */
        --md-secondary-container: #e8def8;
        --md-on-secondary: #ffffff;
        
        /* Tertiary Colors - Accent */
        --md-tertiary: #7d5260;     /* Pink */
        --md-tertiary-container: #ffd8e4;
        --md-on-tertiary: #ffffff;
        
        /* Semantic Colors */
        --md-success: #10b981;      /* Emerald Green */
        --md-warning: #f59e0b;      /* Amber */
        --md-error: #ef4444;        /* Red */
        --md-info: #3b82f6;         /* Blue */
        
        /* Neutral Colors */
        --md-surface: #fffbfe;
        --md-surface-dim: #f3eff4;
        --md-surface-bright: #fffbfe;
        --md-outline: #79747e;
        --md-outline-variant: #cac7d0;
        
        /* Neutral Grays */
        --md-gray-50: #f9fafb;
        --md-gray-100: #f3f4f6;
        --md-gray-200: #e5e7eb;
        --md-gray-300: #d1d5db;
        --md-gray-400: #9ca3af;
        --md-gray-600: #4b5563;
        --md-gray-700: #374151;
        --md-gray-900: #111827;
        
        /* Shadows - Google Material Design */
        --md-shadow-1: 0 1px 2px rgba(0, 0, 0, 0.05);
        --md-shadow-2: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
        --md-shadow-3: 0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06);
        --md-shadow-4: 0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05);
        --md-shadow-5: 0 20px 25px rgba(0, 0, 0, 0.1), 0 10px 10px rgba(0, 0, 0, 0.04);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       GLOBAL STYLES
       ═══════════════════════════════════════════════════════════════ */
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
        background-color: var(--md-gray-50);
        color: var(--md-gray-900);
    }
    
    /* Main content area */
    .main {
        background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       BUTTONS - Elevated & Filled Style
       ═══════════════════════════════════════════════════════════════ */
    
    .stButton > button {
        background-color: var(--md-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: 100px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.5px !important;
        box-shadow: var(--md-shadow-2) !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
    }
    
    .stButton > button:hover {
        background-color: #5a47a0 !important;
        box-shadow: var(--md-shadow-4) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: var(--md-shadow-2) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       INPUT FIELDS - Material Design Style
       ═══════════════════════════════════════════════════════════════ */
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: var(--md-gray-100) !important;
        border: 2px solid var(--md-outline-variant) !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
        font-family: inherit !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        background-color: white !important;
        border-color: var(--md-primary) !important;
        box-shadow: 0 0 0 3px rgba(103, 80, 164, 0.1) !important;
        outline: none !important;
    }
    
    /* Input label styling */
    .stTextInput label,
    .stTextArea label,
    .stNumberInput label,
    .stSelectbox label {
        font-weight: 600 !important;
        color: var(--md-gray-900) !important;
        margin-bottom: 8px !important;
        font-size: 14px !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       TABS - Modern Design
       ═══════════════════════════════════════════════════════════════ */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background-color: transparent !important;
        border-bottom: 2px solid var(--md-outline-variant) !important;
        padding: 0 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 20px !important;
        border-radius: 0 !important;
        border-bottom: 3px solid transparent !important;
        color: var(--md-gray-600) !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: var(--md-primary) !important;
        border-bottom-color: var(--md-primary) !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--md-primary) !important;
        background-color: rgba(103, 80, 164, 0.05) !important;
    }
    
    .stTabs [data-baseweb="tab-content"] {
        padding-top: 24px !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       CARDS & CONTAINERS
       ═══════════════════════════════════════════════════════════════ */
    
    .stMetric {
        background: white !important;
        padding: 20px !important;
        border-radius: 16px !important;
        border: 1px solid var(--md-outline-variant) !important;
        box-shadow: var(--md-shadow-1) !important;
        transition: all 0.3s ease !important;
    }
    
    .stMetric:hover {
        box-shadow: var(--md-shadow-3) !important;
        border-color: var(--md-primary) !important;
    }
    
    /* Metric label */
    .stMetric label {
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
        color: var(--md-gray-600) !important;
        text-transform: uppercase !important;
    }
    
    /* Metric value */
    .stMetric .metric-value {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: var(--md-primary) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       SIDEBAR - Material Design
       ═══════════════════════════════════════════════════════════════ */
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5f3f9 0%, #faf8fc 100%) !important;
        border-right: 1px solid var(--md-outline-variant) !important;
    }
    
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        font-weight: 700 !important;
        color: var(--md-gray-900) !important;
        margin-top: 24px !important;
        margin-bottom: 12px !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       DIVIDERS & SEPARATORS
       ═══════════════════════════════════════════════════════════════ */
    
    hr {
        background: linear-gradient(90deg, transparent, var(--md-outline-variant), transparent) !important;
        border: none !important;
        height: 1px !important;
        margin: 24px 0 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       EXPANDERS & COLLAPSIBLE SECTIONS
       ═══════════════════════════════════════════════════════════════ */
    
    .streamlit-expander {
        border: 1px solid var(--md-outline-variant) !important;
        border-radius: 12px !important;
        background-color: white !important;
        margin: 8px 0 !important;
    }
    
    .streamlit-expanderHeader {
        padding: 16px !important;
        font-weight: 600 !important;
        color: var(--md-gray-900) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: var(--md-gray-50) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       INFO, WARNING, SUCCESS, ERROR BOXES
       ═══════════════════════════════════════════════════════════════ */
    
    .stSuccess {
        background-color: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid var(--md-success) !important;
        border-radius: 12px !important;
        padding: 16px !important;
    }
    
    .stSuccess > div > p {
        color: #065f46 !important;
        font-weight: 500 !important;
    }
    
    .stError {
        background-color: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid var(--md-error) !important;
        border-radius: 12px !important;
        padding: 16px !important;
    }
    
    .stError > div > p {
        color: #7f1d1d !important;
        font-weight: 500 !important;
    }
    
    .stWarning {
        background-color: rgba(245, 158, 11, 0.1) !important;
        border: 1px solid var(--md-warning) !important;
        border-radius: 12px !important;
        padding: 16px !important;
    }
    
    .stWarning > div > p {
        color: #78350f !important;
        font-weight: 500 !important;
    }
    
    .stInfo {
        background-color: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid var(--md-info) !important;
        border-radius: 12px !important;
        padding: 16px !important;
    }
    
    .stInfo > div > p {
        color: #1e3a8a !important;
        font-weight: 500 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       TYPOGRAPHY
       ═══════════════════════════════════════════════════════════════ */
    
    h1 {
        font-size: 32px !important;
        font-weight: 700 !important;
        color: var(--md-gray-900) !important;
        margin-bottom: 24px !important;
        letter-spacing: -0.5px !important;
    }
    
    h2 {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: var(--md-gray-900) !important;
        margin-top: 24px !important;
        margin-bottom: 16px !important;
    }
    
    h3 {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: var(--md-gray-900) !important;
        margin-top: 16px !important;
        margin-bottom: 12px !important;
    }
    
    p, span, label {
        font-size: 14px !important;
        line-height: 1.6 !important;
        color: var(--md-gray-700) !important;
    }
    
    /* Caption text */
    .caption {
        font-size: 12px !important;
        color: var(--md-gray-600) !important;
        font-weight: 500 !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       FORMS
       ═══════════════════════════════════════════════════════════════ */
    
    .stForm {
        background: white !important;
        padding: 24px !important;
        border-radius: 16px !important;
        border: 1px solid var(--md-outline-variant) !important;
        box-shadow: var(--md-shadow-1) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       COLUMNS & LAYOUT
       ═══════════════════════════════════════════════════════════════ */
    
    [data-testid="column"] {
        padding: 0 12px !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       SCROLLBAR STYLING
       ═══════════════════════════════════════════════════════════════ */
    
    /* Webkit browsers */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--md-gray-100);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--md-outline);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--md-primary);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       TRANSITIONS & ANIMATIONS
       ═══════════════════════════════════════════════════════════════ */
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    [data-testid="stMetricContainer"] {
        animation: fadeIn 0.4s ease forwards;
    }
    
    .stAlert {
        animation: slideInRight 0.3s ease forwards;
    }
    
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "token" not in st.session_state:
    st.session_state.token = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "selected_profile_id" not in st.session_state:
    st.session_state.selected_profile_id = None

# OPTIMIZATION: Persistent HTTP client (created once per session)
if "api_client" not in st.session_state:
    st.session_state.api_client = None

# AI Chatbot state
if "chat_open" not in st.session_state:
    st.session_state.chat_open = False
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


def get_api_with_auth() -> httpx.Client:
    """
    Get authenticated HTTP client with optimal performance settings.
    Reuses connections and enables HTTP/2 for faster requests.
    """
    token = st.session_state.get("token", "")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return httpx.Client(
        base_url=API_BASE,
        timeout=10.0,  # Reduced timeout for faster failure detection
        headers=headers,
        limits=httpx.Limits(
            max_connections=20,  # Increased connection pool
            max_keepalive_connections=10,  # More keep-alive connections
        ),
        http2=True,  # Enable HTTP/2 for faster multiplexing
    )


# ─────────────────────────────────────────────
# API Functions (Optimized with caching)
# ─────────────────────────────────────────────

def api_register(email: str, password: str, name: str) -> dict:
    """Register a new user (no caching - one-time call)."""
    try:
        client = httpx.Client(base_url=API_BASE, timeout=10.0)
        response = client.post(
            "/auth/register",
            json={"email": email, "password": password, "name": name}
        )
        client.close()
        if response.status_code == 201:
            return response.json()
        else:
            st.error(f"Registration error: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"❌ Registration failed: {e}")
        return None


def api_login(email: str, password: str) -> dict:
    """Login user (no caching - one-time call)."""
    try:
        client = httpx.Client(base_url=API_BASE, timeout=10.0)
        response = client.post(
            "/auth/login",
            json={"email": email, "password": password}
        )
        client.close()
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Login error: {response.json().get('detail', 'Invalid credentials')}")
            return None
    except Exception as e:
        st.error(f"❌ Login failed: {e}")
        return None


@st.cache_data(ttl=60)  # Cache for 60s (good for read-heavy workouts)
def list_profiles():
    """Fetch all profiles with 60s cache."""
    try:
        client = get_api_with_auth()
        response = client.get("/profile/")
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.warning(f"⚠️ Offline: {e}")
        return []


def create_profile(data):
    """Create a new profile and invalidate cache."""
    try:
        client = get_api_with_auth()
        response = client.post("/profile/", json=data)
        if response.status_code == 201:
            # Clear the cache so next list_profiles call fetches fresh data
            list_profiles.clear()
            return response.json()
        return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


@st.cache_data(ttl=120)  # Cache for 2 min
def get_protein_target(profile_id):
    """Get protein target with 120s cache."""
    try:
        client = get_api_with_auth()
        response = client.get(f"/profile/{profile_id}/protein-target")
        return response.json() if response.status_code == 200 else None
    except:
        return None


@st.cache_data(ttl=60)  # Cache for 60s
def list_exercises():
    """Fetch all exercises with 60s cache."""
    try:
        client = get_api_with_auth()
        response = client.get("/exercises/")
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.warning(f"⚠️ Exercises offline: {e}")
        return []


def create_exercise(data):
    """Create exercise and invalidate cache."""
    try:
        client = get_api_with_auth()
        response = client.post("/exercises/", json=data)
        if response.status_code == 201:
            list_exercises.clear()  # Invalidate cache
            return response.json()
        return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


@st.cache_data(ttl=45)  # Cache for 45s (workouts change frequently)
@st.cache_data(ttl=30)  # Cache for 30s (workouts change frequently)
def list_workout_logs():
    """Fetch latest workout logs with 30s cache and pagination."""
    try:
        client = get_api_with_auth()
        # Limit to 50 most recent logs for better performance
        response = client.get("/logs/?limit=50&offset=0")
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.warning(f"⚠️ Workouts offline: {e}")
        return []


def create_workout_log(data):
    """Log a workout and invalidate cache."""
    try:
        client = get_api_with_auth()
        response = client.post("/logs/", json=data)
        
        # Success
        if response.status_code == 201:
            list_workout_logs.clear()  # Invalidate cache
            return response.json()
        
        # Handle errors with details
        try:
            error_detail = response.json().get("detail", response.text)
        except:
            error_detail = response.text
        
        st.error(f"❌ API Error ({response.status_code}): {error_detail}")
        return None
        
    except Exception as e:
        st.error(f"❌ Connection Error: {str(e)}")
        return None


def update_workout_log(log_id: str, data):
    """Update a workout log and invalidate cache."""
    try:
        client = get_api_with_auth()
        response = client.put(f"/logs/{log_id}", json=data)
        
        if response.status_code == 200:
            list_workout_logs.clear()  # Invalidate cache
            return response.json()
        
        try:
            error_detail = response.json().get("detail", response.text)
        except:
            error_detail = response.text
        
        st.error(f"❌ API Error ({response.status_code}): {error_detail}")
        return None
        
    except Exception as e:
        st.error(f"❌ Connection Error: {str(e)}")
        return None


def delete_workout_log(log_id: str):
    """Delete a workout log and invalidate cache."""
    try:
        client = get_api_with_auth()
        response = client.delete(f"/logs/{log_id}")
        
        if response.status_code == 204:
            list_workout_logs.clear()  # Invalidate cache
            return True
        
        try:
            error_detail = response.json().get("detail", response.text)
        except:
            error_detail = response.text
        
        st.error(f"❌ API Error ({response.status_code}): {error_detail}")
        return False
        
    except Exception as e:
        st.error(f"❌ Connection Error: {str(e)}")
        return False


@st.cache_data(ttl=45)  # Cache for 45s (nutrition changes often)
def list_macros():
    """Fetch all macros with 45s cache."""
    try:
        client = get_api_with_auth()
        response = client.get("/macros/")
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.warning(f"⚠️ Nutrition offline: {e}")
        return []


def create_macro(data):
    """Log macros and invalidate cache."""
    try:
        client = get_api_with_auth()
        response = client.post("/macros/", json=data)
        if response.status_code == 201:
            list_macros.clear()  # Invalidate cache
            return response.json()
        return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


def update_macro(entry_id: str, data):
    """Update a macro entry and invalidate cache."""
    try:
        client = get_api_with_auth()
        response = client.put(f"/macros/{entry_id}", json=data)
        
        if response.status_code == 200:
            list_macros.clear()  # Invalidate cache
            return response.json()
        
        try:
            error_detail = response.json().get("detail", response.text)
        except:
            error_detail = response.text
        
        st.error(f"❌ API Error ({response.status_code}): {error_detail}")
        return None
        
    except Exception as e:
        st.error(f"❌ Connection Error: {str(e)}")
        return None


def delete_macro(entry_id: str):
    """Delete a macro entry and invalidate cache."""
    try:
        client = get_api_with_auth()
        response = client.delete(f"/macros/{entry_id}")
        
        if response.status_code == 204:
            list_macros.clear()  # Invalidate cache
            return True
        
        try:
            error_detail = response.json().get("detail", response.text)
        except:
            error_detail = response.text
        
        st.error(f"❌ API Error ({response.status_code}): {error_detail}")
        return False
        
    except Exception as e:
        st.error(f"❌ Connection Error: {str(e)}")
        return False


def chat_with_ai(profile_id: str, message: str) -> dict:
    """Chat with AI (no caching - real-time conversation)."""
    try:
        client = get_api_with_auth()
        response = client.post("/ai/chat", json={
            "profile_id": profile_id,
            "message": message
        })
        if response.status_code == 200:
            return response.json()
        else:
            error_detail = response.json().get("detail", response.text)
            return {"reply": f"❌ Error: {error_detail}"}
    except Exception as e:
        return {"reply": f"❌ Error: {str(e)}"}


def floating_ai_chatbot():
    """Large side panel FitCoach chatbot - positioned on the right."""
    # Initialize chat state
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    
    # Add CSS for FitCoach styling
    st.markdown("""
        <style>
        .fitcoach-toggle {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 9999;
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6750a4 0%, #7d5260 100%);
            border: none;
            cursor: pointer;
            font-size: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 24px rgba(103, 80, 164, 0.4);
            transition: all 0.3s ease;
        }
        .fitcoach-toggle:hover {
            transform: scale(1.1);
            box-shadow: 0 12px 32px rgba(103, 80, 164, 0.5);
        }
        .fitcoach-panel {
            background: white;
            border-radius: 16px;
            border: 2px solid #6750a4;
            box-shadow: 0 10px 40px rgba(103, 80, 164, 0.25);
            display: flex;
            flex-direction: column;
            height: 600px;
            margin-top: 16px;
        }
        .fitcoach-panel-header {
            background: linear-gradient(135deg, #6750a4 0%, #7d5260 100%);
            color: white;
            padding: 20px;
            border-radius: 14px 14px 0 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .fitcoach-panel-header-emoji {
            font-size: 40px;
        }
        .fitcoach-panel-header-text h3 {
            margin: 0;
            font-size: 20px;
            font-weight: 700;
        }
        .fitcoach-panel-header-text p {
            margin: 4px 0 0 0;
            font-size: 12px;
            opacity: 0.9;
        }
        .fitcoach-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: #f9fafb;
        }
        .fitcoach-message-user {
            display: flex;
            justify-content: flex-end;
            margin-bottom: 12px;
        }
        .fitcoach-message-user-text {
            background: #6750a4;
            color: white;
            padding: 12px 16px;
            border-radius: 12px 12px 0 12px;
            max-width: 85%;
            font-size: 13px;
            word-wrap: break-word;
        }
        .fitcoach-message-assistant {
            display: flex;
            justify-content: flex-start;
            margin-bottom: 12px;
        }
        .fitcoach-message-assistant-text {
            background: white;
            color: #111827;
            padding: 12px 16px;
            border-radius: 12px 12px 12px 0;
            border-left: 4px solid #6750a4;
            max-width: 85%;
            font-size: 13px;
            word-wrap: break-word;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Toggle button at bottom right
    col_space, col_btn = st.columns([20, 1])
    with col_btn:
        if st.button("🏋️", key="fitcoach_toggle", help="Chat with FitCoach"):
            st.session_state.chat_open = not st.session_state.chat_open
            st.rerun()
    
    # Show side panel when open
    if st.session_state.chat_open:
        st.markdown("<div class='fitcoach-panel'>", unsafe_allow_html=True)
        
        # Header
        st.markdown("""
            <div class="fitcoach-panel-header">
                <div class="fitcoach-panel-header-emoji">🏋️‍♂️</div>
                <div class="fitcoach-panel-header-text">
                    <h3>FitCoach</h3>
                    <p>Your Personal AI Fitness Trainer</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Chat messages area
        if st.session_state.get("selected_profile_id"):
            st.markdown("<div class='fitcoach-messages'>", unsafe_allow_html=True)
            
            # Display welcome message
            if not st.session_state.get("chat_messages"):
                st.markdown("""
                    <div style="text-align: center; padding: 12px 0;">
                        <p style="font-size: 13px; color: #6b7280; margin: 0;">
                            <strong style="color: #6750a4;">💡 Welcome to FitCoach!</strong><br>
                            Your personal AI fitness trainer is ready to help. Ask me about workouts, nutrition, progress, and more!
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Display chat history
            for msg in st.session_state.get("chat_messages", []):
                if msg["role"] == "user":
                    st.markdown(f"""
                        <div class="fitcoach-message-user">
                            <div class="fitcoach-message-user-text">{msg['content']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="fitcoach-message-assistant">
                            <div class="fitcoach-message-assistant-text">{msg['content']}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Input area
            st.divider()
            col_input, col_send = st.columns([4, 1])
            
            with col_input:
                chat_input = st.text_input(
                    "Ask FitCoach...",
                    placeholder="e.g., protein goal? best exercises?",
                    key="fitcoach_input_main",
                    label_visibility="collapsed"
                )
            
            with col_send:
                send_clicked = st.button("➤", key="fitcoach_send_main", help="Send message")
            
            if send_clicked and chat_input:
                # Add user message
                if "chat_messages" not in st.session_state:
                    st.session_state.chat_messages = []
                
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": chat_input
                })
                
                # Get AI response
                with st.spinner("🏋️ FitCoach is analyzing..."):
                    response = chat_with_ai(str(st.session_state.selected_profile_id), chat_input)
                
                # Add assistant message
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response.get("reply", "Sorry, I couldn't process that.")
                })
                
                st.rerun()
        else:
            st.warning("⚠️ **Select a fitness profile first** to chat with FitCoach!")
        
        # Close button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Close Panel ✕", use_container_width=True, key="close_fitcoach_panel"):
                st.session_state.chat_open = False
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Calendar Helper Functions
# ─────────────────────────────────────────────

def display_workout_calendar(logs):
    """Display calendar with workout dates highlighted."""
    import calendar
    from datetime import datetime
    
    if not logs:
        st.info("No workouts logged yet. Start logging to see your calendar!")
        return
    
    # Get unique dates from logs
    workout_dates = set()
    logs_by_date = {}
    for log in logs:
        log_date = log.get('log_date')
        if log_date:
            workout_dates.add(log_date)
            if log_date not in logs_by_date:
                logs_by_date[log_date] = []
            logs_by_date[log_date].append(log)
    
    # Month/year selector
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        current_month = st.session_state.get('workout_cal_month', date.today().month)
    with col2:
        current_year = st.session_state.get('workout_cal_year', date.today().year)
    with col3:
        pass
    
    # Display calendar
    cal = calendar.monthcalendar(current_year, current_month)
    month_name = calendar.month_name[current_month]
    
    st.subheader(f"📅 {month_name} {current_year}")
    
    # Header row
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for i, day in enumerate(days):
        cols[i].write(f"**{day}**")
    
    # Calendar grid
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                date_str = f"{current_year}-{current_month:02d}-{day:02d}"
                has_workout = date_str in workout_dates
                if has_workout:
                    cols[i].button(f"💪 {day}", key=f"wod_{date_str}", use_container_width=True)
                else:
                    cols[i].write(f"{day}")
    
    # Show details for selected date
    st.divider()
    st.subheader("📋 Workouts by Date")
    selected_date = st.selectbox(
        "Select a date",
        sorted(list(workout_dates)),
        key="workout_date_select"
    )
    
    if selected_date in logs_by_date:
        st.write(f"**{selected_date}**")
        for log in logs_by_date[selected_date]:
            st.write(f"💪 **{log.get('sets')}×{log.get('reps')}** @ {log.get('weight_kg')} kg")
            if log.get('notes'):
                st.caption(f"📝 {log['notes']}")


def display_nutrition_calendar(macros):
    """Display calendar with nutrition logging dates highlighted."""
    import calendar
    from datetime import datetime
    
    if not macros:
        st.info("No nutrition logged yet. Start logging to see your calendar!")
        return
    
    # Get unique dates from macros
    nutrition_dates = set()
    macros_by_date = {}
    for m in macros:
        entry_date = m.get('entry_date')
        if entry_date:
            nutrition_dates.add(entry_date)
            if entry_date not in macros_by_date:
                macros_by_date[entry_date] = []
            macros_by_date[entry_date].append(m)
    
    # Month/year selector
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        current_month = st.session_state.get('nutrition_cal_month', date.today().month)
    with col2:
        current_year = st.session_state.get('nutrition_cal_year', date.today().year)
    with col3:
        pass
    
    # Display calendar
    cal = calendar.monthcalendar(current_year, current_month)
    month_name = calendar.month_name[current_month]
    
    st.subheader(f"📅 {month_name} {current_year}")
    
    # Header row
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for i, day in enumerate(days):
        cols[i].write(f"**{day}**")
    
    # Calendar grid
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].write("")
            else:
                date_str = f"{current_year}-{current_month:02d}-{day:02d}"
                has_nutrition = date_str in nutrition_dates
                if has_nutrition:
                    cols[i].button(f"🍽️ {day}", key=f"nut_{date_str}", use_container_width=True)
                else:
                    cols[i].write(f"{day}")
    
    # Show details for selected date
    st.divider()
    st.subheader("🥗 Nutrition by Date")
    selected_date = st.selectbox(
        "Select a date",
        sorted(list(nutrition_dates), reverse=True),
        key="nutrition_date_select"
    )
    
    if selected_date in macros_by_date:
        st.write(f"**{selected_date}**")
        for m in macros_by_date[selected_date]:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Calories", f"{m['calories']:.0f}")
            with col2:
                st.metric("Protein", f"{m['protein_g']:.1f}g")
            with col3:
                st.metric("Carbs", f"{m['carbs_g']:.1f}g")
            with col4:
                st.metric("Fat", f"{m['fat_g']:.1f}g")
            if m.get('notes'):
                st.caption(f"📝 {m['notes']}")


# ─────────────────────────────────────────────
# Authentication Pages
# ─────────────────────────────────────────────

def login_page():
    """Professional login page with Material Design styling."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div style="text-align: center; margin: 60px 0 40px 0;">
                <div style="
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 88px;
                    height: 88px;
                    background: linear-gradient(135deg, #6750a4 0%, #7d5260 100%);
                    border-radius: 16px;
                    font-size: 48px;
                    box-shadow: 0 8px 24px rgba(103, 80, 164, 0.3);
                    margin: 0 auto 24px auto;
                ">
                    💪📊
                </div>
                <h1 style="margin: 16px 0 8px 0; font-size: 36px; font-weight: 800; color: #111827;">FitLog</h1>
                <p style="color: #6b7280; font-size: 16px; margin: 0;">Your Personal Fitness & Nutrition Companion</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        tab1, tab2 = st.tabs(["🔓 Login", "✨ Register"])
        
        with tab1:
            st.subheader("Welcome Back")
            email = st.text_input("Email Address", placeholder="you@example.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")
            
            col_btn, col_space = st.columns([1, 3])
            with col_btn:
                if st.button("🚀 Sign In", use_container_width=True, key="login_btn"):
                    if not email or not password:
                        st.error("⚠️ Please enter email and password")
                    else:
                        result = api_login(email, password)
                        if result:
                            st.session_state.logged_in = True
                            st.session_state.token = result.get("access_token")
                            st.session_state.user_id = result.get("user_id")
                            st.session_state.user_name = result.get("name")
                            st.success(f"✅ Welcome back, {result.get('name')}!")
                            st.rerun()
        
        with tab2:
            st.subheader("Create an Account")
            name = st.text_input("Full Name", placeholder="Alexander Fitness", key="register_name")
            email = st.text_input("Email Address", placeholder="you@example.com", key="register_email")
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Min 8 characters",
                key="register_password"
            )
            password_confirm = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="••••••••",
                key="register_confirm"
            )
            
            col_btn, col_space = st.columns([1, 3])
            with col_btn:
                if st.button("✨ Get Started", use_container_width=True, key="register_btn"):
                    if not name or not email or not password:
                        st.error("⚠️ Please fill in all fields")
                    elif password != password_confirm:
                        st.error("⚠️ Passwords don't match")
                    elif len(password) < 8:
                        st.error("⚠️ Password must be at least 8 characters")
                    else:
                        result = api_register(email, password, name)
                        if result:
                            st.session_state.logged_in = True
                            st.session_state.token = result.get("access_token")
                            st.session_state.user_id = result.get("user_id")
                            st.session_state.user_name = result.get("name")
                            st.success(f"✅ Account created! Welcome, {result.get('name')}!")
                            st.rerun()


def main_app():
    """Main application with professional Material Design layout."""
    # Professional Header with Material Design
    st.markdown("""
        <div style="
            padding: 16px 0 20px 0;
            margin-bottom: 20px;
            background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
            border-radius: 12px;
            position: relative;
        ">
    """, unsafe_allow_html=True)
    
    header_col1, header_col2 = st.columns([2, 1], vertical_alignment="center")
    
    with header_col1:
        st.markdown("""
            <div style="display: flex; align-items: center; gap: 16px; padding: 0 12px;">
                <div style="
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 56px;
                    height: 56px;
                    background: linear-gradient(135deg, #6750a4 0%, #7d5260 100%);
                    border-radius: 12px;
                    font-size: 32px;
                    box-shadow: 0 4px 12px rgba(103, 80, 164, 0.25);
                ">
                    💪📊
                </div>
                <div>
                    <h1 style="margin: 0; color: #6750a4; font-size: 32px; font-weight: 800;">FitLog</h1>
                    <p style="margin: 8px 0 0 0; color: #6b7280; font-size: 15px; font-weight: 500;">Welcome back, <strong style="color: #6750a4;">{}</strong></p>
                </div>
            </div>
        """.format(st.session_state.user_name), unsafe_allow_html=True)
    
    with header_col2:
        # Compact Logout button in top right
        col_space, col_logout = st.columns([3, 1])
        with col_logout:
            if st.button("🚪", key="logout_top", help="Logout"):
                st.session_state.logged_in = False
                st.session_state.token = None
                st.session_state.user_id = None
                st.session_state.user_name = None
                st.session_state.selected_profile_id = None
                st.success("✅ Logged out successfully!")
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    
    # ═══════════════════════════════════════════
    # SIDEBAR - Profile & Settings
    # ═══════════════════════════════════════════
    with st.sidebar:
        # Logo in Sidebar
        st.markdown("""
            <div style="text-align: center; padding: 12px 0 20px 0;">
                <div style="
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 60px;
                    height: 60px;
                    background: linear-gradient(135deg, #6750a4 0%, #7d5260 100%);
                    border-radius: 14px;
                    font-size: 36px;
                    box-shadow: 0 4px 12px rgba(103, 80, 164, 0.25);
                    margin: 0 auto;
                ">
                    💪📊
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 👤 Fitness Profile")
        st.divider()
        
        profiles = list_profiles()
        
        if profiles:
            profile_names = [f"{p['name']} ({p['goal'].upper()})" for p in profiles]
            selected_idx = st.selectbox(
                "Select Profile",
                range(len(profiles)),
                format_func=lambda i: profile_names[i],
                key="profile_select"
            )
            st.session_state.selected_profile_id = profiles[selected_idx]["id"]
            selected_profile = profiles[selected_idx]
        else:
            selected_profile = None
            st.session_state.selected_profile_id = None
        
        # Settings Section in Sidebar - Collapsible
        with st.expander("⚙️ Settings", expanded=False):
            # Account Info
            st.markdown("**Account Information**")
            info_col1, info_col2 = st.columns(2)
            with info_col1:
                st.metric("Status", "Active ✅")
            with info_col2:
                st.metric("Profiles", len(profiles) if profiles else 0)
            
            st.markdown("### Security")
            st.info("🔒 Your account is protected with PBKDF2 password hashing and JWT tokens")
            
            # Quick stats
            st.markdown("### Your Statistics")
            exercises = list_exercises()
            logs = list_workout_logs()
            macros = list_macros()
            
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            with stat_col1:
                st.metric("Exercises", len(exercises))
            with stat_col2:
                st.metric("Workouts", len(logs))
            with stat_col3:
                st.metric("Tracked Days", len(macros))
    
    # Main tabs with professional icons
    tabs = st.tabs([
        "📊 Dashboard",
        "👤 Profile",
        "💪 Training",
        "🥗 Nutrition",
    ])
    
    # ─────────────────────────────────────────────
    # Tab 0: Dashboard
    # ─────────────────────────────────────────────
    with tabs[0]:
        st.title("� Dashboard")
        
        if selected_profile:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💪 Name", selected_profile["name"])
            with col2:
                st.metric("⚖️ Weight", f"{selected_profile['weight_kg']} kg")
            with col3:
                st.metric("📏 Height", f"{selected_profile['height_cm']} cm")
            with col4:
                st.metric("🎯 Goal", selected_profile["goal"].upper())
            
            st.divider()
            
            # Protein Calculator
            st.subheader("🥩 Daily Protein Target")
            protein = get_protein_target(st.session_state.selected_profile_id)
            if protein:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Protein/Day", f"{protein['protein_g']} g")
                with col2:
                    st.metric("Multiplier", f"{protein['multiplier_g_per_kg']} g/kg")
                with col3:
                    st.metric("Based on", f"{protein['weight_kg']} kg")
                st.info(protein["recommendation"])
            
            st.divider()
            
            # Quick Stats
            st.subheader("📊 Your Statistics")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Workouts", len(logs))
            with col2:
                st.metric("Exercises", len(exercises))
            with col3:
                st.metric("Nutrition Days", len(macros))
        else:
            st.warning("⚠️ Create a fitness profile to get started!")
    
    # ─────────────────────────────────────────────
    # Tab 1: Profile Management
    # ─────────────────────────────────────────────
    with tabs[1]:
        st.title("👤 Fitness Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("➕ Create New Profile")
            with st.form("create_profile"):
                name = st.text_input("Profile Name", placeholder="My Fitness Journey")
                weight = st.number_input("Weight (kg)", min_value=30, max_value=500, value=80)
                height = st.number_input("Height (cm)", min_value=100, max_value=250, value=175)
                age = st.number_input("Age", min_value=10, max_value=120, value=25)
                gender = st.selectbox("Gender", ["male", "female", "other"])
                goal = st.selectbox("Goal", ["fit", "muscle"])
                
                if st.form_submit_button("✨ Create Profile", use_container_width=True):
                    new = create_profile({
                        "name": name,
                        "weight_kg": weight,
                        "height_cm": height,
                        "age": age,
                        "gender": gender,
                        "goal": goal,
                    })
                    if new:
                        st.success(f"✅ Profile '{name}' created!")
                        st.rerun()
        
        with col2:
            st.subheader("📋 Your Profiles")
            if profiles:
                for p in profiles:
                    st.write(f"👤 **{p['name']}**")
                    st.caption(f"🎯 {p['goal']} | ⚖️ {p['weight_kg']} kg | 📏 {p['height_cm']} cm | 🎂 {p['age']} yrs")
            else:
                st.info("No profiles yet. Create one to get started!")
    
    # ─────────────────────────────────────────────
    # Tab 2: Training (Combined Exercises & Workouts)
    # ─────────────────────────────────────────────
    with tabs[2]:
        st.title("🏋️ Training & Exercises")
        
        training_tabs = st.tabs(["🏋️ Exercise Library", "📋 Log Workout", "📅 Calendar"])
        
        # ─────────────────────────────────────────────
        # Subtab 1: Exercise Library (Add & View)
        # ─────────────────────────────────────────────
        with training_tabs[0]:
            st.subheader("📚 Manage Your Exercise Library")
            st.write("Add new exercises or view all available exercises in your library.")
            
            col_add, col_list = st.columns([1, 1])
            
            # Column 1: Add Exercise Form
            with col_add:
                st.markdown("### ➕ Add New Exercise")
                
                # Form to add exercise
                with st.form("add_exercise_form", clear_on_submit=True):
                    ex_name = st.text_input(
                        "Exercise Name *",
                        placeholder="e.g., Barbell Squat"
                    )
                    
                    ex_category = st.selectbox(
                        "Type *",
                        ["strength", "cardio", "flexibility"]
                    )
                    
                    muscle_groups = ["legs", "chest", "back", "shoulders", "arms", "core", "full-body"]
                    
                    ex_muscle = st.selectbox(
                        "Target Muscle Group *",
                        muscle_groups
                    )
                    
                    ex_desc = st.text_area(
                        "Description (optional)",
                        placeholder="How to perform this exercise, tips, form cues...",
                        height=80
                    )
                    
                    if st.form_submit_button("✅ Add Exercise", use_container_width=True):
                        if not ex_name.strip():
                            st.error("❌ Exercise name is required")
                        else:
                            result = create_exercise({
                                "name": ex_name.strip(),
                                "category": ex_category,
                                "muscle_group": ex_muscle,
                                "description": ex_desc if ex_desc.strip() else None,
                            })
                            if result:
                                st.success(f"✅ **{ex_name}** has been added to your library!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to add exercise. Please try again.")
            
            # Column 2: List All Exercises
            with col_list:
                st.markdown("### 📚 Your Exercise Library")
                exercises = list_exercises()
                
                if exercises:
                    st.write(f"*Total exercises: **{len(exercises)}***")
                    st.divider()
                    
                    # Group by muscle group
                    muscle_groups_dict = {}
                    for ex in exercises:
                        muscle = ex.get("muscle_group", "Other")
                        if muscle not in muscle_groups_dict:
                            muscle_groups_dict[muscle] = []
                        muscle_groups_dict[muscle].append(ex)
                    
                    # Display grouped
                    for muscle, exs in sorted(muscle_groups_dict.items()):
                        with st.expander(f"**{muscle.title()}** ({len(exs)})"):
                            for ex in exs:
                                col_name, col_type = st.columns([3, 1])
                                with col_name:
                                    st.write(f"💪 **{ex['name']}**")
                                    if ex.get("description"):
                                        st.caption(ex['description'])
                                with col_type:
                                    st.caption(f"`{ex['category']}`")
                else:
                    st.info("📭 No exercises yet. Add one to get started!")
        
        # ─────────────────────────────────────────────
        # Subtab 2: Log Workout (Search & Date)
        # ─────────────────────────────────────────────
        with training_tabs[1]:
            st.subheader("📝 Log a New Workout")
            st.write("Select an exercise from your library and record your workout with the date it was performed.")
            
            # Initialize state for exercise selection
            if "selected_log_exercise" not in st.session_state:
                st.session_state.selected_log_exercise = None
            
            col_search, col_date = st.columns([2, 1])
            
            with col_search:
                st.write("**Step 1: Select Exercise**")
                
                # Get user's exercises
                user_exercises = list_exercises()
                
                if user_exercises:
                    # Create simple list of exercise names
                    exercise_names = {f"{ex['name']} ({ex['muscle_group']})" : ex for ex in user_exercises}
                    
                    selected_display = st.selectbox(
                        "Choose an exercise",
                        list(exercise_names.keys()),
                        key="exercise_select"
                    )
                    
                    st.session_state.selected_log_exercise = exercise_names[selected_display]
                else:
                    st.warning("⚠️ No exercises in your library. Create some first in the Exercise Library tab!")
                    st.session_state.selected_log_exercise = None
            
            with col_date:
                st.write("**Step 2: Select Date**")
                log_date = st.date_input(
                    "📅 Date of workout",
                    value=date.today(),
                    key="workout_date_input"
                )
                st.info(f"Selected: **{log_date.strftime('%a, %b %d, %Y')}**")
            
            st.divider()
            
            # Show form if exercise is selected
            if st.session_state.selected_log_exercise:
                selected = st.session_state.selected_log_exercise
                exercise_id = selected["id"]
                exercise_name = selected["name"]
                
                # Display selected exercise
                st.markdown(f"### 💪 Selected: **{exercise_name}**")
                st.write(f"**Date:** {log_date.strftime('%A, %B %d, %Y')}")
                
                st.write("**Step 3: Log Your Performance**")
                
                with st.form("log_workout_form"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        sets = st.number_input(
                            "Sets",
                            min_value=1,
                            max_value=100,
                            value=3,
                            help="Number of sets performed"
                        )
                    
                    with col2:
                        reps = st.number_input(
                            "Reps",
                            min_value=1,
                            max_value=1000,
                            value=8,
                            help="Number of repetitions per set"
                        )
                    
                    with col3:
                        weight = st.number_input(
                            "Weight (kg)",
                            min_value=0.0,
                            max_value=1000.0,
                            value=50.0,
                            step=2.5,
                            help="Weight used (0 for bodyweight)"
                        )
                    
                    notes = st.text_area(
                        "Notes (optional)",
                        placeholder="How did it feel? Any observations?",
                        height=60
                    )
                    
                    if st.form_submit_button("✅ Log This Workout", use_container_width=True):
                        if not exercise_id:
                            st.error("❌ Exercise selection error. Please try again.")
                        else:
                            # Prepare workout data
                            workout_data = {
                                "exercise_id": str(exercise_id),
                                "log_date": str(log_date),
                                "sets": int(sets),
                                "reps": int(reps),
                                "weight_kg": float(weight),
                                "notes": notes.strip() if notes and notes.strip() else None,
                            }
                            
                            # Show what's being sent (for debugging)
                            with st.spinner("📤 Logging workout..."):
                                result = create_workout_log(workout_data)
                            
                            if result:
                                st.success(f"✅ **Workout logged for {log_date.strftime('%B %d')}!**")
                                st.balloons()
                                st.session_state.selected_log_exercise = None
                                st.rerun()
                            # Error is already shown by create_workout_log function
            
            # Recent workouts history
            st.divider()
            st.subheader("📊 Recent Workouts")
            
            logs = list_workout_logs()
            if logs:
                # Group by date (most recent first)
                grouped_by_date = {}
                for log in logs:
                    log_date_str = log.get('log_date', 'Unknown')
                    if log_date_str not in grouped_by_date:
                        grouped_by_date[log_date_str] = []
                    grouped_by_date[log_date_str].append(log)
                
                for log_date_str in sorted(grouped_by_date.keys(), reverse=True)[:10]:
                    logs_on_date = grouped_by_date[log_date_str]
                    with st.expander(f"📅 **{log_date_str}** ({len(logs_on_date)} workout{'s' if len(logs_on_date) > 1 else ''})"):
                        for log in logs_on_date:
                            col1, col2, col3, col_edit, col_delete = st.columns([2, 2, 0.5, 0.5, 0.5])
                            with col1:
                                st.write(f"💪 {log.get('exercise_name', 'Exercise')}")
                            with col2:
                                st.caption(f"{log['sets']}×{log['reps']} @ {log['weight_kg']} kg")
                            with col3:
                                if log.get('notes'):
                                    st.caption(f"📝 {log['notes'][:30]}...")
                            
                            with col_edit:
                                if st.button("✏️", key=f"edit_log_{log['id']}", help="Edit workout"):
                                    st.session_state.editing_log_id = log['id']
                                    st.session_state.editing_log = log
                                    st.rerun()
                            
                            with col_delete:
                                if st.button("🗑️", key=f"delete_log_{log['id']}", help="Delete workout"):
                                    if delete_workout_log(log['id']):
                                        st.success("✅ Workout deleted!")
                                        st.rerun()
                
                # Edit workout modal
                if st.session_state.get("editing_log_id"):
                    st.divider()
                    st.subheader("✏️ Edit Workout")
                    
                    editing_log = st.session_state.get("editing_log", {})
                    log_id = st.session_state.get("editing_log_id")
                    
                    # Get exercises list
                    user_exercises = list_exercises()
                    exercise_names = {f"{ex['name']} ({ex['muscle_group']})" : ex for ex in user_exercises}
                    
                    # Pre-select current exercise
                    current_exercise_name = None
                    for name, ex in exercise_names.items():
                        if ex['id'] == editing_log.get('exercise_id'):
                            current_exercise_name = name
                            break
                    
                    current_index = list(exercise_names.keys()).index(current_exercise_name) if current_exercise_name else 0
                    
                    with st.form("edit_workout_form"):
                        # Exercise selection
                        selected_display = st.selectbox(
                            "Exercise",
                            list(exercise_names.keys()),
                            index=current_index,
                            key="edit_exercise_select"
                        )
                        
                        # Date
                        edit_log_date = st.date_input(
                            "Date",
                            value=editing_log.get('log_date', log_date_str),
                            key="edit_log_date_input"
                        )
                        
                        # Performance metrics
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            edit_sets = st.number_input(
                                "Sets",
                                min_value=1,
                                max_value=100,
                                value=int(editing_log.get('sets', 3)),
                                key="edit_sets_input"
                            )
                        
                        with col2:
                            edit_reps = st.number_input(
                                "Reps",
                                min_value=1,
                                max_value=1000,
                                value=int(editing_log.get('reps', 8)),
                                key="edit_reps_input"
                            )
                        
                        with col3:
                            edit_weight = st.number_input(
                                "Weight (kg)",
                                min_value=0.0,
                                max_value=1000.0,
                                value=float(editing_log.get('weight_kg', 50.0)),
                                step=2.5,
                                key="edit_weight_input"
                            )
                        
                        # Notes
                        edit_notes = st.text_area(
                            "Notes (optional)",
                            value=editing_log.get('notes', ''),
                            key="edit_notes_input"
                        )
                        
                        col_save, col_cancel = st.columns(2)
                        
                        with col_save:
                            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                                edit_exercise = exercise_names[selected_display]
                                
                                update_data = {
                                    "exercise_id": str(edit_exercise['id']),
                                    "log_date": str(edit_log_date),
                                    "sets": int(edit_sets),
                                    "reps": int(edit_reps),
                                    "weight_kg": float(edit_weight),
                                    "notes": edit_notes.strip() if edit_notes.strip() else None,
                                }
                                
                                with st.spinner("📤 Saving changes..."):
                                    result = update_workout_log(log_id, update_data)
                                
                                if result:
                                    st.success("✅ Workout updated!")
                                    st.session_state.editing_log_id = None
                                    st.session_state.editing_log = None
                                    st.rerun()
                        
                        with col_cancel:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                st.session_state.editing_log_id = None
                                st.session_state.editing_log = None
                                st.rerun()
            else:
                st.info("🏋️ No workouts logged yet. Start by logging your first workout!")
        
        # ─────────────────────────────────────────────
        # Subtab 3: Workout Calendar
        # ─────────────────────────────────────────────
        with training_tabs[2]:
            st.subheader("📅 Workout Calendar")
            logs = list_workout_logs()
            display_workout_calendar(logs)
    
    # ─────────────────────────────────────────────
    # Tab 3: Nutrition (with AI Food Analyzer)
    # ─────────────────────────────────────────────
    with tabs[3]:
        st.title("🥗 Nutrition Tracking")
        
        nutrition_tabs = st.tabs(["🤖 AI Analysis", "✍️ Manual Entry", "📅 Calendar", "📈 History"])
        
        # Subtab 1: AI Food Analyzer
        with nutrition_tabs[0]:
            st.subheader("✍️ What Did You Eat?")
            st.write("Describe what you ate and our AI will calculate the nutrition!")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                food_desc = st.text_area(
                    "Describe your meal:",
                    placeholder="e.g., Grilled chicken breast with rice and broccoli",
                    height=80,
                    label_visibility="collapsed"
                )
            
            macro_date_ai = st.date_input("Date", value=date.today(), key="nut_date_ai")
            
            # Initialize state for analyzed nutrition
            if "analyzed_nutrition" not in st.session_state:
                st.session_state.analyzed_nutrition = None
            
            if st.button("🤖 Analyze with AI", use_container_width=True):
                if not food_desc or len(food_desc) < 3:
                    st.error("⚠️ Please describe what you ate (at least 3 characters)")
                else:
                    with st.spinner("🔍 Analyzing your meal..."):
                        try:
                            client = get_api_with_auth()
                            response = client.post("/macros/analyze-food", json={
                                "food_description": food_desc
                            })
                            if response.status_code == 200:
                                st.session_state.analyzed_nutrition = response.json()
                                st.success("✅ Analysis complete!")
                            else:
                                error_detail = response.json().get("detail", response.text)
                                st.error(f"❌ Analysis failed: {error_detail}")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            
            # Display analyzed nutrition if available
            if st.session_state.analyzed_nutrition:
                analyzed = st.session_state.analyzed_nutrition
                st.divider()
                st.subheader("📊 Calculated Nutrition")
                
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("Calories", f"{analyzed['calories']:.0f}")
                with col_b:
                    st.metric("Protein", f"{analyzed['protein_g']:.1f}g")
                with col_c:
                    st.metric("Carbs", f"{analyzed['carbs_g']:.1f}g")
                with col_d:
                    st.metric("Fat", f"{analyzed['fat_g']:.1f}g")
                
                st.info(f"💭 AI Analysis: {analyzed['analysis']}")
                
                # Extract keywords from food description for header
                food_keywords = " | ".join([word for word in food_desc.split() if len(word) > 3][:5])
                header_text = f"📍 {food_keywords}" if food_keywords else "📍 Meal"
                
                # Allow user to save the calculated nutrition
                col_save1, col_save2 = st.columns(2)
                with col_save1:
                    if st.button("💾 Save This Entry", use_container_width=True, key="save_analyzed"):
                        new = create_macro({
                            "entry_date": str(macro_date_ai),
                            "calories": analyzed['calories'],
                            "protein_g": analyzed['protein_g'],
                            "carbs_g": analyzed['carbs_g'],
                            "fat_g": analyzed['fat_g'],
                            "notes": f"{header_text} - {food_desc}",
                        })
                        if new:
                            st.success("✅ Nutrition entry saved!")
                            st.session_state.analyzed_nutrition = None
                            list_macros.clear()  # Invalidate cache
                            st.rerun()
        
        # Subtab 2: Manual Entry
        with nutrition_tabs[1]:
            st.subheader("➕ Log Macros Manually")
            with st.form("log_macros"):
                macro_date = st.date_input("Date", value=date.today(), key="nut_date_manual")
                calories = st.number_input("Calories", min_value=0, max_value=20000, value=2200)
                protein = st.number_input("Protein (g)", min_value=0, max_value=1000, value=180)
                carbs = st.number_input("Carbs (g)", min_value=0, max_value=2000, value=250)
                fat = st.number_input("Fat (g)", min_value=0, max_value=1000, value=70)
                notes = st.text_area("Notes", placeholder="e.g., Skipped breakfast...")
                
                if st.form_submit_button("🥗 Log Macros", use_container_width=True):
                    new = create_macro({
                        "entry_date": str(macro_date),
                        "calories": float(calories),
                        "protein_g": float(protein),
                        "carbs_g": float(carbs),
                        "fat_g": float(fat),
                        "notes": notes if notes else None,
                    })
                    if new:
                        st.success("✅ Macros logged!")
                        list_macros.clear()  # Invalidate cache
                        st.rerun()
        
        # Subtab 3: Calendar Log
        with nutrition_tabs[2]:
            st.subheader("📅 Nutrition Calendar")
            macros = list_macros()
            display_nutrition_calendar(macros)
        
        # Subtab 4: History & Insights
        with nutrition_tabs[3]:
            st.subheader("📊 Nutrition History")
            macros = list_macros()
            
            if macros:
                for m in reversed(macros[-7:]):
                    col1, col2, col3, col_edit, col_delete = st.columns([3, 2, 0.5, 0.5, 0.5])
                    
                    with col1:
                        st.metric(
                            f"📅 {m['entry_date']}",
                            f"{m['calories']:.0f} kcal"
                        )
                    
                    with col2:
                        st.caption(f"P:{m['protein_g']:.1f}g | C:{m['carbs_g']:.1f}g | F:{m['fat_g']:.1f}g")
                        if m.get('notes'):
                            st.caption(f"📝 {m['notes'][:40]}...")
                    
                    with col_edit:
                        if st.button("✏️", key=f"edit_macro_{m['id']}", help="Edit nutrition"):
                            st.session_state.editing_macro_id = m['id']
                            st.session_state.editing_macro = m
                            st.rerun()
                    
                    with col_delete:
                        if st.button("🗑️", key=f"delete_macro_{m['id']}", help="Delete nutrition"):
                            if delete_macro(m['id']):
                                st.success("✅ Nutrition entry deleted!")
                                st.rerun()
                
                # Edit nutrition modal
                if st.session_state.get("editing_macro_id"):
                    st.divider()
                    st.subheader("✏️ Edit Nutrition Entry")
                    
                    editing_macro = st.session_state.get("editing_macro", {})
                    macro_id = st.session_state.get("editing_macro_id")
                    
                    with st.form("edit_macro_form"):
                        edit_macro_date = st.date_input(
                            "Date",
                            value=editing_macro.get('entry_date', date.today()),
                            key="edit_macro_date_input"
                        )
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            edit_calories = st.number_input(
                                "Calories",
                                min_value=0,
                                max_value=20000,
                                value=int(editing_macro.get('calories', 2200)),
                                key="edit_calories_input"
                            )
                        
                        with col2:
                            edit_protein = st.number_input(
                                "Protein (g)",
                                min_value=0,
                                max_value=1000,
                                value=float(editing_macro.get('protein_g', 180)),
                                key="edit_protein_input"
                            )
                        
                        with col3:
                            edit_carbs = st.number_input(
                                "Carbs (g)",
                                min_value=0,
                                max_value=2000,
                                value=float(editing_macro.get('carbs_g', 250)),
                                key="edit_carbs_input"
                            )
                        
                        with col4:
                            edit_fat = st.number_input(
                                "Fat (g)",
                                min_value=0,
                                max_value=1000,
                                value=float(editing_macro.get('fat_g', 70)),
                                key="edit_fat_input"
                            )
                        
                        edit_notes = st.text_area(
                            "Notes (optional)",
                            value=editing_macro.get('notes', ''),
                            key="edit_notes_macro_input"
                        )
                        
                        col_save, col_cancel = st.columns(2)
                        
                        with col_save:
                            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                                update_data = {
                                    "entry_date": str(edit_macro_date),
                                    "calories": float(edit_calories),
                                    "protein_g": float(edit_protein),
                                    "carbs_g": float(edit_carbs),
                                    "fat_g": float(edit_fat),
                                    "notes": edit_notes.strip() if edit_notes.strip() else None,
                                }
                                
                                with st.spinner("📤 Saving changes..."):
                                    result = update_macro(macro_id, update_data)
                                
                                if result:
                                    st.success("✅ Nutrition entry updated!")
                                    st.session_state.editing_macro_id = None
                                    st.session_state.editing_macro = None
                                    st.rerun()
                        
                        with col_cancel:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                st.session_state.editing_macro_id = None
                                st.session_state.editing_macro = None
                                st.rerun()
            else:
                st.info("No nutrition logged yet.")
            
            # Nutrition insights
            if selected_profile and macros:
                st.divider()
                st.subheader("💡 Smart Nutrition Insights")
                protein_target = get_protein_target(st.session_state.selected_profile_id)
                if protein_target:
                    # Calculate 7-day average protein
                    avg_protein = sum(m['protein_g'] for m in macros[-7:]) / len(macros[-7:])
                    today_protein = macros[-1]['protein_g'] if macros else 0
                    total_daily_target = protein_target['protein_g']
                    protein_gap = max(0, total_daily_target - avg_protein)
                    
                    # Protein goal progress
                    st.metric("Average Daily Protein", f"{avg_protein:.1f}g", delta=f"Target: {total_daily_target}g", delta_color="off")
                    
                    # Personalized guidance
                    if protein_gap > 0:
                        st.warning(f"🎯 **You need {protein_gap:.0f}g more protein/day to reach your goal!**\n\nHere are high-protein, low-fat foods to close the gap:")
                        
                        if protein_target['multiplier_g_per_kg'] >= 2.0:  # Muscle goal
                            st.info(
                                "💪 **For Muscle Building:**\n\n"
                                "🍗 Chicken Breast (31g protein, 3.6g fat per 100g)\n"
                                "🐟 Cod/Tilapia (19g protein, 0.7g fat per 100g)\n"
                                "🥚 Egg Whites (11g protein, 0.2g fat per 2 whites)\n"
                                "🥛 Greek Yogurt (10g protein, 0.4g fat per 100g)\n"
                                "🍝 Protein Powder (20-25g protein, <1g fat per scoop)\n\n"
                                "**Recommended Workouts:** Heavy compound lifts (Squats, Deadlifts, Bench Press) 3-4x/week with progressive overload"
                            )
                        else:  # Maintenance/recomposition goal
                            st.info(
                                "⚖️ **For Maintenance & Recomposition:**\n\n"
                                "🍗 Turkey Breast (29g protein, 1.3g fat per 100g)\n"
                                "🐟 Salmon (25g protein, 13g fat per 100g - good omega-3s)\n"
                                "🫘 Lean Beef (26g protein, 5g fat per 100g)\n"
                                "🏠 Cottage Cheese (11g protein, 5g fat per 100g)\n"
                                "🌾 Lentils (9g protein, 0.4g fat per cooked cup)\n\n"
                                "**Recommended Workouts:** Balanced mix of strength and cardio 3-5x/week + flexibility training"
                            )
                    else:
                        st.success(f"🎉 **Great job! You're meeting your protein goal!** ({avg_protein:.1f}g ≥ {total_daily_target}g)")
                        st.success("Keep up this consistency to reach your fitness goals!")
    
    # Footer
    st.divider()
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem; padding: 2rem 0;">
            <div style="
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 56px;
                height: 56px;
                background: linear-gradient(135deg, #6750a4 0%, #7d5260 100%);
                border-radius: 12px;
                font-size: 32px;
                box-shadow: 0 4px 12px rgba(103, 80, 164, 0.25);
                margin: 0 auto 16px auto;
            ">
                💪📊
            </div>
            <p style="font-size: 16px; font-weight: 600; color: #111827; margin: 0;"><strong>FitLog v2.0</strong></p>
            <p style="font-size: 13px; color: #6b7280; margin: 8px 0 0 0;">Professional Fitness & Nutrition Tracking</p>
            <p style="font-size: 0.85rem; color: #999; margin-top: 16px;">
                Powered by FastAPI • Streamlit • Groq AI
            </p>
        </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# App Entry Point (Fixed for Streamlit)
# ─────────────────────────────────────────────

# CRITICAL: This check must use proper Streamlit flow
# (Doesn't rely on __name__ which behaves differently in Streamlit)

# Explicit token and logged_in check
_is_authenticated = (
    st.session_state.get("logged_in") is True and 
    st.session_state.get("token") is not None and 
    len(st.session_state.get("token", "")) > 0
)

# Check authentication state and show appropriate page
if _is_authenticated:
    # User is authenticated - show main app
    main_app()
    # Display floating AI chatbot
    floating_ai_chatbot()
else:
    # User is not authenticated - show login/register
    login_page()
