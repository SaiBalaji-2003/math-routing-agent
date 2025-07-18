from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from knowledge_base import KnowledgeBase
from web_search import WebSearchMCP
from guardrails import InputGuardrails, OutputGuardrails
from feedback_system import FeedbackSystem
from routing_agent import RoutingAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Math Routing Agent",
    description="Agentic-RAG Mathematical Professor System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://*.vercel.app",
        "https://*.netlify.app",
        "*"  # Allow all origins for demo purposes
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
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
    user_id: Optional[str] = None

# Initialize system components
knowledge_base = KnowledgeBase()
web_search = WebSearchMCP()
input_guardrails = InputGuardrails()
output_guardrails = OutputGuardrails()
feedback_system = FeedbackSystem()
routing_agent = RoutingAgent(knowledge_base, web_search)

# Store for question-response pairs
question_responses = {}

@app.on_event("startup")
async def startup_event():
    """Initialize system components on startup"""
    logger.info("Starting Math Routing Agent...")
    try:
        await knowledge_base.initialize()
        await web_search.initialize()
        logger.info("System initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize system: {str(e)}")
        # Don't raise error to allow app to start

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Math Routing Agent API", 
        "status": "active",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "components": {
            "knowledge_base": knowledge_base.is_healthy(),
            "web_search": web_search.is_healthy(),
            "guardrails": True
        }
    }

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Process a mathematical question"""
    try:
        # Input validation and guardrails
        if not input_guardrails.validate(request.question):
            raise HTTPException(
                status_code=400, 
                detail="Question failed input validation"
            )
        
        # Route the question
        route_decision = await routing_agent.route_question(request.question)
        
        # Get answer based on route
        if route_decision["route"] == "knowledge_base":
            answer_data = await knowledge_base.get_answer(request.question)
        else:
            answer_data = await web_search.get_answer(request.question)
        
        # Output guardrails
        validated_answer = output_guardrails.validate(answer_data["answer"])
        
        # Create response
        question_id = f"q_{int(datetime.now().timestamp())}"
        response = QuestionResponse(
            answer=validated_answer,
            route_used=route_decision["route"],
            confidence_score=answer_data["confidence"],
            sources=answer_data["sources"],
            timestamp=datetime.now(),
            question_id=question_id
        )
        
        # Store for feedback
        question_responses[question_id] = {
            "request": request.dict(),
            "response": response.dict(),
            "route_decision": route_decision
        }
        
        logger.info(f"Question processed via {route_decision['route']}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing question: {str(e)}"
        )

@app.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit feedback for a question-response pair"""
    try:
        if request.question_id not in question_responses:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Process feedback
        feedback_result = await feedback_system.process_feedback(
            question_id=request.question_id,
            feedback_type=request.feedback_type,
            user_comment=request.user_comment,
            question_data=question_responses[request.question_id]
        )
        
        logger.info(f"Feedback processed for question {request.question_id}")
        return {"status": "success", "message": "Feedback recorded"}
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing feedback")

@app.get("/knowledge-base/stats")
async def get_knowledge_base_stats():
    """Get knowledge base statistics"""
    try:
        stats = await knowledge_base.get_stats()
        return stats
    except Exception as e:
        return {"error": str(e)}

@app.get("/sample-questions")
async def get_sample_questions():
    """Get sample questions for testing"""
    return {
        "knowledge_base_questions": [
            "What is the derivative of x²?",
            "How do you solve a quadratic equation?",
            "What is the Pythagorean theorem?",
            "Explain the fundamental theorem of calculus",
            "What is the chain rule in calculus?"
        ],
        "web_search_questions": [
            "Latest developments in quantum computing mathematics",
            "Recent mathematical proofs in number theory",
            "Modern applications of calculus in AI",
            "Current research in mathematical optimization",
            "New discoveries in graph theory"
        ]
    }

# For Vercel deployment
if __name__ != "__main__":
    # This is for Vercel
    handler = app