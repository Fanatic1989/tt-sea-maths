export default function Home() {
  return (
    <div className="card">
      <h1 style={{marginTop:0}}>SEA-first Study Mode</h1>
      <p className="muted">
        Trinidad & Tobago Primary (STD 1–5). SEA practice is constructed-response: students work in a notebook and type the final answer.
      </p>
      <div className="row">
        <a className="btn" href="/sea">Start Full SEA Paper (40 questions)</a>
        <a className="btn" href="/sea?mode=section">Section Practice</a>
      </div>
      <hr />
      <h3 style={{margin:'0 0 8px'}}>How it teaches (locked learning)</h3>
      <ul className="muted" style={{lineHeight:1.6}}>
        <li>No skipping in SEA mode.</li>
        <li>After wrong attempts: Hint → Example → Step → (last resort) Reveal Solution.</li>
        <li>Each question can link to a YouTube explanation tied to its skill.</li>
      </ul>
    </div>
  );
}
