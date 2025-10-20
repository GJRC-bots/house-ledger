from __future__ import annotations
from typing import Dict, List, Tuple

import discord

def get_house_member_counts(*, guild: discord.Guild, house_role_ids: Dict[str, List[str]]) -> Tuple[int, int]:
    vr_ids = house_role_ids.get("house_veridian", [])
    fh_ids = house_role_ids.get("feathered_host", [])
    
    veridian_members = set()
    for vr_id in vr_ids:
        if vr_id and vr_id.isdigit():
            role = guild.get_role(int(vr_id))
            if role:
                veridian_members.update(m.id for m in role.members)
    
    feathered_members = set()
    for fh_id in fh_ids:
        if fh_id and fh_id.isdigit():
            role = guild.get_role(int(fh_id))
            if role:
                feathered_members.update(m.id for m in role.members)
    
    return len(veridian_members), len(feathered_members)

def compute_multiplier(*, house_key: str, veridian_count: int, feathered_count: int) -> float:
    largest = max(veridian_count, feathered_count, 1)
    if house_key == "house_veridian":
        this_count = max(veridian_count, 1)
    else:
        this_count = max(feathered_count, 1)
    return largest / this_count
