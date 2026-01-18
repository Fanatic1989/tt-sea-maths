'use client';

import { useEffect, useMemo, useState } from 'react';
import { fetchSeaPaper } from '../lib/api';
import QuestionCard from '../components/QuestionCard';

function useQueryParam(name, fallback=null) {
  const [val, setVal] = useState(fallback);
  useEffect(() => {
    const url = new URL(window.location.href);
    setVal(url.searchParams.get(name) || fallback);
  }, [name, fallback]);
  return val;
}

function formatTime(sec) {
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  return `${m}:${String(s).padStart(2,'0')}`;
}

export default function SeaPage() {
  const mode = useQueryParam('mode','full');
  const [paper, setPaper] = useState(null);
  const [error, setError] = useState(null);
  const [activeIndex, setActiveIndex] = useState(0);
  const [remaining, setRemaining] = useState(null);

  useEffect(() => {
    (async () => {
      try {
        setError(null);
        const p = await fetchSeaPaper(mode);
        setPaper(p);
        setActiveIndex(0);
        setRemaining(p.duration_sec);
      } catch (e) {
        setError(e.message || 'Failed to load');
      }
    })();
  }, [mode]);

  useEffect(() => {
    if (remaining == null) return;
    if (remaining <= 0) return;
    const t = setInterval(() => setRemaining(r => (r==null?null:Math.max(0, r-1))), 1000);
    return () => clearInterval(t);
  }, [remaining]);

  const q = paper?.questions?.[activeIndex];
  const locked = false; // the question component controls progression

  function unlockNext() {
    setActiveIndex(i => Math.min((paper?.questions?.length || 1) - 1, i + 1));
  }

  if (error) {
    return <div className="card"><strong>Error:</strong> {error}</div>;
  }

  if (!paper) {
    return <div className="card">Loading SEA paper...</div>;
  }

  return (
    <div className="row" style={{alignItems:'flex-start'}}>
      <div style={{flex:2, minWidth:320}}>
        <div className="card" style={{marginBottom:12}}>
          <div className="row" style={{justifyContent:'space-between',alignItems:'center'}}>
            <div>
              <div style={{fontSize:16,fontWeight:800}}>SEA Study Simulator</div>
              <div className="muted" style={{fontSize:12}}>Paper: {paper.paper_id} • Mode: {mode}</div>
            </div>
            <div className="pill" title="75 minutes">⏳ {formatTime(remaining ?? 0)}</div>
          </div>
          <div className="muted" style={{marginTop:10,fontSize:13}}>
            No multiple choice. Work in your notebook, then type the final answer.
          </div>
        </div>

        <QuestionCard
          paperId={paper.paper_id}
          q={q}
          index={activeIndex}
          locked={locked}
          onUnlockNext={unlockNext}
        />

        <div className="row" style={{marginTop:12}}>
          <button className="btn" onClick={() => setActiveIndex(i => Math.max(0, i-1))} disabled={activeIndex===0}>Previous</button>
          <button className="btn" onClick={() => setActiveIndex(i => Math.min(paper.questions.length-1, i+1))} disabled={activeIndex===paper.questions.length-1}>Next (locked by learning)</button>
        </div>
      </div>

      <div style={{flex:1, minWidth:280}}>
        <div className="card">
          <div style={{fontWeight:800, marginBottom:8}}>Question Navigator</div>
          <div className="muted" style={{fontSize:12, marginBottom:10}}>Tap a number to jump (MVP: free jump; later we’ll lock jumps until correct).</div>
          <div className="row" style={{gap:8}}>
            {paper.questions.map((_, i) => (
              <button key={i} className="btn" style={{padding:'6px 10px'}} onClick={() => setActiveIndex(i)}>
                {i+1}
              </button>
            ))}
          </div>
        </div>

        <div className="card" style={{marginTop:12}}>
          <div style={{fontWeight:800}}>YouTube explanations</div>
          <div className="muted" style={{fontSize:12, marginTop:6}}>
            For $0 MVP, videos are mapped per-skill (curated). Add links in the backend later and return them with each question.
          </div>
        </div>
      </div>
    </div>
  );
}
