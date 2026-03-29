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
    page_title="FitLog - Fitness Tracker",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional custom CSS
st.markdown("""
    <style>
        /* Main styling */
        :root {
            --primary: #1f77b4;
            --success: #2ca02c;
            --warning: #ff7f0e;
            --danger: #d62728;
        }
        
        /* Header styling */
        .header {
            padding: 1.5rem 0;
            border-bottom: 2px solid #e0e0e0;
            margin-bottom: 2rem;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            background-color: #f8f9fa;
            border-radius: 0.5rem;
            padding: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 1rem;
            border-radius: 0.375rem;
        }
        
        /* Card styling */
        .card {
            background: white;
            border-radius: 0.5rem;
            border: 1px solid #e0e0e0;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        
        /* Metric cards */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 0.5rem;
            padding: 1.5rem;
            text-align: center;
        }
        
        /* Professional colors */
        .success-color { color: #2ca02c; }
        .warning-color { color: #ff7f0e; }
        .danger-color { color: #d62728; }
        
        /* Sidebar improvements */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 0.375rem;
            font-weight: 500;
            padding: 0.5rem 1rem;
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


def get_api_with_auth() -> httpx.Client:
    """
    Get authenticated HTTP client with current token.
    Creates new client each time to ensure token is always current.
    """
    token = st.session_state.get("token", "")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return httpx.Client(
        base_url=API_BASE,
        timeout=15.0,
        headers=headers,
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
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
def list_workout_logs():
    """Fetch all workout logs with 45s cache."""
    try:
        client = get_api_with_auth()
        response = client.get("/logs/")
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        st.warning(f"⚠️ Workouts offline: {e}")
        return []


def create_workout_log(data):
    """Log a workout and invalidate cache."""
    try:
        client = get_api_with_auth()
        response = client.post("/logs/", json=data)
        if response.status_code == 201:
            list_workout_logs.clear()  # Invalidate cache
            return response.json()
        return None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


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
    """Login page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🏋️ FitLog")
        st.markdown("*Your Personal Fitness & Nutrition Tracker*")
        st.divider()
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("👤 Login")
            email = st.text_input("Email", placeholder="you@example.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")
            
            if st.button("🔓 Login", use_container_width=True, key="login_btn"):
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
            st.subheader("📝 Create Account")
            name = st.text_input("Full Name", placeholder="Alex Fitness", key="register_name")
            email = st.text_input("Email", placeholder="you@example.com", key="register_email")
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
            
            if st.button("✨ Create Account", use_container_width=True, key="register_btn"):
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
    """Main application with professional layout."""
    # Header
    header_col1, header_col2, header_col3 = st.columns([3, 1, 1], vertical_alignment="center")
    
    with header_col1:
        st.markdown("# 🏋️ FitLog")
        st.markdown(f"**Welcome, {st.session_state.user_name}**")
    
    with header_col2:
        pass  # Spacing
    
    with header_col3:
        if st.button("🚪 Logout", use_container_width=True, key="logout_top"):
            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.session_state.selected_profile_id = None
            st.success("✅ Logged out successfully!")
            st.rerun()
    
    st.divider()
    
    # ═══════════════════════════════════════════
    # SIDEBAR - Profile & Settings
    # ═══════════════════════════════════════════
    with st.sidebar:
        st.markdown("## 📊 Fitness Profile")
        st.divider()
        
        profiles = list_profiles()
        
        if profiles:
            profile_names = [f"{p['name']} ({p['goal']})" for p in profiles]
            selected_idx = st.selectbox(
                "Select Profile",
                range(len(profiles)),
                format_func=lambda i: profile_names[i],
            )
            st.session_state.selected_profile_id = profiles[selected_idx]["id"]
            selected_profile = profiles[selected_idx]
        else:
            selected_profile = None
            st.session_state.selected_profile_id = None
        
        # Settings Section in Sidebar
        st.markdown("## ⚙️ Account Settings")
        st.divider()
        
        # Account Info
        st.markdown("### Account Information")
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
    
    # Main tabs (5 tabs)
    tabs = st.tabs([
        "📈 Dashboard",
        "👤 Profile",
        "💪 Training",
        "🥗 Nutrition",
        "🤖 AI Coach",
    ])
    
    # ─────────────────────────────────────────────
    # Tab 0: Dashboard
    # ─────────────────────────────────────────────
    with tabs[0]:
        st.title("📈 Dashboard")
        
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
        
        training_tabs = st.tabs(["📚 Exercise Library", "📝 Log Workout"])
        
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
                            result = create_workout_log({
                                "exercise_id": str(exercise_id),
                                "log_date": str(log_date),
                                "sets": int(sets),
                                "reps": int(reps),
                                "weight_kg": float(weight),
                                "notes": notes if notes.strip() else None,
                            })
                            
                            if result:
                                st.success(f"✅ **Workout logged for {log_date.strftime('%B %d')}!**")
                                st.balloons()
                                st.session_state.selected_log_exercise = None
                                st.rerun()
                            else:
                                st.error("❌ Failed to log workout. Please check your connection and try again.")
            
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
                            col1, col2, col3 = st.columns([2, 2, 1])
                            with col1:
                                st.write(f"💪 {log.get('exercise_name', 'Exercise')}")
                            with col2:
                                st.caption(f"{log['sets']}×{log['reps']} @ {log['weight_kg']} kg")
                            with col3:
                                if log.get('notes'):
                                    st.caption(f"📝 {log['notes'][:30]}...")
            else:
                st.info("🏋️ No workouts logged yet. Start by logging your first workout!")
    
    # ─────────────────────────────────────────────
    # Tab 3: Nutrition (with AI Food Analyzer)
    # ─────────────────────────────────────────────
    with tabs[3]:
        st.title("🥗 Nutrition Tracking")
        
        nutrition_tabs = st.tabs(["🤖 AI Analyzer", "📋 Manual Entry", "📅 Calendar Log", "📊 History"])
        
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
                    st.metric(
                        f"📅 {m['entry_date']}",
                        f"{m['calories']:.0f} kcal",
                        delta=f"P:{m['protein_g']:.1f}g | C:{m['carbs_g']:.1f}g | F:{m['fat_g']:.1f}g"
                    )
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
    
    # ─────────────────────────────────────────────
    # Tab 4: AI Coach
    # ─────────────────────────────────────────────
    with tabs[4]:
        st.title("🤖 AI Fitness Coach")
        st.markdown("Get personalized fitness advice from our Gemini AI coach")
        
        if selected_profile:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                message = st.text_area(
                    "💬 Ask me anything",
                    placeholder="e.g., How much protein should I eat? What exercises for my goal?",
                    height=100,
                    key="ai_msg"
                )
            
            with col2:
                st.write("")
                st.write("")
                send_btn = st.button("🚀 Send", use_container_width=True, key="ai_btn")
            
            if send_btn and message.strip():
                if not st.session_state.selected_profile_id:
                    st.error("⚠️ Please select a fitness profile first!")
                else:
                    with st.spinner("🤖 AI is thinking..."):
                        response = chat_with_ai(str(st.session_state.selected_profile_id), message)
                st.divider()
                st.info(f"**🤖 Coach Response:**\n\n{response.get('reply', 'No response')}")
            elif send_btn:
                st.warning("⚠️ Type a message!")
            
            st.divider()
            st.subheader("💡 Ask Common Questions")
            
            col1, col2, col3 = st.columns(3)
            
            quick_questions = [
                ("🥩 Protein Target", "How much protein should I eat daily?"),
                ("💪 Exercise Tips", "What exercises should I focus on for my goal?"),
                ("📈 Progress Check", "How is my progress going?"),
            ]
            
            for i, (btn_label, question) in enumerate(quick_questions):
                with [col1, col2, col3][i]:
                    if st.button(btn_label, use_container_width=True, key=f"quick_{i}"):
                        with st.spinner("🤖"):
                            r = chat_with_ai(str(st.session_state.selected_profile_id), question)
                        st.info(r.get("reply"))
        else:
            st.warning("⚠️ Create a profile first!")
    
    # Footer
    st.divider()
    st.markdown("""
        <div style="text-align: center; margin-top: 3rem;">
            <p><strong>🏋️ FitLog v2.0</strong> | Professional Fitness & Nutrition Tracking</p>
            <p style="font-size: 0.85rem; color: #666;">
                Powered by FastAPI • Streamlit • Groq AI
            </p>
        </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# App Entry Point (Fixed for Streamlit)
# ─────────────────────────────────────────────

# CRITICAL: This check must be at the END and use proper Streamlit flow
# (Doesn't rely on __name__ which behaves differently in Streamlit)

# Check authentication state and show appropriate page
if st.session_state.logged_in and st.session_state.token:
    # User is authenticated - show main app
    main_app()
    # Exit early to prevent login_page from running
    st.stop()
else:
    # User is not authenticated - show login/register
    login_page()
    # Exit early to prevent main_app from running
    st.stop()
