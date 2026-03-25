"""
FitLog Frontend – Streamlit Dashboard with Authentication
Complete fitness tracking application with login system
"""
import streamlit as st
import httpx
from datetime import date
import json

# Configuration
API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")

st.set_page_config(
    page_title="FitLog - Fitness Tracker",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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


def get_api_with_auth():
    """Create HTTP client with authentication headers."""
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    return httpx.Client(base_url=API_BASE, timeout=10.0, headers=headers)


# ─────────────────────────────────────────────
# API Functions
# ─────────────────────────────────────────────

def api_register(email: str, password: str, name: str) -> dict:
    """Register a new user."""
    try:
        with httpx.Client(base_url=API_BASE, timeout=10.0) as client:
            response = client.post(
                "/auth/register",
                json={"email": email, "password": password, "name": name}
            )
            if response.status_code == 201:
                return response.json()
            else:
                st.error(f"Registration error: {response.json().get('detail', 'Unknown error')}")
                return None
    except Exception as e:
        st.error(f"❌ Registration failed: {e}")
        return None


def api_login(email: str, password: str) -> dict:
    """Login user."""
    try:
        with httpx.Client(base_url=API_BASE, timeout=10.0) as client:
            response = client.post(
                "/auth/login",
                json={"email": email, "password": password}
            )
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Login error: {response.json().get('detail', 'Invalid credentials')}")
                return None
    except Exception as e:
        st.error(f"❌ Login failed: {e}")
        return None


def list_profiles():
    """Fetch all profiles."""
    try:
        with get_api_with_auth() as client:
            response = client.get("/profile/")
            return response.json() if response.status_code == 200 else []
    except:
        return []


def create_profile(data):
    """Create a new profile."""
    try:
        with get_api_with_auth() as client:
            response = client.post("/profile/", json=data)
            return response.json() if response.status_code == 201 else None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


def get_protein_target(profile_id):
    """Get protein target."""
    try:
        with get_api_with_auth() as client:
            response = client.get(f"/profile/{profile_id}/protein-target")
            return response.json() if response.status_code == 200 else None
    except:
        return None


def list_exercises():
    """Fetch all exercises."""
    try:
        with get_api_with_auth() as client:
            response = client.get("/exercises/")
            return response.json() if response.status_code == 200 else []
    except:
        return []


def create_exercise(data):
    """Create exercise."""
    try:
        with get_api_with_auth() as client:
            response = client.post("/exercises/", json=data)
            return response.json() if response.status_code == 201 else None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


def list_workout_logs():
    """Fetch all workout logs."""
    try:
        with get_api_with_auth() as client:
            response = client.get("/logs/")
            return response.json() if response.status_code == 200 else []
    except:
        return []


def create_workout_log(data):
    """Log a workout."""
    try:
        with get_api_with_auth() as client:
            response = client.post("/logs/", json=data)
            return response.json() if response.status_code == 201 else None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


def list_macros():
    """Fetch all macros."""
    try:
        with get_api_with_auth() as client:
            response = client.get("/macros/")
            return response.json() if response.status_code == 200 else []
    except:
        return []


def create_macro(data):
    """Log macros."""
    try:
        with get_api_with_auth() as client:
            response = client.post("/macros/", json=data)
            return response.json() if response.status_code == 201 else None
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None


def chat_with_ai(user_id: str, message: str) -> dict:
    """Chat with AI."""
    try:
        with get_api_with_auth() as client:
            response = client.post("/ai/chat", json={
                "user_id": user_id,
                "message": message
            })
            return response.json() if response.status_code == 200 else {"reply": "Error"}
    except Exception as e:
        return {"reply": f"Error: {e}"}


def get_workout_summary(profile_id):
    """Get analytics summary."""
    try:
        with get_api_with_auth() as client:
            response = client.get(f"/analytics/{profile_id}/workout-summary")
            return response.json() if response.status_code == 200 else None
    except:
        return None


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
    """Main application."""
    # Sidebar
    st.sidebar.markdown(f"## 👋 {st.session_state.user_name}")
    st.sidebar.markdown(f"*{st.session_state.user_id}*", help="Your User ID")
    st.sidebar.divider()
    
    # Profile selector
    st.sidebar.header("📊 Fitness Profile")
    profiles = list_profiles()
    
    if profiles:
        profile_names = [f"{p['name']} ({p['goal']})" for p in profiles]
        selected_idx = st.sidebar.selectbox(
            "Select Profile",
            range(len(profiles)),
            format_func=lambda i: profile_names[i],
        )
        st.session_state.selected_profile_id = profiles[selected_idx]["id"]
        selected_profile = profiles[selected_idx]
    else:
        selected_profile = None
        st.session_state.selected_profile_id = None
    
    # Logout button
    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.token = None
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.session_state.selected_profile_id = None
        st.success("✅ Logged out successfully!")
        st.rerun()
    
    # Main tabs
    tabs = st.tabs([
        "Dashboard",
        "Profile",
        "Exercises",
        "Workouts",
        "Nutrition",
        "Analytics",
        "AI Coach",
        "Settings",
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
            
            # Workout Summary
            st.subheader("📊 Workout Summary")
            summary = get_workout_summary(st.session_state.selected_profile_id)
            if summary:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Workouts", summary['total_workouts'])
                with col2:
                    st.metric("Total Volume", f"{summary['total_volume_kg']:.0f} kg")
                with col3:
                    st.metric("Most Worked", summary['most_worked_muscle_group'])
                st.success(summary['recommendation'])
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
    # Tab 2: Exercises
    # ─────────────────────────────────────────────
    with tabs[2]:
        st.title("🏋️ Exercise Library")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("➕ Add Exercise")
            with st.form("add_exercise"):
                name = st.text_input("Exercise Name", placeholder="Barbell Squat")
                category = st.selectbox("Category", ["strength", "cardio", "flexibility"])
                muscle = st.selectbox("Muscle Group", ["legs", "chest", "back", "shoulders", "arms", "core", "full-body"])
                desc = st.text_area("Description", placeholder="Optional...")
                
                if st.form_submit_button("➕ Add Exercise", use_container_width=True):
                    new = create_exercise({
                        "name": name,
                        "category": category,
                        "muscle_group": muscle,
                        "description": desc if desc else None,
                    })
                    if new:
                        st.success(f"✅ {name} added!")
                        st.rerun()
        
        with col2:
            st.subheader("📚 All Exercises")
            exercises = list_exercises()
            if exercises:
                for ex in exercises:
                    st.write(f"💪 **{ex['name']}** [{ex['category']}]")
                    st.caption(f"🎯 {ex['muscle_group']}")
            else:
                st.info("No exercises. Add some to get started!")
    
    # ─────────────────────────────────────────────
    # Tab 3: Workouts
    # ─────────────────────────────────────────────
    with tabs[3]:
        st.title("📝 Workout Logs")
        
        exercises = list_exercises()
        if exercises:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("➕ Log Workout")
                with st.form("log_workout"):
                    exercise = st.selectbox("Exercise", exercises, format_func=lambda x: x["name"])
                    log_date = st.date_input("Date", value=date.today())
                    sets = st.number_input("Sets", min_value=1, max_value=100, value=3)
                    reps = st.number_input("Reps", min_value=1, max_value=1000, value=8)
                    weight = st.number_input("Weight (kg)", min_value=0, max_value=1000.0, value=80.0)
                    notes = st.text_area("Notes")
                    
                    if st.form_submit_button("📝 Log It", use_container_width=True):
                        new = create_workout_log({
                            "exercise_id": exercise["id"],
                            "log_date": str(log_date),
                            "sets": int(sets),
                            "reps": int(reps),
                            "weight_kg": float(weight),
                            "notes": notes if notes else None,
                        })
                        if new:
                            st.success("✅ Workout logged!")
                            st.rerun()
            
            with col2:
                st.subheader("📊 Recent Workouts")
                logs = list_workout_logs()
                if logs:
                    for log in reversed(logs[-5:]):
                        st.write(f"📅 {log['log_date']} | {log['sets']}×{log['reps']} @ {log['weight_kg']} kg")
                else:
                    st.info("No workouts logged yet.")
        else:
            st.warning("⚠️ Add exercises first!")
    
    # ─────────────────────────────────────────────
    # Tab 4: Nutrition
    # ─────────────────────────────────────────────
    with tabs[4]:
        st.title("🥗 Nutrition Tracking")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("➕ Log Macros")
            with st.form("log_macros"):
                macro_date = st.date_input("Date", value=date.today(), key="nut_date")
                calories = st.number_input("Calories", min_value=0, max_value=20000, value=2200)
                protein = st.number_input("Protein (g)", min_value=0, max_value=1000, value=180)
                carbs = st.number_input("Carbs (g)", min_value=0, max_value=2000, value=250)
                fat = st.number_input("Fat (g)", min_value=0, max_value=1000, value=70)
                notes = st.text_area("Notes")
                
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
                        st.rerun()
        
        with col2:
            st.subheader("📊 Nutrition History")
            macros = list_macros()
            if macros:
                for m in reversed(macros[-7:]):
                    st.write(f"📅 {m['entry_date']} | {m['calories']} kcal | P:{m['protein_g']}g C:{m['carbs_g']}g F:{m['fat_g']}g")
            else:
                st.info("No nutrition logged yet.")
    
    # ─────────────────────────────────────────────
    # Tab 5: Analytics
    # ─────────────────────────────────────────────
    with tabs[5]:
        st.title("📊 Analytics & Progress")
        
        if selected_profile:
            summary = get_workout_summary(st.session_state.selected_profile_id)
            if summary:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Workouts", summary['total_workouts'])
                with col2:
                    st.metric("Total Volume (kg)", f"{summary['total_volume_kg']:.0f}")
                with col3:
                    st.metric("Most Worked", summary['most_worked_muscle_group'])
                with col4:
                    st.metric("Workouts/Week", summary['workouts_per_week'])
                
                st.divider()
                st.success(f"**💡 Recommendation:** {summary['recommendation']}")
        else:
            st.warning("⚠️ Select a profile to view analytics!")
    
    # ─────────────────────────────────────────────
    # Tab 6: AI Coach
    # ─────────────────────────────────────────────
    with tabs[6]:
        st.title("🤖 AI Fitness Coach")
        st.markdown("Ask for personalized fitness advice powered by Gemini AI")
        
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
                with st.spinner("🤖 AI is thinking..."):
                    response = chat_with_ai(str(st.session_state.selected_profile_id), message)
                st.divider()
                st.info(response.get("reply", "No response"))
            elif send_btn:
                st.warning("⚠️ Type a message!")
            
            st.divider()
            st.subheader("💡 Quick Questions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🥩 Protein Target"):
                    with st.spinner("🤖"):
                        r = chat_with_ai(str(st.session_state.selected_profile_id), "How much protein should I eat?")
                    st.info(r.get("reply"))
            
            with col2:
                if st.button("💪 Exercise Tips"):
                    with st.spinner("🤖"):
                        r = chat_with_ai(str(st.session_state.selected_profile_id), "What exercises should I do?")
                    st.info(r.get("reply"))
            
            with col3:
                if st.button("📈 Progress Check"):
                    with st.spinner("🤖"):
                        r = chat_with_ai(str(st.session_state.selected_profile_id), "How's my progress?")
                    st.info(r.get("reply"))
        else:
            st.warning("⚠️ Create a profile first!")
    
    # ─────────────────────────────────────────────
    # Tab 7: Settings & Account Management
    # ─────────────────────────────────────────────
    with tabs[7]:
        st.title("⚙️ Account Settings")
        
        # Account Information
        st.subheader("👤 Account Information")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("User ID", st.session_state.user_id[:8] + "...")
        with col2:
            st.metric("Email", st.session_state.user_id)
        with col3:
            st.metric("Name", st.session_state.user_name)
        with col4:
            st.metric("Account Status", "Active ✅")
        
        st.divider()
        
        # User Profiles Management
        st.subheader("📋 Your Fitness Profiles")
        if profiles:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("### All Profiles")
            with col2:
                refresh_btn = st.button("🔄 Refresh", key="profiles_refresh")
                if refresh_btn:
                    st.rerun()
            
            # Display all profiles in a table-like format
            for idx, p in enumerate(profiles):
                with st.container(border=True):
                    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                    
                    with col1:
                        profile_badge = "🟢" if st.session_state.selected_profile_id == p["id"] else "⚪"
                        st.write(f"{profile_badge} **{p['name']}**")
                        st.caption(f"⚖️ {p['weight_kg']}kg • 📏 {p['height_cm']}cm • 🎂 {p['age']}y • 🎯 {p['goal'].upper()}")
                    
                    with col2:
                        st.write(f"⚙️ {p['gender']}")
                    
                    with col3:
                        if st.button("👁️ Select", key=f"select_{p['id']}", use_container_width=True):
                            st.session_state.selected_profile_id = p["id"]
                            st.success(f"Selected: {p['name']}")
                            st.rerun()
                    
                    with col4:
                        if st.button("✏️ Edit", key=f"edit_{p['id']}", use_container_width=True):
                            st.session_state[f"editing_{p['id']}"] = True
                    
                    with col5:
                        if st.button("🗑️ Delete", key=f"delete_{p['id']}", use_container_width=True):
                            try:
                                with get_api_with_auth() as client:
                                    response = client.delete(f"/profile/{p['id']}")
                                    if response.status_code == 204:
                                        st.success(f"✅ Profile deleted!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Error deleting profile")
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                    
                    # Edit mode
                    if st.session_state.get(f"editing_{p['id']}", False):
                        st.write("**Editing Mode**")
                        with st.form(f"edit_profile_{p['id']}"):
                            name = st.text_input("Name", value=p["name"])
                            weight = st.number_input("Weight (kg)", value=p["weight_kg"])
                            height = st.number_input("Height (cm)", value=p["height_cm"])
                            age = st.number_input("Age", value=p["age"])
                            goal = st.selectbox("Goal", ["fit", "muscle"], index=0 if p["goal"] == "fit" else 1)
                            
                            if st.form_submit_button("💾 Save Changes"):
                                try:
                                    with get_api_with_auth() as client:
                                        response = client.put(
                                            f"/profile/{p['id']}",
                                            json={
                                                "name": name,
                                                "weight_kg": weight,
                                                "height_cm": height,
                                                "age": age,
                                                "goal": goal,
                                            }
                                        )
                                        if response.status_code == 200:
                                            st.success("✅ Profile updated!")
                                            st.session_state[f"editing_{p['id']}"] = False
                                            st.rerun()
                                        else:
                                            st.error("❌ Error updating profile")
                                except Exception as e:
                                    st.error(f"❌ Error: {e}")
        else:
            st.info("📭 No profiles yet. Create one in the Profile tab!")
        
        st.divider()
        
        # Account Statistics
        st.subheader("📊 Account Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        exercises = list_exercises()
        logs = list_workout_logs()
        macros = list_macros()
        
        with col1:
            st.metric("Total Exercises", len(exercises))
        with col2:
            st.metric("Total Workouts Logged", len(logs))
        with col3:
            st.metric("Nutrition Days Tracked", len(macros))
        
        # Profile-specific stats
        if selected_profile and logs:
            st.subheader("📈 Profile Stats")
            profile_logs = [l for l in logs]  # In real app, would filter by profile
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Workouts (Current Profile)", len(profile_logs))
            with col2:
                if profile_logs:
                    total_volume = sum(float(l.get('weight_kg', 0) or 0) * l.get('sets', 1) for l in profile_logs)
                    st.metric("Total Volume (kg)", f"{total_volume:.0f}")
        
        st.divider()
        
        # Account Security
        st.subheader("🔒 Security & Privacy")
        
        security_col1, security_col2 = st.columns(2)
        
        with security_col1:
            st.write("**Threat Model:**")
            st.info(
                "✅ Passwords hashed with PBKDF2\n"
                "✅ JWT tokens expire in 24 hours\n"
                "✅ HTTPS recommended for production\n"
                "✅ User data isolated by account"
            )
        
        with security_col2:
            st.write("**Account Actions:**")
            if st.button("🔑 Change Password", disabled=True, help="Coming soon"):
                st.info("Password change feature coming soon!")
            
            if st.button("📥 Export My Data", help="Download all account data"):
                # Prepare data export
                export_data = {
                    "user_id": st.session_state.user_id,
                    "name": st.session_state.user_name,
                    "profiles": profiles,
                    "exercises": exercises,
                    "workout_logs": logs,
                    "macro_entries": macros,
                }
                st.success("✅ Data ready to export (JSON)")
                st.json(export_data)
        
        st.divider()
        
        # Danger Zone
        st.subheader("⚠️ Danger Zone", help="These actions cannot be undone")
        
        danger_col1, danger_col2 = st.columns(2)
        
        with danger_col1:
            if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
                st.session_state.logged_in = False
                st.session_state.token = None
                st.session_state.user_id = None
                st.session_state.user_name = None
                st.session_state.selected_profile_id = None
                st.success("✅ Logged out successfully!")
                st.rerun()
        
        with danger_col2:
            if st.button("🗑️ Delete Account", use_container_width=True, key="delete_account", type="secondary"):
                st.warning(
                    "⚠️ **This will permanently delete your account and all data.**\n\n"
                    "To confirm, type your email and click the button below."
                )
                confirm_email = st.text_input("Type your email to confirm")
                if st.button("🔴 PERMANENTLY DELETE ACCOUNT", use_container_width=True, type="secondary"):
                    if confirm_email == st.session_state.user_id:
                        st.error("Account deletion backend not yet implemented.")
                        st.info("This feature would permanently delete all user data.")
                    else:
                        st.error("❌ Email doesn't match. Account not deleted.")
    
    # Footer
    st.divider()
    st.markdown("""
        ---
        **🏋️ FitLog v2.0** | Powered by FastAPI + Streamlit + Gemini AI
        
        [API Docs](http://localhost:8000/docs) • [GitHub](#) • [Contact](#)
    """)


# ─────────────────────────────────────────────
# App Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if st.session_state.logged_in:
        main_app()
    else:
        login_page()
