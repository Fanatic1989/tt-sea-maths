from __future__ import annotations

import random
from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Dict, List, Tuple


@dataclass
class GeneratedQuestion:
    question_id: str
    skill_id: str
    section: str
    marks: int
    difficulty: int
    prompt_text: str
    answer_type: str
    correct_answer: Dict[str, Any]
    solution_steps: List[Dict[str, Any]]
    example_help: Dict[str, Any]
    common_mistakes: List[str]
    estimated_time_sec: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question_id": self.question_id,
            "skill_id": self.skill_id,
            "section": self.section,
            "marks": self.marks,
            "difficulty": self.difficulty,
            "prompt_text": self.prompt_text,
            "answer_type": self.answer_type,
            "correct_answer": self.correct_answer,
            "solution_steps": self.solution_steps,
            "example_help": self.example_help,
            "common_mistakes": self.common_mistakes,
            "estimated_time_sec": self.estimated_time_sec,
        }


def _qid(prefix: str) -> str:
    return f"{prefix}_{random.randint(100000, 999999)}"


def gen_add_sub(section: str, marks: int, difficulty: int) -> GeneratedQuestion:
    # Clean integer arithmetic for SEA-style short answers
    max_n = 100 if difficulty == 1 else 1000 if difficulty == 2 else 9999
    a = random.randint(10 if difficulty > 1 else 0, max_n)
    b = random.randint(10 if difficulty > 1 else 0, max_n)
    op = random.choice(["+", "-"])
    if op == "-" and b > a:
        a, b = b, a
    ans = a + b if op == "+" else a - b
    prompt = f"Calculate: {a} {op} {b}"
    steps = [
        {"step": 1, "title": "Compute", "work": f"{a} {op} {b} = {ans}"}
    ]
    example_a = random.randint(0, 50)
    example_b = random.randint(0, 50)
    example_op = op
    if example_op == "-" and example_b > example_a:
        example_a, example_b = example_b, example_a
    example_ans = example_a + example_b if example_op == "+" else example_a - example_b
    example = {
        "rule": "Work carefully with the signs. For subtraction, you can subtract the smaller from the larger.",
        "examples": [
            {
                "prompt": f"{example_a} {example_op} {example_b} = ?",
                "steps": [f"{example_a} {example_op} {example_b} = {example_ans}"],
                "answer": str(example_ans),
            }
        ],
    }
    mistakes = ["Mixing up addition and subtraction.", "Borrowing/carrying errors in column work."]
    return GeneratedQuestion(
        question_id=_qid("arith"),
        skill_id="core_add_sub",
        section=section,
        marks=marks,
        difficulty=difficulty,
        prompt_text=prompt,
        answer_type="numeric",
        correct_answer={"type": "numeric", "value": ans, "tolerance": 0},
        solution_steps=steps,
        example_help=example,
        common_mistakes=mistakes,
        estimated_time_sec=60 if marks == 1 else 120,
    )


def gen_simplify_fraction(section: str, marks: int, difficulty: int) -> GeneratedQuestion:
    # Generate reducible fraction and ask to simplify
    n = random.randint(2, 20 if difficulty == 1 else 50)
    d = random.randint(2, 20 if difficulty == 1 else 60)
    k = random.randint(2, 5)
    frac = Fraction(n * k, d * k)
    prompt = f"Simplify: {frac.numerator}/{frac.denominator}"
    simp = frac  # already reduced by Fraction
    steps = [
        {"step": 1, "title": "Find a common factor", "work": "Divide top and bottom by the same number."},
        {"step": 2, "title": "Simplify", "work": f"= {simp.numerator}/{simp.denominator}"},
    ]
    example = {
        "rule": "To simplify a fraction, divide numerator and denominator by their highest common factor (HCF).",
        "examples": [
            {
                "prompt": "8/12 = ?",
                "steps": ["HCF of 8 and 12 is 4", "8÷4 / 12÷4 = 2/3"],
                "answer": "2/3",
            }
        ],
    }
    mistakes = ["Dividing only the top or only the bottom.", "Not reducing fully."]
    return GeneratedQuestion(
        question_id=_qid("frac"),
        skill_id="std4_simplify_fractions",
        section=section,
        marks=marks,
        difficulty=difficulty,
        prompt_text=prompt,
        answer_type="fraction",
        correct_answer={
            "type": "fraction",
            "numerator": simp.numerator,
            "denominator": simp.denominator,
            "accept_equivalents": True,
        },
        solution_steps=steps,
        example_help=example,
        common_mistakes=mistakes,
        estimated_time_sec=90,
    )


def gen_add_sub_fractions_unlike(section: str, marks: int, difficulty: int) -> GeneratedQuestion:
    denoms = [2, 3, 4, 5, 6, 8, 10, 12]
    d1, d2 = random.sample(denoms, 2)
    # keep numbers small
    n1 = random.randint(1, d1 - 1)
    n2 = random.randint(1, d2 - 1)
    op = random.choice(["+", "-"])
    f1 = Fraction(n1, d1)
    f2 = Fraction(n2, d2)
    if op == "-" and f2 > f1:
        f1, f2 = f2, f1
        n1, d1 = f1.numerator, f1.denominator
        n2, d2 = f2.numerator, f2.denominator
    ans = f1 + f2 if op == "+" else f1 - f2
    prompt = f"Calculate: {n1}/{d1} {op} {n2}/{d2}"
    lcm = (d1 * d2) // Fraction(d1, d2).denominator
    m1 = lcm // d1
    m2 = lcm // d2
    eq1 = Fraction(n1 * m1, d1 * m1)
    eq2 = Fraction(n2 * m2, d2 * m2)
    steps = [
        {"step": 1, "title": "Common denominator", "work": f"LCM of {d1} and {d2} is {lcm}."},
        {"step": 2, "title": "Rewrite fractions", "work": f"{n1}/{d1} = {eq1.numerator}/{lcm}, {n2}/{d2} = {eq2.numerator}/{lcm}"},
        {"step": 3, "title": "Add/Subtract", "work": f"= {(eq1.numerator)} {op} {(eq2.numerator)} over {lcm}"},
        {"step": 4, "title": "Simplify", "work": f"= {ans.numerator}/{ans.denominator}"},
    ]
    example = {
        "rule": "Make denominators the same (LCM), then add/subtract the numerators.",
        "examples": [
            {
                "prompt": "1/3 + 1/6 = ?",
                "steps": ["1/3 = 2/6", "2/6 + 1/6 = 3/6", "3/6 = 1/2"],
                "answer": "1/2",
            }
        ],
    }
    mistakes = ["Adding denominators.", "Forgetting to simplify."]
    return GeneratedQuestion(
        question_id=_qid("fracop"),
        skill_id="std5_add_sub_unlike_denoms",
        section=section,
        marks=marks,
        difficulty=difficulty,
        prompt_text=prompt,
        answer_type="fraction",
        correct_answer={
            "type": "fraction",
            "numerator": ans.numerator,
            "denominator": ans.denominator,
            "accept_equivalents": True,
        },
        solution_steps=steps,
        example_help=example,
        common_mistakes=mistakes,
        estimated_time_sec=150,
    )


def gen_percent_of_quantity(section: str, marks: int, difficulty: int) -> GeneratedQuestion:
    percents = [10, 20, 25, 30, 40, 50, 60, 75]
    p = random.choice(percents)
    base = random.randint(20, 500)
    # force clean answer by making base divisible by 100/p when needed
    divisor = 100 // Fraction(p, 100).numerator if p in [25, 50, 75] else 10
    base = (base // divisor) * divisor
    ans = int(base * p / 100)
    prompt = f"Find {p}% of {base}."
    steps = [
        {"step": 1, "title": "Convert percent", "work": f"{p}% = {p}/100"},
        {"step": 2, "title": "Multiply", "work": f"{p}/100 × {base} = {ans}"},
    ]
    example = {
        "rule": "Percent means ‘out of 100’. Multiply by p/100.",
        "examples": [
            {"prompt": "Find 25% of 80", "steps": ["25% = 25/100", "25/100 × 80 = 20"], "answer": "20"}
        ],
    }
    mistakes = ["Dividing by the percent instead of multiplying.", "Forgetting /100."]
    return GeneratedQuestion(
        question_id=_qid("pct"),
        skill_id="std5_percent_of_quantity",
        section=section,
        marks=marks,
        difficulty=difficulty,
        prompt_text=prompt,
        answer_type="numeric",
        correct_answer={"type": "numeric", "value": ans, "tolerance": 0},
        solution_steps=steps,
        example_help=example,
        common_mistakes=mistakes,
        estimated_time_sec=150,
    )


def gen_elapsed_time(section: str, marks: int, difficulty: int) -> GeneratedQuestion:
    # Output duration in minutes (clean) for auto-checking
    start_h = random.randint(1, 12)
    start_m = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    duration = random.choice([15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 75, 90, 105, 120])
    prompt = f"A class starts at {start_h}:{start_m:02d}. It lasts {duration} minutes. What time does it end? (write as H:MM)"
    total_minutes = (start_h % 12) * 60 + start_m + duration
    end_h = (total_minutes // 60) % 12
    end_h = 12 if end_h == 0 else end_h
    end_m = total_minutes % 60
    answer_str = f"{end_h}:{end_m:02d}"
    steps = [
        {"step": 1, "title": "Add minutes", "work": f"Start minutes: {(start_h%12)*60 + start_m}. Add {duration}."},
        {"step": 2, "title": "Convert back to time", "work": f"End time = {answer_str}"},
    ]
    example = {
        "rule": "Convert to minutes, add, then convert back.",
        "examples": [
            {"prompt": "Starts 2:30, lasts 40 min", "steps": ["2:30 = 150 min", "150+40=190", "190=3:10"], "answer": "3:10"}
        ],
    }
    mistakes = ["Forgetting to carry 60 minutes to an hour.", "Writing minutes without two digits."]
    return GeneratedQuestion(
        question_id=_qid("time"),
        skill_id="std5_elapsed_time_harder",
        section=section,
        marks=marks,
        difficulty=difficulty,
        prompt_text=prompt,
        answer_type="text_time",
        correct_answer={"type": "time_hhmm", "value": answer_str},
        solution_steps=steps,
        example_help=example,
        common_mistakes=mistakes,
        estimated_time_sec=180,
    )


def generate_by_skill(skill_id: str, section: str, marks: int, difficulty: int) -> GeneratedQuestion:
    # Map a subset of skills to working generators. Expand this map as you build.
    if skill_id == "std5_add_sub_unlike_denoms":
        return gen_add_sub_fractions_unlike(section, marks, difficulty)
    if skill_id == "std4_simplify_fractions":
        return gen_simplify_fraction(section, marks, difficulty)
    if skill_id == "std5_percent_of_quantity":
        return gen_percent_of_quantity(section, marks, difficulty)
    if skill_id == "std5_elapsed_time_harder":
        return gen_elapsed_time(section, marks, difficulty)

    # Fallback: clean integer arithmetic (keeps MVP usable)
    return gen_add_sub(section, marks, difficulty)
