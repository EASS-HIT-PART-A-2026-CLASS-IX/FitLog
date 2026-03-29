"""API v1 routes initialization."""
from . import routes_auth
from . import routes_exercises
from . import routes_workout_logs
from . import routes_macros
from . import routes_profile
from . import routes_ai_assistant

__all__ = [
    "routes_auth",
    "routes_exercises",
    "routes_workout_logs",
    "routes_macros",
    "routes_profile",
    "routes_ai_assistant",
]
