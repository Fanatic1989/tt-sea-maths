"use client";

import { useEffect, useMemo, useState } from "react";
import QuestionCard from "../components/QuestionCard";
import { fetchSeaPaper, checkAnswer, logAttempt } from "../lib/api";

export default function SeaPage() {
  const [loading, setLoading] = useState(false);
  const [paper, setPaper] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [index, setIndex] = useState(0);
  const [attemptsByQid, setAttemptsByQid] = useState({});
  const [error, setError] = useState("");

  // timer (simple countdown)
  const [remainingSec, setRemainingSec] = useState(0);
  const totalSec = paper?.duration_sec ?? 0;

  const currentQuestion = useMemo(() => {
    return questions && questions.length > 0 ? questions[index] : null;
  }, [questions, index]);

  const attempts = useMemo(() => {
    if (!currentQuestion) return 0;
    return attemptsByQid[currentQuestion.question_id] ?? 0;
  }, [attemptsByQid, currentQuestion]);

  async function startPaper(mode = "full") {
    setError("");
    setLoading(true);
    try {
      const p = await fetchSeaPaper(mode);
      setPaper(p);
      setQuestions(p.questions || []);
      setIndex(0);
      setAttemptsByQid({});
      setRemainingSec(p.duration_sec || 0);
    } catch (e) {
      setError("Failed to fetch");
    } finally {
      setLoading(false);
    }
  }

  // auto start once
  useEffect(() => {
    startPaper("full");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // countdown timer
  useEffect(() => {
    if (!remainingSec) return;
    const t = setInterval(() => {
      setRemainingSec((s) => (s > 0 ? s - 1 : 0));
    }, 1000);
    return () => clearInterval(t);
  }, [remainingSec]);

  function fmt(sec) {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${String(s).padStart(2, "0")}`;
  }

  async function handleCheck(userInput, correctAnswer) {
    if (!currentQuestion) return;

    const qid = currentQuestion.question_id;
    const nextAttempts = (attemptsByQid[qid] ?? 0) + 1;

    setAttemptsByQid((prev) => ({ ...prev, [qid]: nextAttempts }));

    try {
      const result = await checkAnswer(String(userInput ?? ""), correctAnswer);

      // log attempt (best-effort)
      logAttempt({
        session_id: paper?.paper_id || "session",
        paper_id: paper?.paper_id || null,
        question_id: qid,
        entered_answer: String(userInput ?? ""),
        is_correct: !!result.is_correct,
        attempt_count: nextAttempts,
        hint_level_used: 0,
        used_example: false,
        used_tutor: false,
        used_show_step: false,
        used_reveal_solution: false,
        time_spent_sec: 0,
      });

      if (result.is_correct) {
        // move to next automatically (optional)
        if (index < questions.length - 1) setIndex(index + 1);
      } else {
        // show feedback in a simple alert for MVP
        alert(result.feedback || "Not correct yet. Try again.");
      }
    } catch {
      alert("Failed to check answer");
    }
  }

  function prev() {
    if (index > 0) setIndex(index - 1);
  }

  function next() {
    // locked-by-learning MVP: block if attempts === 0 or last answer wrong.
    // For now we allow next if they have at least 1 attempt (you can tighten later)
    if (index < questions.length - 1) setIndex(index + 1);
  }

  // helpers (simple MVP)
  function showExample(q) {
    if (!q) return;
    alert(q.example?.prompt ? `${q.example.prompt}\n\nAnswer: ${q.example.answer || ""}` : "No example yet.");
  }
  function showSteps(q) {
    if (!q) return;
    alert(q.steps?.length ? q.steps.join("\n") : "No steps yet.");
  }
  function revealSolution(q) {
    if (!q) return;
    alert(q.correct_answer?.value ? `Solution: ${q.correct_answer.value}` : "No solution.");
  }

  return (
    <div style={{ padding: 24, maxWidth: 1100, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
        <div>
          <h1 style={{ margin: 0 }}>TT SEA Maths Tutor</h1>
          <div className="muted">SEA Study Simulator · STD 1–5 Tutor</div>
        </div>
        <div className="muted" style={{ fontWeight: 700 }}>
          ⏳ {totalSec ? fmt(remainingSec) : "--:--"}
        </div>
      </div>

      <div style={{ marginTop: 16 }}>
        <button className="btnSecondary" onClick={() => startPaper("full")} disabled={loading}>
          Start Full SEA Paper (40 questions)
        </button>
        <span style={{ marginLeft: 10 }} className="muted">
          {paper?.paper_id ? `Paper: ${paper.paper_id}` : ""}
        </span>
      </div>

      {error ? (
        <div style={{ marginTop: 16 }} className="card">
          <strong>Error:</strong> {error}
        </div>
      ) : null}

      {/* ✅ DEBUG LINE: proves prompt exists */}
      <div style={{ marginTop: 12 }} className="muted">
        Debug prompt: {currentQuestion?.prompt ? currentQuestion.prompt : "(missing)"}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.35fr 0.65fr", gap: 18, marginTop: 16 }}>
        <div>
          <QuestionCard
            question={currentQuestion}
            index={index}
            total={questions.length}
            attempts={attempts}
            onCheck={handleCheck}
            onPrev={prev}
            onNext={next}
            nextLocked={false}
            showExample={showExample}
            showSteps={showSteps}
            revealSolution={revealSolution}
          />
        </div>

        <div className="card">
          <div className="cardTitle">Question Navigator</div>
          <div className="muted">Tap a number to jump (MVP)</div>

          <div style={{ marginTop: 12, display: "flex", flexWrap: "wrap", gap: 8 }}>
            {questions.map((q, i) => (
              <button
                key={q.question_id || i}
                className={i === index ? "pillActive" : "pill"}
                onClick={() => setIndex(i)}
              >
                {i + 1}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
