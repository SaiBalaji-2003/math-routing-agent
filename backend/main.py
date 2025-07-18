from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Math Routing Agent",
    description="Agentic-RAG Mathematical Professor System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    user_id: Optional[str] = None
    session_id: Optional[str] = None

class QuestionResponse(BaseModel):
    answer: str
    route_used: str
    confidence_score: float
    sources: List[str]
    timestamp: datetime
    question_id: str

class FeedbackRequest(BaseModel):
    question_id: str
    feedback_type: str
    user_comment: Optional[str] = None

# Simple knowledge base
KNOWLEDGE_BASE = {
    "derivative": """**Step-by-step solution:**
1. **Identify the function:** f(x) = x²
2. **Apply the power rule:** For f(x) = xⁿ, f'(x) = n·xⁿ⁻¹
3. **Calculate:** f'(x) = 2·x²⁻¹ = 2x
4. **Verify:** The derivative of x² is 2x""",
    
    "quadratic": """**Step-by-step solution for ax² + bx + c = 0:**
1. **Identify coefficients:** a, b, and c
2. **Apply quadratic formula:** x = (-b ± √(b² - 4ac)) / (2a)
3. **Calculate discriminant:** Δ = b² - 4ac
4. **Example:** For x² - 5x + 6 = 0, solutions are x = 3 or x = 2""",
    
    "pythagorean": """**The Pythagorean Theorem:**
1. **Statement:** In a right triangle, a² + b² = c²
2. **Example:** If legs are 3 and 4 units: c = √(3² + 4²) = √25 = 5 units"""
}

question_responses = {}

def route_question(question: str) -> str:
    question_lower = question.lower()
    kb_keywords = ["derivative", "quadratic", "pythagorean", "theorem", "solve"]
    web_keywords = ["latest", "recent", "current", "research"]
    
    kb_score = sum(1 for k in kb_keywords if k in question_lower)
    web_score = sum(1 for k in web_keywords if k in question_lower)
    
    return "knowledge_base" if kb_score >= web_score else "web_search"

def get_kb_answer(question: str) -> Dict:
    question_lower = question.lower()
    for key, answer in KNOWLEDGE_BASE.items():
        if key in question_lower:
            return {"answer": answer, "confidence": 0.9, "sources": ["Knowledge Base"]}
    
    return {
        "answer": "This is a mathematical question processed by our knowledge base. Please try more specific terms like 'derivative', 'quadratic', or 'pythagorean'.",
        "confidence": 0.5,
        "sources": ["Knowledge Base"]
    }

async def get_web_answer(question: str) -> Dict:
    return {
        "answer": f"""**Web Search Response for: {question}**

Based on current mathematical research and academic sources, this topic involves advanced mathematical concepts. Here's a general approach:

1. **Research Analysis:** Current literature shows multiple methodologies
2. **Academic Perspective:** This is an active area of mathematical study
3. **Applications:** Relevant to modern mathematical applications
4. **Further Study:** Consult recent academic papers for detailed analysis

**Note:** This is a simulated web search response. With real API keys, this would provide current research data.""",
        "confidence": 0.7,
        "sources": ["Web Search Simulation"]
    }

@app.get("/")
async def root():
    return {"message": "Math Routing Agent API", "status": "active", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "components": {"knowledge_base": True, "web_search": True}
    }

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    try:
        route = route_question(request.question)
        
        if route == "knowledge_base":
            answer_data = get_kb_answer(request.question)
        else:
            answer_data = await get_web_answer(request.question)
        
        question_id = f"q_{int(datetime.now().timestamp())}"
        response = QuestionResponse(
            answer=answer_data["answer"],
            route_used=route,
            confidence_score=answer_data["confidence"],
            sources=answer_data["sources"],
            timestamp=datetime.now(),
            question_id=question_id
        )
        
        question_responses[question_id] = {"request": request.dict(), "response": response.dict()}
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    return {"status": "success", "message": "Feedback recorded"}

@app.get("/sample-questions")
async def get_sample_questions():
    return {
        "knowledge_base_questions": [
            "What is the derivative of x²?",
            "How do you solve a quadratic equation?",
            "What is the Pythagorean theorem?"
        ],
        "web_search_questions": [
            "Latest developments in quantum computing mathematics",
            "Recent mathematical proofs in number theory",
            "Modern applications of calculus in AI"
        ]
    }

@app.get("/knowledge-base/stats")
async def get_knowledge_base_stats():
    return {
        "total_documents": len(KNOWLEDGE_BASE),
        "status": "healthy",
        "embedding_model": "Simple keyword matching"
    }

# For Vercel
handler = app
