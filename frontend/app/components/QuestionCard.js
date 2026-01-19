"use client";

import { useEffect, useMemo, useState } from "react";

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
  disabled = false, // ✅ new
}) {
  const [answer, setAnswer] = useState("");

  // ✅ Reset answer whenever the question changes
  useEffect(() => {
    setAnswer("");
  }, [question?.question_id]);

  const headerLeft = useMemo(() => {
    if (!question) return "";
    const marksLabel = question.marks === 1 ? "1 mark" : `${question.marks} marks`;
    return `Q${index + 1} · ${question.section} · ${marksLabel}`;
  }, [question, index]);

  const headerRight = useMemo(() => {
    if (!question) return "";
    return `Difficulty ${question.difficulty ?? ""}`.trim();
  }, [question]);

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
      <div className="row" style={{ justifyContent: "space-between", gap: 12 }}>
        <div className="muted" style={{ fontWeight: 600 }}>
          {headerLeft}
        </div>
        <div className="muted">{headerRight}</div>
      </div>

      <div style={{ marginTop: 10, fontSize: 16, lineHeight: 1.35, whiteSpace: "pre-wrap" }}>
        {question.prompt}
      </div>

      <div style={{ marginTop: 14 }}>
        <input
          className="input"
          placeholder={disabled ? "Paper locked (time up)" : "Type your final answer"}
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          disabled={disabled}
        />
      </div>

      <div style={{ marginTop: 10, display: "flex", gap: 10, alignItems: "center" }}>
        <button
          className="btn"
          onClick={() => onCheck?.(answer, question.correct_answer)}
          disabled={disabled || !answer.trim()}
        >
          Check
        </button>
        <div className="muted">Attempts: {attempts}</div>
      </div>

      <div style={{ marginTop: 12, display: "flex", gap: 10, flexWrap: "wrap" }}>
        <button className="btnSecondary" onClick={() => showExample?.(question)} disabled={disabled}>
          i Example
        </button>
        <button className="btnSecondary" onClick={() => showSteps?.(question)} disabled={disabled}>
          Show Steps
        </button>
        {/* ✅ Reveal Solution REMOVED */}
      </div>

      <div style={{ marginTop: 16, display: "flex", gap: 10 }}>
        <button className="btnSecondary" onClick={() => onPrev?.()} disabled={disabled || index <= 0}>
          Previous
        </button>

        <button
          className="btnPrimary"
          onClick={() => onNext?.()}
          disabled={disabled || nextLocked}
          title={
            disabled
              ? "Paper locked (time up)"
              : nextLocked
              ? "Next is locked until correct (learning mode)"
              : ""
          }
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
