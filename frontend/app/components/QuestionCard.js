"use client";

import { useMemo, useState } from "react";

export default function QuestionCard({
  question,
  index = 0,
  total = 0,
  attempts = 0,
  onCheck,
  onPrev,
  onNext,
  nextLocked = true,
  showExample,
  showSteps,
  revealSolution,
}) {
  const [answer, setAnswer] = useState("");

  const headerLeft = useMemo(() => {
    if (!question) return "";
    const marksLabel = question.marks === 1 ? "1 mark" : `${question.marks} marks`;
    return `Q${index + 1} · ${question.section} · ${marksLabel}`;
  }, [question, index]);

  const headerRight = useMemo(() => {
    if (!question) return "";
    return `Difficulty ${question.difficulty ?? ""}`.trim();
  }, [question]);

  // ---- Guard: if question is missing, show a helpful message ----
  if (!question) {
    return (
      <div className="card">
        <div className="cardTitle">SEA Study Simulator</div>
        <div className="muted">No question loaded yet. Try starting the paper again.</div>
      </div>
    );
  }

  return (
    <div className="card">
      {/* Header row */}
      <div className="row" style={{ justifyContent: "space-between", gap: 12 }}>
        <div className="muted" style={{ fontWeight: 600 }}>
          {headerLeft}
        </div>
        <div className="muted">{headerRight}</div>
      </div>

      {/* ✅ THIS IS THE FIX: render prompt */}
      <div style={{ marginTop: 10, fontSize: 16, lineHeight: 1.35 }}>
        {question.prompt}
      </div>

      {/* Answer input */}
      <div style={{ marginTop: 14 }}>
        <input
          className="input"
          placeholder="Type your final answer"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
        />
      </div>

      {/* Check button */}
      <div style={{ marginTop: 10, display: "flex", gap: 10, alignItems: "center" }}>
        <button className="btn" onClick={() => onCheck?.(answer, question.correct_answer)}>
          Check
        </button>
        <div className="muted">Attempts: {attempts}</div>
      </div>

      {/* Helper buttons */}
      <div style={{ marginTop: 12, display: "flex", gap: 10, flexWrap: "wrap" }}>
        <button className="btnSecondary" onClick={() => showExample?.(question)}>
          i Example
        </button>
        <button className="btnSecondary" onClick={() => showSteps?.(question)}>
          Show Steps
        </button>
        <button className="btnSecondary" onClick={() => revealSolution?.(question)}>
          Reveal Solution (flags)
        </button>
      </div>

      {/* Footer nav */}
      <div style={{ marginTop: 16, display: "flex", gap: 10 }}>
        <button className="btnSecondary" onClick={() => onPrev?.()} disabled={index <= 0}>
          Previous
        </button>

        <button
          className="btnPrimary"
          onClick={() => onNext?.()}
          disabled={nextLocked}
          title={nextLocked ? "Next is locked until correct (learning mode)" : ""}
        >
          Next (locked by learning)
        </button>

        <div className="muted" style={{ marginLeft: "auto" }}>
          {total ? `${index + 1} / ${total}` : ""}
        </div>
      </div>
    </div>
  );
}
