from __future__ import annotations
from typing import Dict, Any
from datetime import datetime

from storage.base import StorageBase

DEFAULT_SEASON_DATA: Dict[str, Any] = {
    "current_season": 1,
    "seasons": {
        "1": {
            "name": "Season 1",
            "start_date": None,
            "end_date": None,
            "total_submissions": 0,
            "stages": {
                "1": {
                    "name": "Stage 1",
                    "solution": "",
                    "submissions": [],
                    "completed": False
                }
            },
            "current_stage": 1
        }
    }
}

class SeasonManager:
    def __init__(self, storage: StorageBase):
        self._storage = storage
        self._data = self._storage.load_season_data(default_payload=DEFAULT_SEASON_DATA)

    @property
    def data(self) -> Dict[str, Any]:
        return self._data

    def save(self) -> None:
        self._storage.save_season_data(self._data)

    def get_current_season(self) -> Dict[str, Any]:
        season_id = str(self._data["current_season"])
        return self._data["seasons"].get(season_id, {})

    def get_current_stage(self) -> Dict[str, Any]:
        season = self.get_current_season()
        stage_id = str(season.get("current_stage", 1))
        return season.get("stages", {}).get(stage_id, {})

    def advance_season(self) -> str:
        """Advance to the next season."""
        current = self._data["current_season"]
        next_season = current + 1
        self._data["current_season"] = next_season

        # Create new season if it doesn't exist
        if str(next_season) not in self._data["seasons"]:
            self._data["seasons"][str(next_season)] = {
                "name": f"Season {next_season}",
                "start_date": datetime.now().isoformat(),
                "end_date": None,
                "total_submissions": 0,
                "stages": {
                    "1": {
                        "name": "Stage 1",
                        "solution": "",
                        "submissions": [],
                        "completed": False
                    }
                },
                "current_stage": 1
            }
        self.save()
        return f"Advanced to Season {next_season}"

    def advance_stage(self) -> str:
        """Advance to the next stage in current season."""
        season = self.get_current_season()
        current_stage = season["current_stage"]
        next_stage = current_stage + 1

        # Create new stage
        if str(next_stage) not in season["stages"]:
            season["stages"][str(next_stage)] = {
                "name": f"Stage {next_stage}",
                "solution": "",
                "submissions": [],
                "completed": False
            }

        season["current_stage"] = next_stage
        self.save()
        return f"Advanced to Stage {next_stage}"

    def set_stage_solution(self, solution: str) -> str:
        """Set the solution for the current stage."""
        stage = self.get_current_stage()
        stage["solution"] = solution.lower().strip()
        self.save()
        return f"Set solution for {stage['name']}"

    def submit_answer(self, user_id: str, answer: str) -> tuple[str, bool]:
        """Submit an answer for the current stage.
        
        Returns: (message, was_correct)
        """
        stage = self.get_current_stage()
        answer = answer.lower().strip()
        solution = stage.get("solution", "")

        if stage.get("completed", False):
            return "This stage has already been solved! Wait for the next stage.", False

        if not solution:
            return "No solution has been set yet. Please wait for the moderators.", False

        submission = {
            "user_id": user_id,
            "answer": answer,
            "timestamp": datetime.now().isoformat(),
            "correct": answer == solution
        }

        submissions = stage.get("submissions", [])
        submissions.append(submission)
        stage["submissions"] = submissions

        season = self.get_current_season()
        season["total_submissions"] = season.get("total_submissions", 0) + 1

        was_correct = answer == solution
        if was_correct:
            stage["completed"] = True

        self.save()

        if was_correct:
            return "🎉 Correct! Well done. You've solved the stage!", True
        else:
            return "❌ Incorrect. Try again!", False

    def get_season_stats(self) -> Dict[str, Any]:
        """Get stats for current season."""
        season = self.get_current_season()
        stages = season.get("stages", {})

        return {
            "season_name": season.get("name", "Unknown"),
            "total_submissions": season.get("total_submissions", 0),
            "current_stage": season.get("current_stage", 1),
            "total_stages": len(stages)
        }

    def get_stage_stats(self) -> Dict[str, Any]:
        """Get detailed stats for current stage."""
        stage = self.get_current_stage()
        submissions = stage.get("submissions", [])
        correct_count = sum(1 for s in submissions if s.get("correct", False))

        return {
            "stage_name": stage.get("name", "Unknown"),
            "total_submissions": len(submissions),
            "correct_submissions": correct_count,
            "has_solution": bool(stage.get("solution")),
            "completed": stage.get("completed", False)
        }