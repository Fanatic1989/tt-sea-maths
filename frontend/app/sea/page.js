"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import QuestionCard from "../components/QuestionCard";
import { fetchSeaPaper, checkAnswer, logAttempt } from "../lib/api";

function fmt(sec) {
  const s = Math.max(0, Number(sec || 0));
  const mm = String(Math.floor(s / 60)).padStart(2, "0");
  const ss = String(Math.floor(s % 60)).padStart(2, "0");
  return `${mm}:${ss}`;
}

export default function SeaPage() {
  const [loading, setLoading] = useState(false);
  const [paper, setPaper] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [index, setIndex] = useState(0);

  const [attemptsByQid, setAttemptsByQid] = useState({});
  const [solvedByQid, setSolvedByQid] = useState({});
  const [feedback, setFeedback] = useState("");
  const [error, setError] = useState("");

  // ✅ TIMER
  const [remainingSec, setRemainingSec] = useState(0);
  const timerRef = useRef(null);

  const currentQuestion = useMemo(() => {
    return questions.length ? questions[index] : null;
  }, [questions, index]);

  const attempts = useMemo(() => {
    if (!currentQuestion) return 0;
    return attemptsByQid[currentQuestion.question_id] ?? 0;
  }, [attemptsByQid, currentQuestion]);

  const isSolved = useMemo(() => {
    if (!currentQuestion) return false;
    return !!solvedByQid[currentQuestion.question_id];
  }, [solvedByQid, currentQuestion]);

  const timeUp = remainingSec <= 0 && !!paper?.duration_sec;

  function stopTimer() {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }

  function startTimer(seconds) {
    stopTimer();
    setRemainingSec(seconds);

    timerRef.current = setInterval(() => {
      setRemainingSec((s) => {
        if (s <= 1) {
          // hit 0 → stop
          stopTimer();
          return 0;
        }
        return s - 1;
      });
    }, 1000);
  }

  async function startPaper(mode = "full") {
    setError("");
    setFeedback("");
    setLoading(true);
    try {
      const p = await fetchSeaPaper(mode);
      setPaper(p);
      setQuestions(p.questions || []);
      setIndex(0);
      setAttemptsByQid({});
      setSolvedByQid({});

      // ✅ start/reset timer ONLY after paper loads
      const dur = Number(p?.duration_sec ?? 4500);
      startTimer(dur);
    } catch {
      setError("Failed to fetch");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    startPaper("full");
    return () => stopTimer();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleCheck(userInputRaw, correctAnswer) {
    if (!currentQuestion || timeUp) return;

    const user_input = String(userInputRaw ?? "").trim();
    const qid = currentQuestion.question_id;

    setFeedback("");

    const nextAttempts = (attemptsByQid[qid] ?? 0) + 1;
    setAttemptsByQid((prev) => ({ ...prev, [qid]: nextAttempts }));

    try {
      const result = await checkAnswer(user_input, correctAnswer);

      // best-effort logging
      logAttempt({
        session_id: paper?.paper_id || "session",
        paper_id: paper?.paper_id || null,
        question_id: qid,
        entered_answer: user_input,
        is_correct: !!result.is_correct,
        attempt_count: nextAttempts,
        hint_level_used: 0,
        used_example: false,
        used_tutor: false,
        used_show_step: false,
        used_reveal_solution: false, // keep false (feature removed)
        time_spent_sec: 0,
      });

      if (result.is_correct) {
        setSolvedByQid((prev) => ({ ...prev, [qid]: true }));
        setFeedback("✅ Correct! Next unlocked.");

        // auto-advance
        setIndex((i) => (i < questions.length - 1 ? i + 1 : i));
      } else {
        setFeedback(result.feedback || "❌ Not correct yet. Try again.");
      }
    } catch {
      setFeedback("❌ Failed to check answer (API error).");
    }
  }

  function prev() {
    if (timeUp) return;
    setFeedback("");
    setIndex((i) => (i > 0 ? i - 1 : 0));
  }

  function next() {
    if (timeUp) return;
    setFeedback("");
    setIndex((i) => (i < questions.length - 1 ? i + 1 : i));
  }

  function jumpTo(i) {
    if (timeUp) return;
    setFeedback("");
    setIndex(() => Math.max(0, Math.min(i, questions.length - 1)));
  }

  // helper popups (MVP)
  function showExample(q) {
    if (!q || timeUp) return;
    if (q.example?.prompt) {
      const work = Array.isArray(q.example.work) ? q.example.work.join("\n") : "";
      alert(`${q.example.prompt}\n\n${work}\n\nAnswer: ${q.example.answer || ""}`);
    } else {
      alert("No example available for this question yet.");
    }
  }

  function showSteps(q) {
    if (!q || timeUp) return;
    if (Array.isArray(q.steps) && q.steps.length) {
      alert(q.steps.join("\n"));
    } else {
      alert("No steps available for this question yet.");
    }
  }

  return (
    <div style={{ padding: 24, maxWidth: 1100, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
        <div>
          <h1 style={{ margin: 0 }}>TT SEA Maths Tutor</h1>
          <div className="muted">SEA Study Simulator · STD 1–5 Tutor</div>
          <div className="muted">{paper?.paper_id ? `Paper: ${paper.paper_id}` : ""}</div>
        </div>

        {/* ✅ Timer UI */}
        <div style={{ textAlign: "right" }}>
          <div className="muted" style={{ fontSize: 13 }}>Time left</div>
          <div style={{ fontSize: 28, fontWeight: 800 }}>{fmt(remainingSec)}</div>
          {timeUp ? (
            <div style={{ marginTop: 6, fontWeight: 800 }}>⛔ Time’s up (paper locked)</div>
          ) : null}
        </div>

        <div style={{ display: "flex", gap: 10 }}>
          <button className="btnSecondary" onClick={() => startPaper("full")} disabled={loading}>
            Restart Paper
          </button>
        </div>
      </div>

      {error ? (
        <div style={{ marginTop: 16 }} className="card">
          <strong>Error:</strong> {error}
        </div>
      ) : null}

      {feedback ? (
        <div style={{ marginTop: 12 }} className="card">
          {feedback}
        </div>
      ) : null}

      <div style={{ display: "grid", gridTemplateColumns: "1.35fr 0.65fr", gap: 18, marginTop: 16 }}>
        <div>
          <QuestionCard
            key={currentQuestion?.question_id || index}
            question={currentQuestion}
            index={index}
            total={questions.length}
            attempts={attempts}
            onCheck={handleCheck}
            onPrev={prev}
            onNext={next}
            nextLocked={!isSolved}
            showExample={showExample}
            showSteps={showSteps}
            disabled={timeUp}          // ✅ lock inputs when time up
          />
        </div>

        <div className="card">
          <div className="cardTitle">Question Navigator</div>
          <div className="muted">Tap a number to jump.</div>

          <div style={{ marginTop: 12, display: "flex", flexWrap: "wrap", gap: 8 }}>
            {questions.map((q, i) => (
              <button
                key={q.question_id || i}
                className={i === index ? "pillActive" : "pill"}
                onClick={() => jumpTo(i)}
                disabled={timeUp}
                title={timeUp ? "Paper locked (time up)" : ""}
              >
                {i + 1}
              </button>
            ))}
          </div>

          <div className="muted" style={{ marginTop: 12 }}>
            SEA timing: 75 minutes (4500 seconds).
          </div>
        </div>
      </div>
    </div>
  );
}
