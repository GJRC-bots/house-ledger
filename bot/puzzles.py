from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
import json
from datetime import datetime, timedelta

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
    
    def activate_timed_puzzle(
        self,
        puzzle_id: str,
        base_points: int,
        veridian_minutes: int,
        feathered_minutes: int,
        veridian_msg_id: Optional[str] = None,
        feathered_msg_id: Optional[str] = None
    ) -> bool:
        """Activate a puzzle with time limits per house"""
        puzzle = self.get_puzzle_by_id(puzzle_id)
        if not puzzle:
            return False
        
        start_time = datetime.now()
        
        puzzle["timed"] = True
        puzzle["active"] = True
        puzzle["timed_config"] = {
            "base_points": base_points,
            "house_veridian": {
                "duration_minutes": veridian_minutes,
                "start_time": start_time.isoformat(),
                "end_time": (start_time + timedelta(minutes=veridian_minutes)).isoformat(),
                "solved": False,
                "solver_id": None,
                "points_awarded": None,
                "message_id": veridian_msg_id
            },
            "feathered_host": {
                "duration_minutes": feathered_minutes,
                "start_time": start_time.isoformat(),
                "end_time": (start_time + timedelta(minutes=feathered_minutes)).isoformat(),
                "solved": False,
                "solver_id": None,
                "points_awarded": None,
                "message_id": feathered_msg_id
            }
        }
        
        self._save_puzzles()
        return True
    
    def update_timed_message_ids(self, puzzle_id: str, veridian_msg_id: str, feathered_msg_id: str) -> bool:
        """Update message IDs for timed puzzle embeds"""
        puzzle = self.get_puzzle_by_id(puzzle_id)
        if puzzle and puzzle.get("timed"):
            config = puzzle.get("timed_config", {})
            if "house_veridian" in config:
                config["house_veridian"]["message_id"] = veridian_msg_id
            if "feathered_host" in config:
                config["feathered_host"]["message_id"] = feathered_msg_id
            self._save_puzzles()
            return True
        return False
    
    def get_timed_points(self, puzzle_id: str, house_key: str) -> int:
        """Calculate points based on time remaining for a house"""
        puzzle = self.get_puzzle_by_id(puzzle_id)
        if not puzzle or not puzzle.get("timed"):
            return puzzle.get("points", 0) if puzzle else 0
        
        config = puzzle.get("timed_config", {})
        house_config = config.get(house_key, {})
        
        if house_config.get("solved"):
            return house_config.get("points_awarded", 0)
        
        base_points = config.get("base_points", 0)
        duration_minutes = house_config.get("duration_minutes", 60)
        start_time = datetime.fromisoformat(house_config.get("start_time"))
        
        now = datetime.now()
        elapsed = (now - start_time).total_seconds() / 60  # minutes elapsed
        time_remaining = max(0, duration_minutes - elapsed)
        
        if time_remaining <= 0:
            return 0
        
        # Points = base_points × (time_remaining / total_time)
        points = int(base_points * (time_remaining / duration_minutes))
        return max(1, points)  # At least 1 point if time remains
    
    def is_puzzle_expired_for_house(self, puzzle_id: str, house_key: str) -> bool:
        """Check if puzzle has expired for a specific house"""
        puzzle = self.get_puzzle_by_id(puzzle_id)
        if not puzzle or not puzzle.get("timed"):
            return False
        
        config = puzzle.get("timed_config", {})
        house_config = config.get(house_key, {})
        
        if house_config.get("solved"):
            return True  # Solved = expired for this house
        
        end_time = datetime.fromisoformat(house_config.get("end_time"))
        return datetime.now() >= end_time
    
    def mark_timed_solved(self, puzzle_id: str, user_id: str, house_key: str) -> Tuple[bool, int]:
        """Mark a timed puzzle as solved for a specific house. Returns (success, points_awarded)"""
        puzzle = self.get_puzzle_by_id(puzzle_id)
        if not puzzle or not puzzle.get("timed"):
            return False, 0
        
        config = puzzle.get("timed_config", {})
        house_config = config.get(house_key, {})
        
        if house_config.get("solved") or self.is_puzzle_expired_for_house(puzzle_id, house_key):
            return False, 0
        
        points = self.get_timed_points(puzzle_id, house_key)
        
        house_config["solved"] = True
        house_config["solver_id"] = user_id
        house_config["points_awarded"] = points
        
        # Check if both houses are done (solved or expired)
        both_done = all(
            config[hk].get("solved") or self.is_puzzle_expired_for_house(puzzle_id, hk)
            for hk in ["house_veridian", "feathered_host"]
        )
        
        if both_done:
            puzzle["active"] = False
        
        self._save_puzzles()
        return True, points
    
    def check_and_expire_timed_puzzles(self) -> List[Tuple[str, str]]:
        """Check all timed puzzles and expire houses that ran out of time.
        Returns list of (puzzle_id, house_key) that expired."""
        expired = []
        
        for puzzle in self.get_active_puzzles():
            if not puzzle.get("timed"):
                continue
            
            config = puzzle.get("timed_config", {})
            puzzle_id = puzzle["id"]
            
            for house_key in ["house_veridian", "feathered_host"]:
                house_config = config.get(house_key, {})
                
                if house_config.get("solved"):
                    continue
                
                if self.is_puzzle_expired_for_house(puzzle_id, house_key):
                    house_config["solved"] = True  # Mark as done (0 points)
                    house_config["points_awarded"] = 0
                    expired.append((puzzle_id, house_key))
            
            # Check if both houses are done
            both_done = all(
                config[hk].get("solved")
                for hk in ["house_veridian", "feathered_host"]
            )
            
            if both_done:
                puzzle["active"] = False
        
        if expired:
            self._save_puzzles()
        
        return expired
    
    def get_time_remaining_str(self, puzzle_id: str, house_key: str) -> str:
        """Get formatted time remaining string for a house"""
        puzzle = self.get_puzzle_by_id(puzzle_id)
        if not puzzle or not puzzle.get("timed"):
            return "N/A"
        
        config = puzzle.get("timed_config", {})
        house_config = config.get(house_key, {})
        
        if house_config.get("solved"):
            return "✅ Solved"
        
        end_time = datetime.fromisoformat(house_config.get("end_time"))
        now = datetime.now()
        
        if now >= end_time:
            return "⏰ Time's Up"
        
        remaining = end_time - now
        total_seconds = int(remaining.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"⏰ {hours}h {minutes}m remaining"
        else:
            return f"⏰ {minutes}m remaining"
