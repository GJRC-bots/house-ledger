from __future__ import annotations
from typing import Dict, Tuple

import discord

def get_house_member_counts(*, guild: discord.Guild, house_role_ids: Dict[str, str]) -> Tuple[int, int]:
    vr_id = (house_role_ids.get("house_veridian") or "").strip()
    fh_id = (house_role_ids.get("feathered_host") or "").strip()
    veridian = feathered = 0
    if vr_id and vr_id.isdigit():
        role = guild.get_role(int(vr_id))
        if role:
            veridian = len(role.members)
    if fh_id and fh_id.isdigit():
        role = guild.get_role(int(fh_id))
        if role:
            feathered = len(role.members)
    return veridian, feathered

def compute_multiplier(*, house_key: str, veridian_count: int, feathered_count: int) -> float:
    largest = max(veridian_count, feathered_count, 1)
    if house_key == "house_veridian":
        this_count = max(veridian_count, 1)
    else:
        this_count = max(feathered_count, 1)
    return largest / this_count
