from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Dict, Tuple


def _parse_fraction(s: str) -> Fraction | None:
    s = s.strip().replace(" ", "")
    # mixed number like 1 1/2 -> handled before removal of spaces
    m = re.match(r"^(-?\d+)/(\d+)$", s)
    if not m:
        return None
    n = int(m.group(1))
    d = int(m.group(2))
    if d == 0:
        return None
    return Fraction(n, d)


def _parse_mixed(s: str) -> Fraction | None:
    s = s.strip()
    m = re.match(r"^(-?\d+)\s+(\d+)/(\d+)$", s)
    if not m:
        return None
    whole = int(m.group(1))
    n = int(m.group(2))
    d = int(m.group(3))
    if d == 0:
        return None
    frac = Fraction(n, d)
    return Fraction(whole, 1) + frac if whole >= 0 else Fraction(whole, 1) - frac


def check_answer(user_input: str, correct: Dict[str, Any]) -> Tuple[bool, str]:
    """Returns (is_correct, feedback)."""
    u = (user_input or "").strip()
    ctype = correct.get("type")

    if ctype == "numeric":
        try:
            uv = float(u)
        except ValueError:
            return False, "Enter a number."
        val = float(correct.get("value"))
        tol = float(correct.get("tolerance", 0))
        ok = abs(uv - val) <= tol
        return ok, "Correct!" if ok else "Not quite. Try again."

    if ctype == "fraction":
        frac = _parse_mixed(u) or _parse_fraction(u)
        if frac is None:
            return False, "Enter a fraction like 3/4 (or a mixed number like 1 1/2)."
        cn = int(correct.get("numerator"))
        cd = int(correct.get("denominator"))
        corr = Fraction(cn, cd)
        ok = frac == corr if correct.get("accept_equivalents", True) else (frac.numerator == cn and frac.denominator == cd)
        return ok, "Correct!" if ok else "Not quite. Simplify if needed and try again."

    if ctype == "time_hhmm":
        # Accept H:MM with optional leading zeros in minutes.
        target = str(correct.get("value")).strip()
        norm = u.replace(" ", "")
        m = re.match(r"^(\d{1,2}):(\d{2})$", norm)
        if not m:
            return False, "Enter time like 3:05."
        ok = f"{int(m.group(1))}:{m.group(2)}" == target
        return ok, "Correct!" if ok else "Not quite. Check your carry of minutes to hours."

    return False, "This question type is not supported yet."
