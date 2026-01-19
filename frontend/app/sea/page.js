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
  const [solvedByQid, setSolvedByQid] = useState({});
  const [feedback, setFeedback] = useState("");
  const [error, setError] = useState("");

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
    } catch {
      setError("Failed to fetch");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    startPaper("full");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleCheck(userInputRaw, correctAnswer) {
    if (!currentQuestion) return;

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
        used_reveal_solution: false,
        time_spent_sec: 0,
      });

      if (result.is_correct) {
        setSolvedByQid((prev) => ({ ...prev, [qid]: true }));
        setFeedback("✅ Correct! Next unlocked.");

        // ✅ auto-advance safely (no stale index)
        setIndex((i) => (i < questions.length - 1 ? i + 1 : i));
      } else {
        setFeedback(result.feedback || "❌ Not correct yet. Try again.");
      }
    } catch {
      setFeedback("❌ Failed to check answer (API error).");
    }
  }

  function prev() {
    setFeedback("");
    setIndex((i) => (i > 0 ? i - 1 : 0));
  }

  function next() {
    setFeedback("");
    setIndex((i) => (i < questions.length - 1 ? i + 1 : i));
  }

  function jumpTo(i) {
    setFeedback("");
    setIndex(() => Math.max(0, Math.min(i, questions.length - 1)));
  }

  // helper popups (MVP)
  function showExample(q) {
    if (!q) return;
    if (q.example?.prompt) {
      const work = Array.isArray(q.example.work) ? q.example.work.join("\n") : "";
      alert(`${q.example.prompt}\n\n${work}\n\nAnswer: ${q.example.answer || ""}`);
    } else {
      alert("No example available for this question yet.");
    }
  }

  function showSteps(q) {
    if (!q) return;
    if (Array.isArray(q.steps) && q.steps.length) {
      alert(q.steps.join("\n"));
    } else {
      alert("No steps available for this question yet.");
    }
  }

  function revealSolution(q) {
    if (!q) return;
    const v = q.correct_answer?.value;
    alert(v ? `Solution: ${v}` : "No solution available.");
  }

  return (
    <div style={{ padding: 24, maxWidth: 1100, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
        <div>
          <h1 style={{ margin: 0 }}>TT SEA Maths Tutor</h1>
          <div className="muted">SEA Study Simulator · STD 1–5 Tutor</div>
          <div className="muted">{paper?.paper_id ? `Paper: ${paper.paper_id}` : ""}</div>
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
            key={currentQuestion?.question_id || index} // ✅ forces rerender when question changes
            question={currentQuestion}
            index={index}
            total={questions.length}
            attempts={attempts}
            onCheck={handleCheck}
            onPrev={prev}
            onNext={next}
            nextLocked={!isSolved} // ✅ locked until correct
            showExample={showExample}
            showSteps={showSteps}
            revealSolution={revealSolution}
          />
        </div>

        <div className="card">
          <div className="cardTitle">Question Navigator</div>
          <div className="muted">Tap a number to jump (MVP). We’ll lock jumping later.</div>

          <div style={{ marginTop: 12, display: "flex", flexWrap: "wrap", gap: 8 }}>
            {questions.map((q, i) => (
              <button
                key={q.question_id || i}
                className={i === index ? "pillActive" : "pill"}
                onClick={() => jumpTo(i)}
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

