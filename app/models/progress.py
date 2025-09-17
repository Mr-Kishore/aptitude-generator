"""
User progress tracking model.

This module handles tracking user progress across different aptitude categories.
"""
from datetime import datetime
from typing import Dict, List, Optional
import json
import os


class CategoryProgress:
    """Represents progress for a single aptitude category."""
    
    def __init__(self, category_slug: str, questions_attempted: int = 0, 
                 questions_correct: int = 0, last_attempted: Optional[datetime] = None):
        self.category_slug = category_slug
        self.questions_attempted = questions_attempted
        self.questions_correct = questions_correct
        self.last_attempted = last_attempted or datetime.now()
    
    @property
    def accuracy_percentage(self) -> float:
        """Calculate accuracy percentage."""
        if self.questions_attempted == 0:
            return 0.0
        return (self.questions_correct / self.questions_attempted) * 100
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage based on questions attempted vs total available."""
        # For now, assume each category has 20 questions
        # TODO: Make this dynamic based on actual question count
        total_questions = 20
        if total_questions == 0:
            return 0.0
        return min((self.questions_attempted / total_questions) * 100, 100.0)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'category_slug': self.category_slug,
            'questions_attempted': self.questions_attempted,
            'questions_correct': self.questions_correct,
            'last_attempted': self.last_attempted.isoformat() if self.last_attempted else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CategoryProgress':
        """Create from dictionary."""
        last_attempted = None
        if data.get('last_attempted'):
            last_attempted = datetime.fromisoformat(data['last_attempted'])
        
        return cls(
            category_slug=data['category_slug'],
            questions_attempted=data.get('questions_attempted', 0),
            questions_correct=data.get('questions_correct', 0),
            last_attempted=last_attempted
        )


class UserProgress:
    """Manages progress for a single user across all categories."""
    
    def __init__(self, username: str):
        self.username = username
        self.categories: Dict[str, CategoryProgress] = {}
        self.activities: List[Dict] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def get_category_progress(self, category_slug: str) -> CategoryProgress:
        """Get progress for a specific category, creating if it doesn't exist."""
        if category_slug not in self.categories:
            self.categories[category_slug] = CategoryProgress(category_slug)
        return self.categories[category_slug]
    
    def update_category_progress(self, category_slug: str, questions_attempted: int, 
                               questions_correct: int):
        """Update progress for a specific category."""
        progress = self.get_category_progress(category_slug)
        progress.questions_attempted = questions_attempted
        progress.questions_correct = questions_correct
        progress.last_attempted = datetime.now()
        self.updated_at = datetime.now()
        
        # Add activity
        accuracy = (questions_correct / questions_attempted * 100) if questions_attempted > 0 else 0
        activity = {
            'type': 'quiz_completed',
            'category_slug': category_slug,
            'score': f"{questions_correct}/{questions_attempted} ({accuracy:.1f}%)",
            'timestamp': datetime.now().isoformat()
        }
        self.activities.append(activity)
        
        # Keep only last 10 activities
        if len(self.activities) > 10:
            self.activities = self.activities[-10:]
    
    def get_overall_progress(self) -> Dict:
        """Get overall progress statistics."""
        total_attempted = sum(cat.questions_attempted for cat in self.categories.values())
        total_correct = sum(cat.questions_correct for cat in self.categories.values())
        total_categories = len(self.categories)
        categories_with_progress = len([cat for cat in self.categories.values() 
                                      if cat.questions_attempted > 0])
        
        overall_accuracy = 0.0
        if total_attempted > 0:
            overall_accuracy = (total_correct / total_attempted) * 100
        
        return {
            'total_questions_attempted': total_attempted,
            'total_questions_correct': total_correct,
            'overall_accuracy': overall_accuracy,
            'categories_started': categories_with_progress,
            'total_categories': total_categories
        }
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'username': self.username,
            'categories': {slug: progress.to_dict() for slug, progress in self.categories.items()},
            'activities': self.activities,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'UserProgress':
        """Create from dictionary."""
        progress = cls(data['username'])
        progress.created_at = datetime.fromisoformat(data['created_at'])
        progress.updated_at = datetime.fromisoformat(data['updated_at'])
        progress.activities = data.get('activities', [])
        
        for slug, cat_data in data.get('categories', {}).items():
            progress.categories[slug] = CategoryProgress.from_dict(cat_data)
        
        return progress


class ProgressStore:
    """Manages user progress data storage."""
    
    def __init__(self, data_dir: str = "instance"):
        self.data_dir = data_dir
        self.progress_file = os.path.join(data_dir, "user_progress.json")
        self._progress_data: Dict[str, UserProgress] = {}
        self._load_data()
    
    def _load_data(self):
        """Load progress data from file."""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for username, progress_data in data.items():
                        self._progress_data[username] = UserProgress.from_dict(progress_data)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Error loading progress data: {e}")
                self._progress_data = {}
    
    def _save_data(self):
        """Save progress data to file."""
        os.makedirs(self.data_dir, exist_ok=True)
        data = {username: progress.to_dict() for username, progress in self._progress_data.items()}
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def get_user_progress(self, username: str) -> UserProgress:
        """Get progress for a user, creating if it doesn't exist."""
        if username not in self._progress_data:
            self._progress_data[username] = UserProgress(username)
            self._save_data()
        return self._progress_data[username]
    
    def update_user_progress(self, username: str, category_slug: str, 
                           questions_attempted: int, questions_correct: int):
        """Update progress for a user in a specific category."""
        progress = self.get_user_progress(username)
        progress.update_category_progress(category_slug, questions_attempted, questions_correct)
        self._save_data()
    
    def get_all_progress(self) -> Dict[str, UserProgress]:
        """Get all user progress data."""
        return self._progress_data.copy()


# Global progress store instance
progress_store = ProgressStore()
