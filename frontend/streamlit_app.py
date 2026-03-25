"""
FitLog Frontend – Streamlit Dashboard
Connects to the FitLog FastAPI backend at http://127.0.0.1:8000
"""
import streamlit as st
import httpx
from datetime import date
from uuid import UUID

# Configuration
API_BASE = "http://127.0.0.1:8000"
st.set_page_config(page_title="FitLog", page_icon="🏋️", layout="wide")

# Initialize session state for selected profile
if "selected_profile_id" not in st.session_state:
    st.session_state.selected_profile_id = None


def get_api():
    """Create HTTP client for API calls."""
    return httpx.Client(base_url=API_BASE, timeout=10.0)


def list_profiles():
    """Fetch all profiles from API."""
    try:
        with get_api() as client:
            response = client.get("/profile/")
            return response.json()
    except Exception as e:
        st.error(f"❌ Failed to fetch profiles: {e}")
        return []


def create_profile(data):
    """Create a new profile."""
    try:
        with get_api() as client:
            response = client.post("/profile/", json=data)
            if response.status_code == 201:
                return response.json()
            else:
                st.error(f"Error: {response.text}")
                return None
    except Exception as e:
        st.error(f"❌ Failed to create profile: {e}")
        return None


def get_profile(profile_id):
    """Fetch a specific profile."""
    try:
        with get_api() as client:
            response = client.get(f"/profile/{profile_id}")
            return response.json()
    except Exception as e:
        st.error(f"❌ Failed to fetch profile: {e}")
        return None


def get_protein_target(profile_id):
    """Get protein target for a profile."""
    try:
        with get_api() as client:
            response = client.get(f"/profile/{profile_id}/protein-target")
            return response.json()
    except Exception as e:
        st.error(f"❌ Failed to fetch protein target: {e}")
        return None


def list_exercises():
    """Fetch all exercises."""
    try:
        with get_api() as client:
            response = client.get("/exercises/")
            return response.json()
    except Exception as e:
        st.error(f"❌ Failed to fetch exercises: {e}")
        return []


def create_exercise(data):
    """Create a new exercise."""
    try:
        with get_api() as client:
            response = client.post("/exercises/", json=data)
            if response.status_code == 201:
                return response.json()
            else:
                st.error(f"Error: {response.text}")
                return None
    except Exception as e:
        st.error(f"❌ Failed to create exercise: {e}")
        return None


def list_workout_logs():
    """Fetch all workout logs."""
    try:
        with get_api() as client:
            response = client.get("/logs/")
            return response.json()
    except Exception as e:
        st.error(f"❌ Failed to fetch workout logs: {e}")
        return []


def create_workout_log(data):
    """Log a new workout."""
    try:
        with get_api() as client:
            response = client.post("/logs/", json=data)
            if response.status_code == 201:
                return response.json()
            else:
                st.error(f"Error: {response.text}")
                return None
    except Exception as e:
        st.error(f"❌ Failed to log workout: {e}")
        return None


def list_macros():
    """Fetch all macro entries."""
    try:
        with get_api() as client:
            response = client.get("/macros/")
            return response.json()
    except Exception as e:
        st.error(f"❌ Failed to fetch macros: {e}")
        return []


def create_macro(data):
    """Log daily macros."""
    try:
        with get_api() as client:
            response = client.post("/macros/", json=data)
            if response.status_code == 201:
                return response.json()
            else:
                st.error(f"Error: {response.text}")
                return None
    except Exception as e:
        st.error(f"❌ Failed to log macros: {e}")
        return None


def chat_with_ai(user_id: str, message: str) -> dict:
    """Send a message to the AI fitness assistant."""
    try:
        with get_api() as client:
            response = client.post("/ai/chat", json={
                "user_id": user_id,
                "message": message
            })
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error: {response.text}")
                return {"reply": "Error communicating with AI"}
    except Exception as e:
        st.error(f"❌ Failed to chat with AI: {e}")
        return {"reply": "Connection error"}


# ─────────────────────────────────────────────
# UI Layout
# ─────────────────────────────────────────────

st.title("🏋️ FitLog Dashboard")
st.markdown("Your fitness & nutrition tracking hub")

# Sidebar for profile selection
st.sidebar.header("📊 User Profile")
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

# Main tabs
tabs = st.tabs(["Dashboard", "Profile", "Exercises", "Workout Logs", "Macros", "AI Assistant"])

# ─────────────────────────────────────────────
# Tab 1: Dashboard (Summary + Protein Calculator)
# ─────────────────────────────────────────────
with tabs[0]:
    st.subheader("📈 Dashboard")
    
    if selected_profile:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("💪 Name", selected_profile["name"])
        with col2:
            st.metric("⚖️ Weight", f"{selected_profile['weight_kg']} kg")
        with col3:
            st.metric("🎯 Goal", selected_profile["goal"].upper())
        
        # Protein Calculator (Extra Feature)
        st.divider()
        st.subheader("🥩 Protein Target Calculator")
        
        protein_target = get_protein_target(st.session_state.selected_profile_id)
        if protein_target:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Daily Protein Target", f"{protein_target['protein_g']} g")
            with col2:
                st.metric("Multiplier", f"{protein_target['multiplier_g_per_kg']} g/kg")
            with col3:
                st.metric("Based on", f"{protein_target['weight_kg']} kg")
            
            st.info(protein_target["recommendation"])
        
        # Recent Workout Logs
        st.divider()
        st.subheader("📝 Recent Workouts")
        logs = list_workout_logs()
        recent_logs = [l for l in logs if l.get("exercise_id")][-3:] if logs else []
        
        if recent_logs:
            for log in reversed(recent_logs):
                st.write(f"📅 {log['log_date']} | {log['sets']}×{log['reps']} @ {log['weight_kg']} kg")
        else:
            st.write("No workouts logged yet.")
        
        # Recent Macros
        st.divider()
        st.subheader("🥗 Recent Nutrition")
        macros = list_macros()
        recent_macros = macros[-3:] if macros else []
        
        if recent_macros:
            for macro in reversed(recent_macros):
                st.write(
                    f"📅 {macro['entry_date']} | {macro['calories']} kcal | "
                    f"P:{macro['protein_g']}g C:{macro['carbs_g']}g F:{macro['fat_g']}g"
                )
        else:
            st.write("No nutrition logged yet.")
    else:
        st.warning("⚠️ No profiles found. Create one in the Profile tab.")

# ─────────────────────────────────────────────
# Tab 2: Profile Management
# ─────────────────────────────────────────────
with tabs[1]:
    st.subheader("👤 Manage Profiles")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create New Profile")
        with st.form("create_profile_form"):
            name = st.text_input("Name", placeholder="Alex Fitness")
            weight = st.number_input("Weight (kg)", min_value=30, max_value=500, value=80)
            height = st.number_input("Height (cm)", min_value=100, max_value=250, value=178)
            age = st.number_input("Age", min_value=10, max_value=120, value=28)
            gender = st.selectbox("Gender", ["male", "female", "other"])
            goal = st.selectbox("Goal", ["fit", "muscle"])
            
            if st.form_submit_button("✨ Create Profile"):
                new_profile = create_profile({
                    "name": name,
                    "weight_kg": weight,
                    "height_cm": height,
                    "age": age,
                    "gender": gender,
                    "goal": goal,
                })
                if new_profile:
                    st.success(f"✅ Profile '{name}' created!")
                    st.rerun()
    
    with col2:
        st.subheader("All Profiles")
        if profiles:
            for p in profiles:
                st.write(f"👤 **{p['name']}** | {p['age']} yrs | {p['weight_kg']} kg | 🎯 {p['goal']}")
        else:
            st.write("No profiles yet.")

# ─────────────────────────────────────────────
# Tab 3: Exercise Management
# ─────────────────────────────────────────────
with tabs[2]:
    st.subheader("🏋️ Exercises")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create New Exercise")
        with st.form("create_exercise_form"):
            ex_name = st.text_input("Exercise Name", placeholder="Barbell Squat")
            category = st.selectbox("Category", ["strength", "cardio", "flexibility"])
            muscle = st.selectbox("Muscle Group", ["legs", "chest", "back", "shoulders", "arms", "core", "full-body"])
            description = st.text_area("Description (optional)", placeholder="King of compound movements...")
            
            if st.form_submit_button("➕ Add Exercise"):
                new_exercise = create_exercise({
                    "name": ex_name,
                    "category": category,
                    "muscle_group": muscle,
                    "description": description if description else None,
                })
                if new_exercise:
                    st.success(f"✅ Exercise '{ex_name}' added!")
                    st.rerun()
    
    with col2:
        st.subheader("All Exercises")
        exercises = list_exercises()
        if exercises:
            for ex in exercises:
                st.write(f"💪 **{ex['name']}** [{ex['category']}] - {ex['muscle_group']}")
        else:
            st.write("No exercises yet.")

# ─────────────────────────────────────────────
# Tab 4: Workout Logs
# ─────────────────────────────────────────────
with tabs[3]:
    st.subheader("📝 Log Workout")
    
    exercises = list_exercises()
    if exercises:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Log New Workout")
            with st.form("log_workout_form"):
                exercise_name = st.selectbox(
                    "Exercise",
                    exercises,
                    format_func=lambda x: x["name"]
                )
                log_date = st.date_input("Date", value=date.today())
                sets = st.number_input("Sets", min_value=1, max_value=100, value=3)
                reps = st.number_input("Reps", min_value=1, max_value=1000, value=8)
                weight = st.number_input("Weight (kg)", min_value=0, max_value=1000, value=80.0)
                notes = st.text_area("Notes (optional)")
                
                if st.form_submit_button("📝 Log Workout"):
                    new_log = create_workout_log({
                        "exercise_id": exercise_name["id"],
                        "log_date": str(log_date),
                        "sets": int(sets),
                        "reps": int(reps),
                        "weight_kg": float(weight),
                        "notes": notes if notes else None,
                    })
                    if new_log:
                        st.success(f"✅ Workout logged!")
                        st.rerun()
        
        with col2:
            st.subheader("Recent Workouts")
            logs = list_workout_logs()
            if logs:
                for log in reversed(logs[-10:]):
                    st.write(
                        f"📅 {log['log_date']} | {log['sets']}×{log['reps']} @ {log['weight_kg']} kg"
                    )
            else:
                st.write("No workouts logged.")
    else:
        st.warning("⚠️ Create exercises first!")

# ─────────────────────────────────────────────
# Tab 5: Macros
# ─────────────────────────────────────────────
with tabs[4]:
    st.subheader("🥗 Log Daily Macros")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Log Macros")
        with st.form("log_macros_form"):
            macro_date = st.date_input("Date", value=date.today(), key="macro_date")
            calories = st.number_input("Calories", min_value=0, max_value=20000, value=2200)
            protein = st.number_input("Protein (g)", min_value=0, max_value=1000, value=180)
            carbs = st.number_input("Carbs (g)", min_value=0, max_value=2000, value=250)
            fat = st.number_input("Fat (g)", min_value=0, max_value=1000, value=70)
            macro_notes = st.text_area("Notes (optional)")
            
            if st.form_submit_button("➕ Log Macros"):
                new_macro = create_macro({
                    "entry_date": str(macro_date),
                    "calories": float(calories),
                    "protein_g": float(protein),
                    "carbs_g": float(carbs),
                    "fat_g": float(fat),
                    "notes": macro_notes if macro_notes else None,
                })
                if new_macro:
                    st.success("✅ Macros logged!")
                    st.rerun()
    
    with col2:
        st.subheader("Nutrition History")
        macros = list_macros()
        if macros:
            for macro in reversed(macros[-7:]):
                st.write(
                    f"📅 {macro['entry_date']} | {macro['calories']} kcal | "
                    f"P:{macro['protein_g']}g C:{macro['carbs_g']}g F:{macro['fat_g']}g"
                )
        else:
            st.write("No nutrition logged yet.")

# ─────────────────────────────────────────────
# Tab 6: AI Assistant
# ─────────────────────────────────────────────
with tabs[5]:
    st.subheader("🤖 AI Fitness Assistant")
    st.markdown("Ask the AI for personalized fitness advice based on your profile and workout data")
    
    if selected_profile:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_message = st.text_area(
                "💬 Ask me anything",
                placeholder="e.g., How much protein should I eat today? What exercises should I focus on?",
                height=100,
                key="ai_message"
            )
        
        with col2:
            st.write("")
            st.write("")
            send_button = st.button("🚀 Send", use_container_width=True, key="ai_send")
        
        if send_button and user_message.strip():
            with st.spinner("🤖 Fitness AI is thinking..."):
                response = chat_with_ai(
                    str(st.session_state.selected_profile_id),
                    user_message
                )
            
            if response:
                st.divider()
                st.write("**🤖 AI Response:**")
                st.info(response.get("reply", "No response"))
        elif send_button and not user_message.strip():
            st.warning("⚠️ Please type a message first!")
        
        # Example prompts
        st.divider()
        st.subheader("💡 Example Questions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🥩 Protein target?"):
                response = chat_with_ai(
                    str(st.session_state.selected_profile_id),
                    "How much protein should I eat today based on my profile?"
                )
                st.info(response.get("reply", "No response"))
        
        with col2:
            if st.button("💪 What exercises?"):
                response = chat_with_ai(
                    str(st.session_state.selected_profile_id),
                    "What exercises should I focus on this week based on my goal?"
                )
                st.info(response.get("reply", "No response"))
        
        with col3:
            if st.button("📊 Show progress?"):
                response = chat_with_ai(
                    str(st.session_state.selected_profile_id),
                    "How am I progressing with my fitness goal?"
                )
                st.info(response.get("reply", "No response"))
    else:
        st.warning("⚠️ Create a profile first to chat with the AI!")

# Footer
st.divider()
st.markdown(
    """
    ---
    **FitLog Frontend** | Connected to http://127.0.0.1:8000 | [API Docs](http://127.0.0.1:8000/docs)
    """
)
