from __future__ import annotations

import random
from typing import Any, Dict, List

from .skillmap_loader import load_skillmap
from .generators.core import generate_by_skill


DEFAULT_SKILL_POOL = {
    "I": [
        "core_add_sub",
        "std4_simplify_fractions",
        "std5_percent_of_quantity",
    ],
    "II": [
        "std5_add_sub_unlike_denoms",
        "std4_simplify_fractions",
        "std5_percent_of_quantity",
        "std5_elapsed_time_harder",
    ],
    "III": [
        "std5_add_sub_unlike_denoms",
        "std5_percent_of_quantity",
        "std5_elapsed_time_harder",
    ],
}


def _pick_difficulty(section: str) -> int:
    if section == "I":
        return random.choices([1, 2], [0.6, 0.4])[0]
    if section == "II":
        return random.choices([1, 2, 3], [0.25, 0.55, 0.2])[0]
    return random.choices([2, 3], [0.4, 0.6])[0]


def compose_sea_paper(mode: str = "full") -> Dict[str, Any]:
    skillmap = load_skillmap()
    sections = skillmap.get("sea_simulator", {}).get("sections", [])

    paper_id = f"paper_{random.randint(100000,999999)}"
    paper_questions: List[Dict[str, Any]] = []

    for sec in sections:
        sec_name = sec.get("name")
        count = int(sec.get("count"))
        marks = int(sec.get("marks_each", 1))
        pool = DEFAULT_SKILL_POOL.get(sec_name, ["core_add_sub"])

        for _ in range(count):
            skill_id = random.choice(pool)
            difficulty = _pick_difficulty(sec_name)
            q = generate_by_skill(skill_id, section=sec_name, marks=marks, difficulty=difficulty)
            paper_questions.append(q.to_dict())

    return {
        "paper_id": paper_id,
        "duration_sec": int(skillmap.get("sea_simulator", {}).get("duration_sec", 4500)),
        "questions": paper_questions,
    }
