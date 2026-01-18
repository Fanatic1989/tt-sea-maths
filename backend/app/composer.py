from __future__ import annotations

import random
import uuid
from typing import Any, Dict, List

from .skillmap_loader import load_skillmap
from .generators.core import generate_by_skill


# SEA MVP skill pool (expand later)
SEA_SKILL_POOL = [
    "std5_add_sub_unlike_denoms",
]


def compose_sea_paper(mode: str = "full") -> Dict[str, Any]:
    """
    Build a SEA-style paper based on sea_simulator.sections in the JSON.
    Generates Section I/II/III counts & marks.
    """

    skillmap = load_skillmap()
    sea = skillmap.get("sea_simulator", {})
    sea_sections = sea.get("sections", [])

    paper_id = f"sea_{uuid.uuid4().hex[:10]}"
    questions: List[Dict[str, Any]] = []

    # difficulty curve: I easiest, II medium, III hardest
    difficulty_by_name = {"I": 2, "II": 3, "III": 4}

    for sec in sea_sections:
        sec_name = sec.get("name", "I")
        count = int(sec.get("count", 0))
        marks_each = int(sec.get("marks_each", 1))
        difficulty = difficulty_by_name.get(sec_name, 3)

        for _ in range(count):
            skill_id = random.choice(SEA_SKILL_POOL)
            q = generate_by_skill(
                skill_id=skill_id,
                section=f"Section {sec_name}",
                marks=marks_each,
                difficulty=difficulty,
            )
            questions.append(q)

    return {
        "paper_id": paper_id,
        "mode": mode,
        "total_questions": len(questions),
        "duration_sec": int(sea.get("duration_sec", 4500)),
        "questions": questions,
    }
