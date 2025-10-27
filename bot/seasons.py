from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
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
                    "solvers": []  # Track which houses solved it
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
                        "points": 10,
                        "submissions": [],
                        "solvers": []
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
                "points": 10,
                "submissions": [],
                "solvers": []
            }

        season["current_stage"] = next_stage
        self.save()
        return f"Advanced to Stage {next_stage}"

    def set_stage_solution(self, solution: str, points: int = 10) -> str:
        """Set the solution and points for the current stage."""
        stage = self.get_current_stage()
        stage["solution"] = solution.lower().strip()
        stage["points"] = points
        self.save()
        return f"Set solution for {stage['name']} (worth {points} points)"

    def submit_answer(
        self, 
        user_id: str, 
        house_key: str, 
        answer: str
    ) -> Tuple[str, bool, int, Optional[str]]:
        """Submit an answer for the current stage.
        
        Args:
            user_id: The Discord user ID submitting
            house_key: The house key ("house_veridian" or "feathered_host")
            answer: The answer being submitted
        
        Returns: (message, was_correct, points_awarded, house_display_name)
        """
        stage = self.get_current_stage()
        answer = answer.lower().strip()
        solution = stage.get("solution", "")

        if not solution:
            return "No solution has been set yet. Please wait for the moderators.", False, 0, None

        # Check if this house has already solved this stage
        solvers = stage.get("solvers", [])
        houses_solved = [s["house_key"] for s in solvers]
        
        if house_key in houses_solved:
            house_display = "House Veridian" if house_key == "house_veridian" else "Feathered Host"
            return f"{house_display} has already solved this stage!", False, 0, None

        # Record the submission
        submission = {
            "user_id": user_id,
            "house_key": house_key,
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
        points_awarded = 0
        house_display = "House Veridian" if house_key == "house_veridian" else "Feathered Host"

        if was_correct:
            # Calculate points based on house solving order
            base_points = stage.get("points", 10)
            solve_position = len(solvers)  # 0 = first house, 1 = second house
            
            # Point system for 2 houses
            if solve_position == 0:
                # First house gets full points
                points_awarded = base_points
            else:
                # Second house gets 50% of points
                points_awarded = int(base_points * 0.5)
            
            # Track this solver
            solver_entry = {
                "user_id": user_id,
                "house_key": house_key,
                "timestamp": datetime.now().isoformat(),
                "points_awarded": points_awarded,
                "solve_position": solve_position + 1  # 1-indexed for display
            }
            solvers.append(solver_entry)
            stage["solvers"] = solvers

        self.save()

        if was_correct:
            solve_position = len(solvers)
            if solve_position == 1:
                return f"🎉 Correct! {house_display} is the first to solve this stage!", True, points_awarded, house_display
            else:
                return f"✅ Correct! {house_display} solved it!", True, points_awarded, house_display
        else:
            return "❌ Incorrect. Try again!", False, 0, None

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
        solvers = stage.get("solvers", [])
        correct_count = sum(1 for s in submissions if s.get("correct", False))

        return {
            "stage_name": stage.get("name", "Unknown"),
            "total_submissions": len(submissions),
            "correct_submissions": correct_count,
            "unique_solvers": len(solvers),
            "has_solution": bool(stage.get("solution")),
            "completed": len(solvers) >= 2,  # Both houses solved
            "points": stage.get("points", 10)
        }

    def get_stage_leaderboard(self) -> list[Dict[str, Any]]:
        """Get the leaderboard for the current stage."""
        stage = self.get_current_stage()
        solvers = stage.get("solvers", [])
        return solvers

    def get_house_standings(self) -> Dict[str, int]:
        """Get total points for each house across all stages in current season."""
        season = self.get_current_season()
        stages = season.get("stages", {})
        
        house_points = {
            "house_veridian": 0,
            "feathered_host": 0
        }
        
        for stage_data in stages.values():
            solvers = stage_data.get("solvers", [])
            for solver in solvers:
                house_key = solver.get("house_key", "")
                points = solver.get("points_awarded", 0)
                if house_key in house_points:
                    house_points[house_key] += points
        
        return house_points
