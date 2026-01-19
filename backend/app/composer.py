from __future__ import annotations

import random
import uuid
from typing import Any, Dict, List

from .skillmap_loader import load_skillmap
from .generators.core import generate_by_skill


# SEA skill pool (MVP syllabus coverage)
SEA_SKILL_POOL = [
    # Numbers
    "std4_add_sub_4digit",
    "std4_mult_2digit_by_1digit",
    "std4_div_exact",

    # Fractions & Percent
    "std5_add_sub_unlike_denoms",
    "std5_fraction_of_quantity",
    "std5_percent_of_quantity",

    # Measurement / Geometry
    "std4_perimeter_rectangle",
    "std4_area_rectangle",
    "std5_triangle_angle",
]


def compose_sea_paper(mode: str = "full") -> Dict[str, Any]:
    """
    Build a SEA-style paper based on sea_simulator.sections in tt_primary_skillmap.json.
    Generates Section I/II/III counts & marks and mixes skills from SEA_SKILL_POOL.
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

        # Section weighting: keep Section I slightly more number-based
        # (still random, but nudged)
        if sec_name == "I":
            section_pool = [
                "std4_add_sub_4digit",
                "std4_add_sub_4digit",
                "std4_mult_2digit_by_1digit",
                "std4_div_exact",
                "std5_fraction_of_quantity",
                "std4_perimeter_rectangle",
            ]
        elif sec_name == "II":
            section_pool = [
                "std4_add_sub_4digit",
                "std4_mult_2digit_by_1digit",
                "std4_div_exact",
                "std5_add_sub_unlike_denoms",
                "std5_fraction_of_quantity",
                "std5_percent_of_quantity",
                "std4_area_rectangle",
                "std4_perimeter_rectangle",
            ]
        else:  # III
            section_pool = [
                "std5_add_sub_unlike_denoms",
                "std5_fraction_of_quantity",
                "std5_percent_of_quantity",
                "std4_area_rectangle",
                "std4_perimeter_rectangle",
                "std5_triangle_angle",
                "std4_add_sub_4digit",
                "std4_mult_2digit_by_1digit",
            ]

        # ensure all skills used exist in the global pool (fallback safe)
        # (if you later remove a generator, it won't crash)
        def pick_skill() -> str:
            s = random.choice(section_pool or SEA_SKILL_POOL)
            if s not in SEA_SKILL_POOL:
                return random.choice(SEA_SKILL_POOL)
            return s

        for _ in range(count):
            skill_id = pick_skill()
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

