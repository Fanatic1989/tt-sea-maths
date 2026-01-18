from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, Optional

from .db import init_db, get_conn
from .composer import compose_sea_paper
from .checker import check_answer

app = FastAPI(title="TT SEA Maths Tutor API")


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/sea/paper")
def get_sea_paper(mode: str = "full") -> Dict[str, Any]:
    return compose_sea_paper(mode=mode)


class CheckRequest(BaseModel):
    user_input: str
    correct_answer: Dict[str, Any]


@app.post("/answer/check")
def answer_check(req: CheckRequest) -> Dict[str, Any]:
    ok, feedback = check_answer(req.user_input, req.correct_answer)
    return {"is_correct": ok, "feedback": feedback}


class AttemptLog(BaseModel):
    session_id: str
    paper_id: Optional[str] = None
    question_id: str
    entered_answer: str
    is_correct: bool
    attempt_count: int = 1
    hint_level_used: int = 0
    used_example: bool = False
    used_tutor: bool = False
    used_show_step: bool = False
    used_reveal_solution: bool = False
    time_spent_sec: int = 0


@app.post("/attempt/log")
def log_attempt(a: AttemptLog) -> Dict[str, str]:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO attempts (session_id, paper_id, question_id, entered_answer, is_correct, attempt_count, hint_level_used, used_example, used_tutor, used_show_step, used_reveal_solution, time_spent_sec) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                a.session_id,
                a.paper_id,
                a.question_id,
                a.entered_answer,
                1 if a.is_correct else 0,
                a.attempt_count,
                a.hint_level_used,
                1 if a.used_example else 0,
                1 if a.used_tutor else 0,
                1 if a.used_show_step else 0,
                1 if a.used_reveal_solution else 0,
                a.time_spent_sec,
            ),
        )
        conn.commit()
    return {"status": "logged"}
