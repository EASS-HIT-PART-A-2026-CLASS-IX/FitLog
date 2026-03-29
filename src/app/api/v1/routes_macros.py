"""Macro / nutrition entries CRUD router."""
import os
import json
from uuid import UUID

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status, Query
from openai import OpenAI

from src.app.schemas import MacroEntryCreate, MacroEntryOut, MacroEntryUpdate, FoodAnalysisRequest, NutritionAnalysisResponse
from app.repository import macros_repo

load_dotenv()

router = APIRouter(prefix="/macros", tags=["Macro Entries"])

_GROQ_MODEL = "llama-3.3-70b-versatile"


def _get_groq_client() -> OpenAI:
    """Get Groq client for food analysis."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GROQ_API_KEY not configured. Set it in your .env file.",
        )
    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )


@router.post("/analyze-food", response_model=NutritionAnalysisResponse, summary="Analyze food and calculate macros using AI")
def analyze_food_nutrition(body: FoodAnalysisRequest):
    """
    Analyze food description using Groq AI and return estimated nutritional values.
    Takes a natural language description of food (e.g., "2 eggs, bacon, and toast")
    and returns calculated calories, protein, carbs, and fat.
    """
    try:
        client = _get_groq_client()
        
        prompt = f"""You are a nutrition expert. Analyze this food description and provide nutritional estimates.

Food: {body.food_description}

Please respond ONLY with valid JSON (no other text) in this exact format:
{{
  "calories": <number between 0-5000>,
  "protein_g": <number between 0-200>,
  "carbs_g": <number between 0-500>,
  "fat_g": <number between 0-200>,
  "analysis": "<brief 1-2 sentence explanation of your estimates>"
}}

Be as accurate as possible using standard nutrition databases. Estimates should be realistic and reasonable."""
        
        response = client.chat.completions.create(
            model=_GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a nutrition expert that responds ONLY with valid JSON, no markdown, no code blocks, just pure JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temp for more consistent output
            max_tokens=300,
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from response (in case model adds extra text)
        if "{" in response_text and "}" in response_text:
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            json_str = response_text[start_idx:end_idx]
            nutrition_data = json.loads(json_str)
        else:
            nutrition_data = json.loads(response_text)
        
        # Validate the response has required fields
        required_fields = ["calories", "protein_g", "carbs_g", "fat_g", "analysis"]
        if not all(field in nutrition_data for field in required_fields):
            raise ValueError("Missing required nutrition fields in response")
        
        return NutritionAnalysisResponse(
            food_description=body.food_description,
            calories=float(nutrition_data["calories"]),
            protein_g=float(nutrition_data["protein_g"]),
            carbs_g=float(nutrition_data["carbs_g"]),
            fat_g=float(nutrition_data["fat_g"]),
            analysis=str(nutrition_data["analysis"]),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze food: {str(e)}",
        )



@router.get("/", response_model=list[MacroEntryOut], summary="List all macro entries")
def list_macros(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """List macros with pagination. Default 100 per page, max 500."""
    return macros_repo.list(limit=limit, offset=offset)


@router.get("/{entry_id}", response_model=MacroEntryOut, summary="Get a macro entry by ID")
def get_macro(entry_id: UUID):
    record = macros_repo.get(entry_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Macro entry not found")
    return record


@router.post("/", response_model=MacroEntryOut, status_code=status.HTTP_201_CREATED, summary="Log daily macros")
def create_macro(body: MacroEntryCreate):
    return macros_repo.create(body.model_dump())


@router.put("/{entry_id}", response_model=MacroEntryOut, summary="Update a macro entry")
def update_macro(entry_id: UUID, body: MacroEntryUpdate):
    updated = macros_repo.update(entry_id, body.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Macro entry not found")
    return updated


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a macro entry")
def delete_macro(entry_id: UUID):
    if not macros_repo.delete(entry_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Macro entry not found")
