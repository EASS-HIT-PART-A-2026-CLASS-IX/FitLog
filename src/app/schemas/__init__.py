"""
Pydantic schemas for API request/response validation.
"""
from .user import UserRegister, UserLogin, TokenResponse, UserResponse
from .exercise import ExerciseBase, ExerciseCreate, ExerciseUpdate, ExerciseOut
from .workout import WorkoutLogBase, WorkoutLogCreate, WorkoutLogUpdate, WorkoutLogOut, WorkoutSummaryOut
from .macro import MacroEntryBase, MacroEntryCreate, MacroEntryUpdate, MacroEntryOut, FoodAnalysisRequest, NutritionAnalysisResponse
from .profile import UserProfileBase, UserProfileCreate, UserProfileUpdate, UserProfileOut, ProteinTargetOut
from .chat import ChatRequest, ChatResponse

__all__ = [
    # User
    "UserRegister",
    "UserLogin",
    "TokenResponse",
    "UserResponse",
    # Exercise
    "ExerciseBase",
    "ExerciseCreate",
    "ExerciseUpdate",
    "ExerciseOut",
    # Workout
    "WorkoutLogBase",
    "WorkoutLogCreate",
    "WorkoutLogUpdate",
    "WorkoutLogOut",
    "WorkoutSummaryOut",
    # Macro
    "MacroEntryBase",
    "MacroEntryCreate",
    "MacroEntryUpdate",
    "MacroEntryOut",
    "FoodAnalysisRequest",
    "NutritionAnalysisResponse",
    # Profile
    "UserProfileBase",
    "UserProfileCreate",
    "UserProfileUpdate",
    "UserProfileOut",
    "ProteinTargetOut",
    # Chat
    "ChatRequest",
    "ChatResponse",
]
