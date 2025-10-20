from __future__ import annotations
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone

import discord

from storage.base import StorageBase
from bot.config import ConfigManager
from utils.weights import get_house_member_counts, compute_multiplier
from utils.helpers import apply_rounding

DEFAULT_SCORES: Dict[str, Any] = {
    "houses": {"house_veridian": 0, "feathered_host": 0},
    "players": {},
    "events": []
}

class ScoreManager:
    def __init__(self, storage: StorageBase, config_mgr: ConfigManager):
        self._storage = storage
        self._config_mgr = config_mgr
        self._scores = self._storage.load_scores(default_payload=DEFAULT_SCORES)

    @property
    def data(self) -> Dict[str, Any]:
        return self._scores

    def save(self) -> None:
        self._storage.save_scores(self._scores)

    def get_house_totals(self) -> Dict[str, int]:
        return dict(self._scores.get("houses", {}))

    def get_player_total(self, user_id: int) -> int:
        return int(self._scores.get("players", {}).get(str(user_id), 0))

    def get_top_players(self, limit: int = 10) -> List[Tuple[str, int]]:
        players = self._scores.get("players", {})
        sorted_players = sorted(players.items(), key=lambda kv: kv[1], reverse=True)
        return sorted_players[:limit]

    async def add_points(
        self,
        *,
        guild: discord.Guild,
        actor_id: int,
        target: str,
        target_id: str,
        base_points: int,
        reason: str,
        weighted: bool
    ) -> Tuple[int, int]:
        """
        Returns (player_points_awarded, house_points_awarded)
        """
        player_pts_awarded = 0
        house_pts_awarded = 0

        if target == "player":
            players = self._scores.setdefault("players", {})
            players.setdefault(target_id, 0)
            players[target_id] += base_points
            player_pts_awarded = base_points

            member = guild.get_member(int(target_id))
            house_key = self._infer_member_house(member)
            if house_key:
                house_pts_awarded = await self._apply_house_points(
                    guild=guild,
                    house_key=house_key,
                    base_points=base_points,
                    weighted=weighted
                )

        elif target == "house":
            house_key = target_id
            house_pts_awarded = await self._apply_house_points(
                guild=guild,
                house_key=house_key,
                base_points=base_points,
                weighted=weighted
            )
        else:
            raise ValueError("target must be 'house' or 'player'")

        self._log_event(
            actor_id=actor_id,
            target=target,
            target_id=target_id,
            base_points=base_points,
            weighted=weighted,
            house_points_awarded=house_pts_awarded,
            player_points_awarded=player_pts_awarded,
            reason=reason
        )

        self.save()
        return player_pts_awarded, house_pts_awarded

    async def remove_points(
        self,
        *,
        guild: discord.Guild,
        actor_id: int,
        target: str,
        target_id: str,
        base_points: int,
        reason: str,
        weighted: bool
    ) -> Tuple[int, int]:
        neg_points = -abs(base_points)
        return await self.add_points(
            guild=guild,
            actor_id=actor_id,
            target=target,
            target_id=target_id,
            base_points=neg_points,
            reason=reason,
            weighted=weighted
        )

    async def _apply_house_points(self, *, guild: discord.Guild, house_key: str, base_points: int, weighted: bool) -> int:
        houses = self._scores.setdefault("houses", {"house_veridian": 0, "feathered_host": 0})
        if house_key not in houses:
            houses[house_key] = 0

        weighted_cfg = self._config_mgr.data.get("weighting", {})
        house_points = base_points

        if weighted and weighted_cfg.get("enabled", False):
            vr_count, fh_count = get_house_member_counts(guild=guild, house_role_ids=self._config_mgr.get_house_role_ids())
            multiplier = compute_multiplier(house_key=house_key, veridian_count=vr_count, feathered_count=fh_count)
            rounding = weighted_cfg.get("rounding", "round")
            house_points = apply_rounding(base_points * multiplier, rounding)

        houses[house_key] += house_points
        return house_points

    def _infer_member_house(self, member: Optional[discord.Member]) -> Optional[str]:
        if not member:
            return None
        role_ids = self._config_mgr.get_house_role_ids()
        vr_ids = role_ids.get("house_veridian", [])
        fh_ids = role_ids.get("feathered_host", [])
        
        for vr_id in vr_ids:
            if vr_id and vr_id.isdigit():
                try:
                    if any(r.id == int(vr_id) for r in member.roles):
                        return "house_veridian"
                except ValueError:
                    continue
        
        for fh_id in fh_ids:
            if fh_id and fh_id.isdigit():
                try:
                    if any(r.id == int(fh_id) for r in member.roles):
                        return "feathered_host"
                except ValueError:
                    continue
        
        return None

    def _log_event(
        self,
        *,
        actor_id: int,
        target: str,
        target_id: str,
        base_points: int,
        weighted: bool,
        house_points_awarded: int,
        player_points_awarded: int,
        reason: str
    ) -> None:
        events = self._scores.setdefault("events", [])
        events.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor_id": str(actor_id),
            "target": target,
            "target_id": str(target_id),
            "base_points": base_points,
            "weighted": weighted,
            "house_points_awarded": house_points_awarded,
            "player_points_awarded": player_points_awarded,
            "reason": reason
        })
