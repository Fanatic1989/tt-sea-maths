from __future__ import annotations

import random
import uuid
from fractions import Fraction
from typing import Any, Dict, List


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
# Numbers
# ----------------------------

def gen_add_sub_4digit(section: str, marks: int, difficulty: int) -> Dict[str, Any]:
    a = random.randint(1000, 9999)
    b = random.randint(100, 9999)

    if random.random() < 0.5:
        ans = a + b
        return make_question(
            section, marks, difficulty,
            f"Calculate: {a} + {b}",
            {"type": "numeric", "value": str(ans), "accept_equivalents": True},
            hint="Add carefully (carry if needed).",
            steps=["Add ones, tens, hundreds, thousands."],
            example={"prompt": "Example: 2450 + 380", "work": ["2450 + 380 = 2830"], "answer": "2830"},
        )

    if b > a:
        a, b = b, a
    ans = a - b
    return make_question(
        section, marks, difficulty,
        f"Calculate: {a} - {b}",
        {"type": "numeric", "value": str(ans), "accept_equivalents": True},
        hint="Subtract carefully (borrow if needed).",
        steps=["Subtract ones, tens, hundreds, thousands."],
        example={"prompt": "Example: 3000 - 475", "work": ["3000 - 475 = 2525"], "answer": "2525"},
    )


def gen_mult_2digit_by_1digit(section: str, marks: int, difficulty: int) -> Dict[str, Any]:
    a = random.randint(12, 99)
    b = random.randint(2, 9)
    ans = a * b
    return make_question(
        section, marks, difficulty,
        f"Calculate: {a} × {b}",
        {"type": "numeric", "value": str(ans), "accept_equivalents": True},
        hint="Multiply using times tables or long multiplication.",
        steps=["Multiply the ones.", "Multiply the tens.", "Add the results."],
        example={"prompt": "Example: 23 × 4", "work": ["23×4 = 92"], "answer": "92"},
    )


def gen_div_exact(section: str, marks: int, difficulty: int) -> Dict[str, Any]:
    d = random.randint(2, 9)
    q = random.randint(10, 120)
    n = d * q
    return make_question(
        section, marks, difficulty,
        f"Calculate: {n} ÷ {d}",
        {"type": "numeric", "value": str(q), "accept_equivalents": True},
        hint="Division is the reverse of multiplication.",
        steps=["Think: divisor × ? = dividend."],
        example={"prompt": "Example: 84 ÷ 7", "work": ["7×12 = 84"], "answer": "12"},
    )


# ----------------------------
# Fractions
# ----------------------------

def gen_add_sub_fractions_unlike(section: str, marks: int, difficulty: int) -> Dict[str, Any]:
    denoms = [2, 3, 4, 5, 6, 8, 10, 12]
    if difficulty >= 3:
        denoms += [9, 15]

    for _ in range(120):
        d1 = random.choice(denoms)
        d2 = random.choice(denoms)
        if d1 == d2:
            continue

        n1 = random.randint(1, d1 - 1)
        n2 = random.randint(1, d2 - 1)

        f1 = Fraction(n1, d1)
        f2 = Fraction(n2, d2)

        op = random.choice(["+", "-"])

        # ensure non-negative result for subtraction
        if op == "-" and f2 > f1:
            f1, f2 = f2, f1
            n1, d1 = f1.numerator, f1.denominator
            n2, d2 = f2.numerator, f2.denominator

        result = f1 + f2 if op == "+" else f1 - f2
        if result < 0:
            continue

        return make_question(
            section, marks, difficulty,
            f"Calculate: {n1}/{d1} {op} {n2}/{d2}. Give your answer as a simplified fraction.",
            {"type": "fraction", "value": f"{result.numerator}/{result.denominator}", "accept_equivalents": True},
            hint="Use a common denominator (LCM).",
            steps=["Find the LCM.", "Convert both fractions.", "Add/subtract numerators.", "Simplify."],
            example={
                "prompt": "Example: 1/4 + 1/2",
                "work": ["LCM is 4", "1/2 = 2/4", "1/4 + 2/4 = 3/4"],
                "answer": "3/4",
            },
        )

    return make_question(
        section, marks, difficulty,
        "Calculate: 1/2 + 1/3. Give your answer as a simplified fraction.",
        {"type": "fraction", "value": "5/6", "accept_equivalents": True},
        hint="Use a common denominator."
    )


def gen_fraction_of_quantity(section: str, marks: int, difficulty: int) -> Dict[str, Any]:
    d = random.choice([2, 3, 4, 5, 6, 8, 10, 12])
    n = random.randint(1, d - 1)

    qty = random.choice([d * k for k in range(5, 81)])  # divisible by d
    ans = (qty // d) * n

    return make_question(
        section, marks, difficulty,
        f"Find {n}/{d} of {qty}.",
        {"type": "numeric", "value": str(ans), "accept_equivalents": True},
        hint="Divide by the denominator, then multiply by the numerator.",
        steps=["Divide the quantity by the denominator.", "Multiply by the numerator."],
        example={"prompt": "Example: 3/4 of 20", "work": ["20 ÷ 4 = 5", "5 × 3 = 15"], "answer": "15"},
    )


# ----------------------------
# Percent
# ----------------------------

def gen_percent_of_quantity(section: str, marks: int, difficulty: int) -> Dict[str, Any]:
    p = random.choice([10, 20, 25, 30, 40, 50, 60, 75])
    qty = random.choice([20, 40, 60, 80, 100, 120, 150, 200, 240, 300, 400, 500])
    ans = int(qty * p / 100)

    return make_question(
        section, marks, difficulty,
        f"Find {p}% of {qty}.",
        {"type": "numeric", "value": str(ans), "accept_equivalents": True},
        hint="Convert percent to a fraction/decimal then multiply.",
        steps=["Write p% as p/100.", "Multiply by the quantity.", "Simplify."],
        example={"prompt": "Example: 25% of 200", "work": ["25% = 1/4", "1/4 of 200 = 50"], "answer": "50"},
    )


# ----------------------------
# Measurement / Geometry
# ----------------------------

def gen_perimeter_rectangle(section: str, marks: int, difficulty: int) -> Dict[str, Any]:
    L = random.randint(4, 60)
    W = random.randint(3, 45)
    ans = 2 * (L + W)

    return make_question(
        section, marks, difficulty,
        f"A rectangle has length {L} cm and width {W} cm. What is its perimeter (cm)?",
        {"type": "numeric", "value": str(ans), "accept_equivalents": True},
        hint="Perimeter = 2 × (length + width).",
        steps=["Add length + width.", "Multiply by 2."],
        example={"prompt": "Example: L=5, W=3", "work": ["2×(5+3)=16"], "answer": "16"},
    )


def gen_area_rectangle(section: str, marks: int, difficulty: int) -> Dict[str, Any]:
    L = random.randint(4, 60)
    W = random.randint(3, 45)
    ans = L * W

    return make_question(
        section, marks, difficulty,
        f"A rectangle has length {L} cm and width {W} cm. What is its area (cm²)?",
        {"type": "numeric", "value": str(ans), "accept_equivalents": True},
        hint="Area = length × width.",
        steps=["Multiply length by width."],
        example={"prompt": "Example: 4×6", "work": ["4×6 = 24"], "answer": "24"},
    )


def gen_triangle_angle(section: str, marks: int, difficulty: int) -> Dict[str, Any]:
    a = random.randint(20, 120)
    b = random.randint(20, 120)
    if a + b >= 179:
        b = 180 - a - 1
    c = 180 - (a + b)

    return make_question(
        section, marks, difficulty,
        f"In a triangle, two angles are {a}° and {b}°. What is the third angle?",
        {"type": "numeric", "value": str(c), "accept_equivalents": True},
        hint="Angles in a triangle add up to 180°.",
        steps=["Add the two angles.", "Subtract from 180."],
        example={"prompt": "Example: 50° and 60°", "work": ["180 - (50+60) = 70"], "answer": "70"},
    )


# ----------------------------
# Statistics (MVP text-based)
# ----------------------------

def gen_stat_read_table_basic(section: str, marks: int, difficulty: int) -> Dict[str, Any]:
    labels = ["A", "B", "C", "D"]
    values = [random.randint(2, 9) for _ in labels]

    ask = random.choice(labels)
    ans = values[labels.index(ask)]

    prompt = (
        "Look at the table and answer.\n"
        f"Item:  {labels[0]}  {labels[1]}  {labels[2]}  {labels[3]}\n"
        f"Count: {values[0]}  {values[1]}  {values[2]}  {values[3]}\n\n"
        f"What is the count for {ask}?"
    )

    return make_question(
        section, marks, difficulty,
        prompt,
        {"type": "numeric", "value": str(ans), "accept_equivalents": True},
        hint="Read the value directly under the label.",
        steps=["Find the label asked.", "Read the count under it."],
        example={"prompt": "Example: If B has count 7, the answer is 7.", "work": ["Read B column → 7"], "answer": "7"},
    )


def gen_stat_read_bar_chart_basic(section: str, marks: int, difficulty: int) -> Dict[str, Any]:
    cats = ["Mon", "Tue", "Wed", "Thu"]
    vals = [random.randint(1, 9) for _ in cats]

    ask = random.choice(cats)
    ans = vals[cats.index(ask)]

    bars = "\n".join([f"{c}: {'█'*v} ({v})" for c, v in zip(cats, vals)])

    prompt = (
        "Read the bar chart and answer.\n"
        f"{bars}\n\n"
        f"How many for {ask}?"
    )

    return make_question(
        section, marks, difficulty,
        prompt,
        {"type": "numeric", "value": str(ans), "accept_equivalents": True},
        hint="Count the blocks (or read the number in brackets).",
        steps=["Find the bar for the day.", "Read the number shown."],
        example={"prompt": "Example: Tue: ███ (3)", "work": ["Value is 3"], "answer": "3"},
    )


# ----------------------------
# Skill router
# ----------------------------

def generate_by_skill(skill_id: str, section: str, marks: int, difficulty: int) -> Dict[str, Any]:
    # Numbers
    if skill_id == "std4_add_sub_4digit":
        return gen_add_sub_4digit(section, marks, difficulty)
    if skill_id == "std4_mult_2digit_by_1digit":
        return gen_mult_2digit_by_1digit(section, marks, difficulty)
    if skill_id == "std4_div_exact":
        return gen_div_exact(section, marks, difficulty)

    # Fractions / Percent
    if skill_id == "std5_add_sub_unlike_denoms":
        return gen_add_sub_fractions_unlike(section, marks, difficulty)
    if skill_id == "std5_fraction_of_quantity":
        return gen_fraction_of_quantity(section, marks, difficulty)
    if skill_id == "std5_percent_of_quantity":
        return gen_percent_of_quantity(section, marks, difficulty)

    # Measurement / Geometry
    if skill_id == "std4_perimeter_rectangle":
        return gen_perimeter_rectangle(section, marks, difficulty)
    if skill_id == "std4_area_rectangle":
        return gen_area_rectangle(section, marks, difficulty)
    if skill_id == "std5_triangle_angle":
        return gen_triangle_angle(section, marks, difficulty)

    # Statistics
    if skill_id == "stat_read_table_basic":
        return gen_stat_read_table_basic(section, marks, difficulty)
    if skill_id == "stat_read_bar_chart_basic":
        return gen_stat_read_bar_chart_basic(section, marks, difficulty)

    # Safe fallback (should be rare if skill IDs match)
    return make_question(
        section=section,
        marks=marks,
        difficulty=difficulty,
        prompt="Calculate: 12 + 8",
        correct_answer={"type": "numeric", "value": "20", "accept_equivalents": True},
        hint="Add carefully.",
        steps=["Add 12 and 8."],
        example={"prompt": "Example: 12 + 8", "work": ["12 + 8 = 20"], "answer": "20"},
    )
