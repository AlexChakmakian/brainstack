"""
BrainStack - Practice Test Class
Represents an AI-generated practice test derived from a deck of flashcards.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from practice_test_question import PracticeTestQuestion


class PracticeTest:
    """
    Represents an AI-generated practice test.
    
    A PracticeTest is derived from a Deck (association relationship).
    A User can have many PracticeTests (composition relationship).
    """
    
    def __init__(self, deck_id: str, deck_name: str, test_id: Optional[str] = None,
                 questions: Optional[List[PracticeTestQuestion]] = None):
        """
        Initialize a practice test.
        
        Args:
            deck_id: ID of the deck this test is derived from
            deck_name: Name of the deck (for reference)
            test_id: Unique identifier (auto-generated if None)
            questions: List of questions in the test
        """
        self.id = test_id or self._generate_id()
        self.deck_id = deck_id
        self.deck_name = deck_name
        self.created_at = datetime.now().isoformat()
        self.completed_at: Optional[str] = None
        self.questions: List[PracticeTestQuestion] = questions or []
        self.is_completed = False
        self.score: Optional[float] = None  # Percentage score
    
    def _generate_id(self) -> str:
        """Generate a unique ID for the test."""
        return str(uuid.uuid4())
    
    def add_question(self, question: str, correct_answer: str) -> PracticeTestQuestion:
        """Add a question to the test."""
        q = PracticeTestQuestion(question=question, correct_answer=correct_answer)
        self.questions.append(q)
        return q
    
    def get_question(self, question_id: str) -> Optional[PracticeTestQuestion]:
        """Get a question by ID."""
        return next((q for q in self.questions if q.id == question_id), None)
    
    def submit_answer(self, question_id: str, user_answer: str) -> bool:
        """
        Submit an answer for a question.
        
        Args:
            question_id: ID of the question
            user_answer: User's answer
            
        Returns:
            True if correct, False otherwise
        """
        question = self.get_question(question_id)
        if question:
            return question.submit_answer(user_answer)
        return False
    
    def complete_test(self):
        """Mark the test as completed and calculate score."""
        if self.is_completed:
            return
        
        self.is_completed = True
        self.completed_at = datetime.now().isoformat()
        self.score = self.get_score()
    
    def get_score(self) -> float:
        """Get the test score as a percentage."""
        if self.score is not None:
            return self.score
        
        # Calculate if not completed
        total_questions = len(self.questions)
        if total_questions == 0:
            return 0.0
        
        correct_count = sum(1 for q in self.questions if q.is_correct is True)
        return (correct_count / total_questions) * 100
    
    def get_progress(self) -> Dict[str, Any]:
        """Get progress information about the test."""
        total = len(self.questions)
        answered = sum(1 for q in self.questions if q.user_answer is not None)
        correct = sum(1 for q in self.questions if q.is_correct is True)
        incorrect = sum(1 for q in self.questions if q.is_correct is False)
        
        return {
            'total_questions': total,
            'answered': answered,
            'correct': correct,
            'incorrect': incorrect,
            'unanswered': total - answered,
            'score': self.get_score()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert practice test to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'deck_id': self.deck_id,
            'deck_name': self.deck_name,
            'created_at': self.created_at,
            'completed_at': self.completed_at,
            'is_completed': self.is_completed,
            'score': self.score,
            'questions': [q.to_dict() for q in self.questions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PracticeTest':
        """Create practice test from dictionary."""
        test = cls(
            deck_id=data['deck_id'],
            deck_name=data.get('deck_name', ''),
            test_id=data['id']
        )
        test.created_at = data.get('created_at', datetime.now().isoformat())
        test.completed_at = data.get('completed_at')
        test.is_completed = data.get('is_completed', False)
        test.score = data.get('score')
        test.questions = [
            PracticeTestQuestion.from_dict(q_data) 
            for q_data in data.get('questions', [])
        ]
        return test

