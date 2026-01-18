import { useMemo, useState } from 'react';
import { checkAnswer, logAttempt } from '../lib/api';

function makeSessionId() {
  if (typeof window === 'undefined') return 'server';
  const key = 'tt_sea_session_id';
  let v = localStorage.getItem(key);
  if (!v) {
    v = `sess_${Math.random().toString(16).slice(2)}_${Date.now()}`;
    localStorage.setItem(key, v);
  }
  return v;
}

export default function QuestionCard({ paperId, q, index, locked, onUnlockNext }) {
  const sessionId = useMemo(() => makeSessionId(), []);
  const [input, setInput] = useState('');
  const [status, setStatus] = useState(null); // 'correct' | 'wrong'
  const [feedback, setFeedback] = useState('');
  const [attempts, setAttempts] = useState(0);
  const [helpLevel, setHelpLevel] = useState(0);
  const [showExample, setShowExample] = useState(false);
  const [showSteps, setShowSteps] = useState(false);
  const [revealed, setRevealed] = useState(false);

  async function onCheck() {
    const nextAttempts = attempts + 1;
    setAttempts(nextAttempts);
    const res = await checkAnswer(input, q.correct_answer);
    setStatus(res.is_correct ? 'correct' : 'wrong');
    setFeedback(res.feedback || (res.is_correct ? 'Correct!' : 'Try again'));

    // escalate help automatically (no skipping)
    let nextHelp = helpLevel;
    if (!res.is_correct) {
      if (nextAttempts === 2) nextHelp = Math.max(nextHelp, 1);
      if (nextAttempts === 3) nextHelp = Math.max(nextHelp, 2);
      if (nextAttempts === 4) nextHelp = Math.max(nextHelp, 3);
    }
    setHelpLevel(nextHelp);

    await logAttempt({
      session_id: sessionId,
      paper_id: paperId,
      question_id: q.question_id,
      entered_answer: input,
      is_correct: !!res.is_correct,
      attempt_count: nextAttempts,
      hint_level_used: nextHelp,
      used_example: showExample,
      used_tutor: false,
      used_show_step: showSteps,
      used_reveal_solution: revealed,
      time_spent_sec: 0
    });

    if (res.is_correct) {
      onUnlockNext();
    }
  }

  function hintText(level) {
    if (level <= 0) return null;
    if (level === 1) return 'Hint 1: Read the question carefully and choose the correct operation.';
    if (level === 2) return 'Hint 2: Use the rule in the Example panel (ⓘ) and set up your working.';
    return 'Hint 3: Use “Show Steps” to compare with your working, then try again.';
  }

  const yt = q.youtube_url || null;

  return (
    <div className="card" style={{opacity: locked ? 0.6 : 1}}>
      <div className="row" style={{justifyContent:'space-between',alignItems:'center'}}>
        <div className="pill">Q{index + 1} • Section {q.section} • {q.marks} mark{q.marks>1?'s':''}</div>
        <div className="muted" style={{fontSize:12}}>Difficulty {q.difficulty}</div>
      </div>

      <h3 style={{margin:'12px 0 8px'}}>{q.prompt_text}</h3>

      <div className="row" style={{alignItems:'center'}}>
        <input
          className="input"
          placeholder="Type your final answer"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={locked}
        />
        <button className="btn" onClick={onCheck} disabled={locked || !input.trim()}>Check</button>
      </div>

      {feedback && (
        <div style={{marginTop:10}} className={status === 'correct' ? '' : 'muted'}>
          <strong>{status === 'correct' ? '✅ ' : '❌ '}</strong>{feedback}
        </div>
      )}

      {hintText(helpLevel) && (
        <div style={{marginTop:10}} className="muted">{hintText(helpLevel)}</div>
      )}

      <div className="row" style={{marginTop:12}}>
        <button className="btn" onClick={() => setShowExample(v => !v)} disabled={locked}>ⓘ Example</button>
        <button className="btn" onClick={() => setShowSteps(v => !v)} disabled={locked}>Show Steps</button>
        <button
          className="btn"
          onClick={() => { setRevealed(true); setShowSteps(true); onUnlockNext(); }}
          disabled={locked}
        >Reveal Solution (flags)</button>
        {yt && (
          <a className="btn" href={yt} target="_blank" rel="noreferrer">📺 Explanation</a>
        )}
      </div>

      {showExample && (
        <div style={{marginTop:12}} className="card">
          <div style={{fontWeight:700}}>Example</div>
          <div className="muted" style={{marginTop:6}}>{q.example_help?.rule || 'Rule: Use the method shown in steps.'}</div>
          <div style={{marginTop:8}} className="muted">
            {(q.example_help?.examples || []).slice(0,1).map((ex, i) => (
              <div key={i}>
                <div><strong>{ex.prompt}</strong></div>
                <ul>
                  {(ex.steps || []).map((s, j) => <li key={j}>{s}</li>)}
                </ul>
                <div><strong>Answer:</strong> {ex.answer}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {showSteps && (
        <div style={{marginTop:12}} className="card">
          <div style={{fontWeight:700}}>Working / Steps</div>
          <ol className="muted" style={{marginTop:8,lineHeight:1.6}}>
            {(q.solution_steps || []).map((s) => (
              <li key={s.step}><strong>{s.title}:</strong> {s.work}</li>
            ))}
          </ol>
          {revealed && (
            <div className="muted" style={{fontSize:12}}>This question was completed using Reveal Solution.</div>
          )}
        </div>
      )}

      <div className="muted" style={{marginTop:10,fontSize:12}}>
        Attempts: {attempts} • No skipping in SEA mode
      </div>
    </div>
  );
}
