from __future__ import annotations

import random
import uuid
from typing import Any, Dict, List

from .skillmap_loader import load_skillmap
from .generators.core import generate_by_skill


def compose_sea_paper(mode: str = "full") -> Dict[str, Any]:
    """
    Compose an SEA-style paper using the new MOE-aligned structure in tt_primary_skillmap.json.

    Uses:
      - duration_sec
      - paper.sections (I/II/III)
      - paper.strand_items (Number/Measurement/Geometry/Statistics item counts)
      - skill_bank mapping (strand -> list of skills)
    """

    sm = load_skillmap()

    duration_sec = int(sm.get("duration_sec", 4500))
    paper_cfg = sm.get("paper", {}) or {}

    sections_cfg = paper_cfg.get("sections", []) or []
    strand_items = paper_cfg.get("strand_items", {}) or {}
    skill_bank = sm.get("skill_bank", {}) or {}

    # Defensive defaults if JSON missing something
    if not sections_cfg:
        sections_cfg = [
            {"name": "I", "count": 20, "marks_each": 1},
            {"name": "II", "count": 16, "marks_each": [2, 3]},
            {"name": "III", "count": 4, "marks_each": 4},
        ]

    if not strand_items:
        strand_items = {"Number": 19, "Measurement": 9, "Geometry": 6, "Statistics": 6}

    # Ensure skill bank has at least one skill per strand; if missing, fall back safely
    def strand_skill_pool(strand: str) -> List[str]:
        pool = skill_bank.get(strand, [])
        if isinstance(pool, list) and pool:
            return pool
        # fallback by strand
        if strand == "Number":
            return [
                "std4_add_sub_4digit",
                "std4_mult_2digit_by_1digit",
                "std4_div_exact",
                "std5_add_sub_unlike_denoms",
                "std5_fraction_of_quantity",
                "std5_percent_of_quantity",
            ]
        if strand == "Measurement":
            return ["std4_perimeter_rectangle", "std4_area_rectangle"]
        if strand == "Geometry":
            return ["std5_triangle_angle"]
        if strand == "Statistics":
            return ["stat_read_table_basic", "stat_read_bar_chart_basic"]
        return ["std4_add_sub_4digit"]

    # Build a strand list with exact counts (e.g., Number repeated 19 times, etc.)
    strand_queue: List[str] = []
    for s, n in strand_items.items():
        try:
            strand_queue.extend([s] * int(n))
        except Exception:
            continue

    # If totals aren't exactly 40, normalize to 40 to keep SEA shape
    # (We prefer not to crash; we fill/trim to 40.)
    if len(strand_queue) < 40:
        # fill with Number
        strand_queue.extend(["Number"] * (40 - len(strand_queue)))
    elif len(strand_queue) > 40:
        strand_queue = strand_queue[:40]

    random.shuffle(strand_queue)

    # Difficulty curve by section name
    difficulty_by_section = {"I": 2, "II": 3, "III": 4}

    paper_id = f"sea_{uuid.uuid4().hex[:10]}"
    questions: List[Dict[str, Any]] = []

    strand_idx = 0

    for sec in sections_cfg:
        sec_name = str(sec.get("name", "I"))
        count = int(sec.get("count", 0))

        marks_each = sec.get("marks_each", 1)
        difficulty = difficulty_by_section.get(sec_name, 3)

        for _ in range(count):
            # pick strand from queue (exact distribution overall)
            strand = strand_queue[strand_idx] if strand_idx < len(strand_queue) else "Number"
            strand_idx += 1

            # pick mark value
            if isinstance(marks_each, list) and marks_each:
                marks = int(random.choice(marks_each))
            else:
                marks = int(marks_each)

            # pick skill from that strand pool
            pool = strand_skill_pool(strand)
            skill_id = random.choice(pool)

            q = generate_by_skill(
                skill_id=skill_id,
                section=f"Section {sec_name}",
                marks=marks,
                difficulty=difficulty,
            )

            # attach strand + skill_id so frontend/debug can show it
            q["strand"] = strand
            q["skill_id"] = skill_id

            questions.append(q)

    # Guarantee total_questions reports actual length
    return {
        "paper_id": paper_id,
        "mode": mode,
        "duration_sec": duration_sec,
        "total_questions": len(questions),
        "questions": questions,
    }
