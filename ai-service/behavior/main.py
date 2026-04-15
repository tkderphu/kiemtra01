from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from predictor import BehaviorPredictor

app = FastAPI(title="Behavior Analysis Service", version="1.0")
predictor = BehaviorPredictor()

class Action(BaseModel):
    action: str  # view, click, add_to_cart, purchase...
    product_id: Optional[int] = 0
    timestamp: int

class AnalyzeRequest(BaseModel):
    user_id: str
    session_id: str
    recent_actions: Optional[List[Action]] = []

class AnalyzeResponse(BaseModel):
    user_embedding: List[float]
    segment: int
    segment_name: str
    churn_risk: float
    predicted_ltv: float
    next_most_likely_action: str

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_behavior(request: AnalyzeRequest):
    try:
        actions = []
        if request.recent_actions:
            actions = [a.dict() for a in request.recent_actions]
        result = predictor.predict(
            user_id=request.user_id,
            session_id=request.session_id,
            recent_actions=actions
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": True}
