"""
BrainStack - AI Service
Handles AI-powered generation of practice test questions from flashcards.
"""

import os
import json
import requests
from typing import List, Dict
from flashcard import Flashcard

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional; the app can also use real environment variables
    pass


class AIService:
    """Service for generating practice test questions using AI (Groq)."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the AI service.
        
        Args:
            api_key: Groq API key (or set via OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("Groq API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        # Use a current Groq production text model.
        # From the deprecation page, a safe choice is:
        #   llama-3.3-70b-versatile
        self.model = "llama-3.3-70b-versatile"
    
    def generate_practice_test_questions(self, flashcards: List[Flashcard], num_questions: int = 10) -> List[Dict[str, str]]:
        """
        Generate practice test questions from flashcards using AI.
        
        Args:
            flashcards: List of flashcards to generate questions from
            num_questions: Number of questions to generate
            
        Returns:
            List of dictionaries with 'question' and 'correct_answer' keys
        """
        if not flashcards:
            return []
        
        # Prepare flashcard content for the AI
        flashcard_content = "\n".join(
            f"Q: {card.front}\nA: {card.back}" for card in flashcards
        )
        
        # Create the prompt
        # NOTE: We avoid asking for JSON because models often wrap JSON or add comments.
        # Instead we ask for a simple Q/A text format we can parse robustly.
        prompt = f"""You are an educational assistant that creates creative, exam-style practice questions.
Based on the following flashcards, generate {num_questions} diverse practice test questions.

Requirements:
- Test deep understanding and application of the concepts, not just memorization
- Vary formats (short answer, conceptual, scenario-based, fill-in-the-blank, etc.)
- Keep each correct answer concise

Flashcards:
{flashcard_content}

Output format (MUST follow exactly, no extra text before or after):
Q: <question 1 text>
A: <answer 1 text>
Q: <question 2 text>
A: <answer 2 text>
... and so on for all questions."""

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an educational assistant that creates practice test questions from study materials. Always respond with valid JSON only."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract the content from the response
            if 'choices' not in result or len(result['choices']) == 0:
                return self._fallback_question_generation(flashcards, num_questions)
            
            content = result['choices'][0]['message']['content'].strip()
            
            # Parse Q/A pairs from the content instead of strict JSON
            questions: List[Dict[str, str]] = []
            current_question: str = ""
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith("Q:"):
                    # Start a new question
                    current_question = line[2:].strip()
                elif line.startswith("A:") and current_question:
                    answer_text = line[2:].strip()
                    questions.append({
                        "question": current_question,
                        "correct_answer": answer_text
                    })
                    current_question = ""

            if not questions:
                # If we couldn't parse anything useful, fall back
                return self._fallback_question_generation(flashcards, num_questions)

            return questions[:num_questions]
                
        except (requests.RequestException, json.JSONDecodeError, KeyError):
            # On any API or parsing issue, fall back gracefully
            return self._fallback_question_generation(flashcards, num_questions)
    
    def _fallback_question_generation(self, flashcards: List[Flashcard], num_questions: int) -> List[Dict[str, str]]:
        """Fallback: generate simple questions from flashcard content."""
        return [
            {
                "question": f"What is the answer to: {flashcards[i % len(flashcards)].front}?",
                "correct_answer": flashcards[i % len(flashcards)].back
            }
            for i in range(min(num_questions, len(flashcards)))
        ]

