from __future__ import annotations

import random
import uuid
from fractions import Fraction
from typing import Any, Dict, List, Tuple


# ----------------------------
# Core helpers
# ----------------------------

def _qid() -> str:
    return f"q_{uuid.uuid4().hex[:10]}"


def make_question(
    section: str,
    marks: int,
    difficulty: int,
    prompt: str,
    correct_answer: Dict[str, Any],
    hint: str = "",
    example: Dict[str, Any] | None = None,
    steps: List[str] | None = None,
) -> Dict[str, Any]:
    return {
        "question_id": _qid(),
        "section": section,
        "marks": marks,
        "difficulty": difficulty,
        "prompt": prompt,
        "correct_answer": correct_answer,
        "hint": hint,
        "example": example or {},
        "steps": steps or [],
    }


# ----------------------------
# SAFE GENERATORS
# ----------------------------

def gen_add_sub_fractions_unlike(section: str, marks: int, difficulty: int) -> Dict[str, Any]:
    """
    SAFE: Add/subtract fractions with unlike denominators.
    GUARANTEED no ZeroDivisionError.
    """

    denoms = [2, 3, 4, 5, 6, 8, 10, 12]
    if difficulty >= 3:
        denoms += [9, 15]

    for _ in range(100):
        d1 = random.choice(denoms)
        d2 = random.choice(denoms)
        if d1 == d2:
            continue

        n1 = random.randint(1, d1 - 1)
        n2 = random.randint(1, d2 - 1)

        f1 = Fraction(n1, d1)
        f2 = Fraction(n2, d2)

        op = random.choice(["+", "-"])

        if op == "-" and f2 > f1:
            f1, f2 = f2, f1
            n1, d1 = f1.numerator, f1.denominator
            n2, d2 = f2.numerator, f2.denominator

        result = f1 + f2 if op == "+" else f1 - f2
        if result < 0:
            continue

        prompt = f"Calculate: {n1}/{d1} {op} {n2}/{d2}. Give your answer as a simplified fraction."

        return make_question(
            section=section,
            marks=marks,
            difficulty=difficulty,
            prompt=prompt,
            correct_answer={
                "type": "fraction",
                "value": f"{result.numerator}/{result.denominator}",
                "accept_equivalents": True,
            },
            hint="Find a common denominator (LCM) before adding or subtracting.",
            example={
                "prompt": "Example: 1/4 + 1/2",
                "work": ["LCM is 4", "1/2 = 2/4", "1/4 + 2/4 = 3/4"],
                "answer": "3/4",
            },
            steps=[
                "Find the LCM of denominators.",
                "Convert both fractions.",
                "Add or subtract numerators.",
                "Simplify the fraction.",
            ],
        )

    # Absolute fallback (never crashes)
    return make_question(
        section,
        marks,
        difficulty,
        "Calculate: 1/2 + 1/3. Give your answer as a simplified fraction.",
        {
            "type": "fraction",
            "value": "5/6",
            "accept_equivalents": True,
        },
    )


# ----------------------------
# Skill router
# ----------------------------

def generate_by_skill(skill_id: str, section: str, marks: int, difficulty: int) -> Dict[str, Any]:
    """
    Maps skill_id (from JSON skillmap) → generator
    """

    if skill_id == "std5_add_sub_unlike_denoms":
        return gen_add_sub_fractions_unlike(section, marks, difficulty)

    # SAFE fallback
    return make_question(
        section,
        marks,
        difficulty,
        "Calculate: 12 + 8",
        {"type": "numeric", "value": "20", "accept_equivalents": True},
        hint="Add the numbers carefully.",
    )
