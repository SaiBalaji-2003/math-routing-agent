import re
from typing import Dict
import logging

class RoutingAgent:
    def __init__(self, knowledge_base, web_search):
        self.knowledge_base = knowledge_base
        self.web_search = web_search
        self.logger = logging.getLogger(__name__)
        
        # Keywords that suggest knowledge base content
        self.kb_keywords = [
            "derivative", "integral", "quadratic", "pythagorean", 
            "theorem", "basic", "fundamental", "simple", "formula",
            "solve", "what is", "how to", "definition", "equation"
        ]
        
        # Keywords that suggest web search
        self.web_keywords = [
            "latest", "recent", "new", "current", "modern", 
            "advanced", "cutting-edge", "development", "research",
            "breakthrough", "discovery", "innovation", "trend"
        ]
    
    async def route_question(self, question: str) -> Dict:
        """Decide whether to use knowledge base or web search"""
        question_lower = question.lower()
        
        # Count keyword matches
        kb_score = sum(1 for keyword in self.kb_keywords 
                      if keyword in question_lower)
        web_score = sum(1 for keyword in self.web_keywords 
                       if keyword in question_lower)
        
        # Check for basic math patterns
        has_basic_math = bool(re.search(r'(x\^?\d|derivative|integral|equation)', question_lower))
        
        # Routing decision logic
        if kb_score > web_score or has_basic_math:
            route = "knowledge_base"
            confidence = min(0.9, 0.6 + (kb_score * 0.1))
            reason = "Question matches knowledge base content"
        else:
            route = "web_search"
            confidence = min(0.8, 0.5 + (web_score * 0.1))
            reason = "Question requires current information or advanced topics"
        
        self.logger.info(f"Routing decision: {route} (confidence: {confidence:.2f})")
        
        return {
            "route": route,
            "confidence": confidence,
            "reason": reason,
            "kb_score": kb_score,
            "web_score": web_score
        }