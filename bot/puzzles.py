from __future__ import annotations
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

class PuzzleManager:
    def __init__(self, puzzle_file: str = "puzzles.json"):
        self.puzzle_file = puzzle_file
        self._puzzles = self._load_puzzles()
    
    def _load_puzzles(self) -> Dict[str, Any]:
        """Load puzzles from JSON file"""
        try:
            with open(self.puzzle_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"puzzles": []}
    
    def _save_puzzles(self) -> None:
        """Save puzzles to JSON file"""
        with open(self.puzzle_file, 'w', encoding='utf-8') as f:
            json.dump(self._puzzles, f, indent=2, ensure_ascii=False)
    
    def get_all_puzzles(self) -> List[Dict[str, Any]]:
        """Get all puzzles"""
        return self._puzzles.get("puzzles", [])
    
    def get_puzzle_by_id(self, puzzle_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific puzzle by ID"""
        for puzzle in self._puzzles.get("puzzles", []):
            if puzzle.get("id") == puzzle_id:
                return puzzle
        return None
    
    def get_active_puzzles(self) -> List[Dict[str, Any]]:
        """Get all active puzzles"""
        return [p for p in self._puzzles.get("puzzles", []) if p.get("active", False)]
    
    def activate_puzzle(self, puzzle_id: str) -> bool:
        """Activate a puzzle"""
        puzzle = self.get_puzzle_by_id(puzzle_id)
        if puzzle:
            puzzle["active"] = True
            puzzle["solved_by"] = None
            self._save_puzzles()
            return True
        return False
    
    def deactivate_puzzle(self, puzzle_id: str) -> bool:
        """Deactivate a puzzle"""
        puzzle = self.get_puzzle_by_id(puzzle_id)
        if puzzle:
            puzzle["active"] = False
            self._save_puzzles()
            return True
        return False
    
    def mark_solved(self, puzzle_id: str, user_id: str, house: str) -> bool:
        """Mark a puzzle as solved"""
        puzzle = self.get_puzzle_by_id(puzzle_id)
        if puzzle:
            puzzle["solved_by"] = {
                "user_id": user_id,
                "house": house,
                "timestamp": datetime.now().isoformat()
            }
            puzzle["active"] = False
            self._save_puzzles()
            return True
        return False
    
    def check_solution(self, puzzle_id: str, answer: str) -> bool:
        """Check if an answer is correct"""
        puzzle = self.get_puzzle_by_id(puzzle_id)
        if puzzle:
            solution = puzzle.get("solution", "").lower().strip()
            return answer.lower().strip() == solution
        return False
    
    def get_puzzle_for_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get active puzzle for a specific channel"""
        channel_id = str(channel_id)
        for puzzle in self.get_active_puzzles():
            if (puzzle.get("house_veridian_channel") == channel_id or 
                puzzle.get("feathered_host_channel") == channel_id):
                return puzzle
        return None
    
    def set_puzzle_channels(self, puzzle_id: str, veridian_channel: str, feathered_channel: str) -> bool:
        """Set the channels for a puzzle"""
        puzzle = self.get_puzzle_by_id(puzzle_id)
        if puzzle:
            puzzle["house_veridian_channel"] = veridian_channel
            puzzle["feathered_host_channel"] = feathered_channel
            self._save_puzzles()
            return True
        return False
