# 🏋️ FitLog Frontend – Streamlit Dashboard

Beautiful, user-friendly Streamlit dashboard for the FitLog fitness tracking API.

## Features

✅ **User Profile Management** - Create and manage fitness profiles with goals  
✅ **Exercise Library** - Browse and add exercises to your collection  
✅ **Workout Logging** - Log sets, reps, weight, and notes for each session  
✅ **Nutrition Tracking** - Track daily macros (calories, protein, carbs, fat)  
✅ **Protein Calculator** - AI-powered daily protein target based on your goal  
✅ **Dashboard Summary** - Quick view of recent workouts and nutrition  

## Setup

### Prerequisites
- Python 3.11+
- FitLog API running on `http://127.0.0.1:8000`

### Install Dependencies

```bash
cd FitLog
uv sync  # or uv pip install -r requirements.txt
```

### Run the Frontend

```bash
uv run streamlit run frontend/streamlit_app.py
```

The dashboard opens at: **http://127.0.0.1:8501**

## Usage

1. **Start the Backend API** (in a terminal):
   ```bash
   uv run uvicorn app.main:app --reload
   ```

2. **Start the Frontend** (in another terminal):
   ```bash
   uv run streamlit run frontend/streamlit_app.py
   ```

3. **Use the Dashboard**:
   - Select or create a user profile
   - Add exercises to your library
   - Log workouts with sets, reps, and weight
   - Track daily nutrition (macros)
   - View your protein target (extra feature!)

## Project Structure

```
frontend/
├── streamlit_app.py    # Main dashboard application
└── README.md           # This file
```

## Architecture

The frontend is a **pure frontend layer** that:
- Makes HTTP calls to `http://127.0.0.1:8000` (the FastAPI backend)
- Manages no local state (all data lives in the API)
- Provides quick add/view for all core resources
- Can run locally on the same machine or remotely

## Extra Feature: Protein Calculator

The dashboard includes an **AI-powered protein target calculator** that:
- Analyzes your goal ("fit" or "muscle")
- Uses ISSN/ACSM multipliers (1.6 g/kg or 2.2 g/kg)
- Provides personalized recommendations with evidence-based guidance

## Support

For backend API issues, refer to the main [README.md](../README.md).

For Streamlit docs, visit: https://docs.streamlit.io/
