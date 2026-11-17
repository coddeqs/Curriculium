import json
import os
from typing import Dict, Any, List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
MASTER_PROFILE_PATH = os.path.join(DATA_DIR, "master_profile.json")

def load_master_profile() -> Dict[str, Any]:
    if not os.path.exists(MASTER_PROFILE_PATH):
        raise FileNotFoundError(f"Master profile not found at {MASTER_PROFILE_PATH}")
    with open(MASTER_PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_master_profile(profile_data: Dict[str, Any]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(MASTER_PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2, ensure_ascii=False)

def get_all_skills_flat(profile: Dict[str, Any] = None) -> List[str]:
    if profile is None:
        profile = load_master_profile()
    flat = []
    for category, skill_list in profile.get("skills", {}).items():
        flat.extend(skill_list)
    return flat
