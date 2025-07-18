import json
from datetime import datetime
from typing import Dict

class FeedbackSystem:
    def __init__(self):
        self.feedback_data = []
    
    async def process_feedback(self, question_id: str, feedback_type: str, 
                             user_comment: str, question_data: Dict) -> Dict:
        """Process user feedback"""
        feedback_entry = {
            "question_id": question_id,
            "feedback_type": feedback_type,
            "user_comment": user_comment,
            "timestamp": datetime.now().isoformat(),
            "question_data": question_data
        }
        
        self.feedback_data.append(feedback_entry)
        
        # Log feedback for analysis
        print(f"Feedback received: {feedback_type} for question {question_id}")
        
        return {"status": "processed", "feedback_id": len(self.feedback_data)}