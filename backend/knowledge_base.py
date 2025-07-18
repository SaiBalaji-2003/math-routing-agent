import chromadb
import logging
import os
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class KnowledgeBase:
    def __init__(self):
        self.client = None
        self.collection = None
        self.collection_name = "math_knowledge_base"
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize the knowledge base with ChromaDB"""
        try:
            # Initialize ChromaDB client (uses default embeddings)
            self.client = chromadb.PersistentClient(path="./chroma_db")
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Mathematical knowledge base"}
            )
            
            # Load initial data if collection is empty
            if self.collection.count() == 0:
                await self.load_initial_data()
            
            self.logger.info("Knowledge base initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize knowledge base: {str(e)}")
            # Don't raise error to allow app to start
    
    async def load_initial_data(self):
        """Load initial mathematical knowledge data"""
        initial_data = [
            {
                "id": "calc_derivative_1",
                "question": "What is the derivative of x²?",
                "answer": """**Step-by-step solution:**

1. **Identify the function:** f(x) = x²
2. **Apply the power rule:** For f(x) = xⁿ, f'(x) = n·xⁿ⁻¹
3. **Calculate:** f'(x) = 2·x²⁻¹ = 2x
4. **Verify:** The derivative of x² is 2x

**Key concept:** The power rule is fundamental in calculus for finding derivatives of polynomial functions.""",
                "topic": "calculus",
                "difficulty": "basic"
            },
            {
                "id": "algebra_quadratic_1",
                "question": "How do you solve a quadratic equation?",
                "answer": """**Step-by-step solution for ax² + bx + c = 0:**

1. **Identify coefficients:** a, b, and c
2. **Apply quadratic formula:** x = (-b ± √(b² - 4ac)) / (2a)
3. **Calculate discriminant:** Δ = b² - 4ac
4. **Determine solutions:**
   - If Δ > 0: Two real solutions
   - If Δ = 0: One real solution
   - If Δ < 0: Two complex solutions

**Example:** For x² - 5x + 6 = 0
- a = 1, b = -5, c = 6
- x = (5 ± √(25 - 24)) / 2 = (5 ± 1) / 2
- Solutions: x = 3 or x = 2""",
                "topic": "algebra",
                "difficulty": "intermediate"
            },
            {
                "id": "geometry_pythagorean_1",
                "question": "What is the Pythagorean theorem?",
                "answer": """**The Pythagorean Theorem:**

1. **Statement:** In a right triangle, a² + b² = c²
2. **Where:**
   - a and b are the lengths of the legs
   - c is the length of the hypotenuse (longest side)
3. **Application steps:**
   - Identify the right triangle
   - Label the sides (legs and hypotenuse)
   - Substitute known values
   - Solve for the unknown side

**Example:** If legs are 3 and 4 units:
- a² + b² = c²
- 3² + 4² = c²
- 9 + 16 = c²
- c = √25 = 5 units""",
                "topic": "geometry",
                "difficulty": "basic"
            }
        ]
        
        # Add data to ChromaDB (uses default embeddings)
        documents = []
        metadatas = []
        ids = []
        
        for item in initial_data:
            documents.append(item["answer"])
            metadatas.append({
                "question": item["question"],
                "topic": item["topic"],
                "difficulty": item["difficulty"]
            })
            ids.append(item["id"])
        
        try:
            # Use ChromaDB's default embedding function
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            self.logger.info(f"Loaded {len(initial_data)} documents into knowledge base")
        except Exception as e:
            self.logger.error(f"Error loading initial data: {str(e)}")
    
    async def get_answer(self, question: str) -> Dict:
        """Retrieve answer from knowledge base"""
        try:
            if not self.collection:
                return {
                    "answer": "Knowledge base not initialized",
                    "confidence": 0.0,
                    "sources": [],
                    "metadata": {}
                }
            
            # Search in ChromaDB
            results = self.collection.query(
                query_texts=[question],
                n_results=1
            )
            
            if results["documents"] and len(results["documents"][0]) > 0:
                return {
                    "answer": results["documents"][0][0],
                    "confidence": 0.9,
                    "sources": ["Knowledge Base (ChromaDB)"],
                    "metadata": results["metadatas"][0][0] if results["metadatas"] else {}
                }
            else:
                return {
                    "answer": "No relevant information found in knowledge base",
                    "confidence": 0.0,
                    "sources": [],
                    "metadata": {}
                }
                
        except Exception as e:
            self.logger.error(f"Error retrieving from knowledge base: {str(e)}")
            return {
                "answer": f"Error accessing knowledge base: {str(e)}",
                "confidence": 0.0,
                "sources": [],
                "metadata": {}
            }
    
    def is_healthy(self) -> bool:
        """Check if knowledge base is healthy"""
        try:
            return self.collection is not None and self.collection.count() > 0
        except:
            return False
    
    async def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        try:
            if not self.collection:
                return {"error": "Knowledge base not initialized"}
            
            count = self.collection.count()
            return {
                "total_documents": count,
                "status": "healthy" if count > 0 else "empty",
                "embedding_model": "ChromaDB default",
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}