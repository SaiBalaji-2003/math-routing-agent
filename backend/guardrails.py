import re
from typing import List

class InputGuardrails:
    def __init__(self):
        self.blocked_patterns = [
            r"(?i)(hack|exploit|malware|virus)",
            r"(?i)(personal\s+information|private\s+data|social\s+security)",
            r"(?i)(violent|harmful|illegal|dangerous)",
            r"(?i)(password|credit\s+card|bank\s+account)"
        ]
        self.math_keywords = [
            "equation", "derivative", "integral", "theorem", "proof",
            "calculation", "formula", "solve", "compute", "mathematics",
            "algebra", "geometry", "calculus", "statistics", "probability",
            "function", "limit", "matrix", "vector", "graph", "number",
            "polynomial", "logarithm", "exponential", "trigonometry"
        ]
    
    def validate(self, question: str) -> bool:
        """Validate input question"""
        if not question or len(question.strip()) < 3:
            return False
            
        # Check for blocked content
        for pattern in self.blocked_patterns:
            if re.search(pattern, question):
                return False
        
        # Check if it's math-related
        question_lower = question.lower()
        has_math_content = any(keyword in question_lower for keyword in self.math_keywords)
        has_numbers = bool(re.search(r'\d', question))
        has_math_symbols = bool(re.search(r'[+\-*/=^()√∑∫]', question))
        has_question_words = any(word in question_lower for word in ['what', 'how', 'why', 'where', 'when', 'explain', 'solve', 'find', 'calculate'])
        
        return has_math_content or has_numbers or has_math_symbols or has_question_words

class OutputGuardrails:
    def __init__(self):
        self.blocked_outputs = [
            "I cannot", "I'm unable", "I don't know", "I can't help"
        ]
    
    def validate(self, answer: str) -> str:
        """Validate and clean output"""
        if not answer or len(answer.strip()) < 10:
            return "I apologize, but I couldn't generate a comprehensive answer. Please try rephrasing your question."
        
        # Ensure educational format
        if not answer.startswith("**Step-by-step"):
            answer = "**Educational Mathematical Response:**\n\n" + answer
        
        # Add educational disclaimer if needed
        if any(blocked in answer for blocked in self.blocked_outputs):
            answer += "\n\n**Note:** This is an educational mathematics system. Please ensure your question is related to mathematical concepts."
        
        return answer