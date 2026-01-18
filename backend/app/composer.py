from __future__ import annotations

import uuid
from typing import Any, Dict, List

from .skillmap_loader import load_skillmap
from .generators.core import generate_by_skill


def compose_sea_paper(mode: str = "full") -> Dict[str, Any]:
    """
    Compose a SEA-style maths paper using the Trinidad & Tobago primary skill map.
    Returns pure JSON-safe dicts (no classes).
    """

    skillmap = load_skillmap()

    paper_id = f"sea_{uuid.uuid4().hex[:10]}"
    questions: List[Dict[str, Any]] = []

    sections = skillmap.get("sections", [])

    for section in sections:
        section_name = section.get("name", "Section")
        difficulty = section.get("difficulty", 3)

        for qdef in section.get("questions", []):
            skill_id = qdef["skill_id"]
            marks = qdef.get("marks", 1)

            question = generate_by_skill(
                skill_id=skill_id,
                section=section_name,
                marks=marks,
                difficulty=difficulty,
            )

            # question is already a dict
            questions.append(question)

    return {
        "paper_id": paper_id,
        "mode": mode,
        "total_questions": len(questions),
        "questions": questions,
    }
