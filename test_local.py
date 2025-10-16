from bot.config import ConfigManager
from bot.scoring import ScoreManager
from storage.json_storage import JsonStorage
from types import SimpleNamespace

mock_guild = SimpleNamespace()
mock_guild.get_role = lambda role_id: SimpleNamespace(members=[1, 2, 3])

storage = JsonStorage(
    config_path="houseledger_config.json",
    scores_path="houseledger_scores.json"
)
config_mgr = ConfigManager(storage=storage)
score_mgr = ScoreManager(storage=storage, config_mgr=config_mgr)
config_mgr.set_weighting(True, "round")

async def simulate():
    print("Before:", score_mgr.data)

    await score_mgr.add_points(
        guild=mock_guild,
        actor_id=999,
        target="house",
        target_id="house_veridian",
        base_points=10,
        reason="offline test",
        weighted=True
    )

    print("After:", score_mgr.data)

import asyncio
asyncio.run(simulate())
