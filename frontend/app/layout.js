import './globals.css';

export const metadata = {
  title: 'TT SEA Maths Tutor',
  description: 'Primary tutor + SEA Study Simulator (Trinidad & Tobago)',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          <header className="row" style={{justifyContent:'space-between',alignItems:'center'}}>
            <div>
              <div style={{fontSize:18,fontWeight:700}}>TT SEA Maths Tutor</div>
              <div className="muted" style={{fontSize:13}}>SEA Study Simulator • STD 1–5 Tutor</div>
            </div>
            <nav className="row">
              <a className="pill" href="/">Home</a>
              <a className="pill" href="/sea">SEA Simulator</a>
            </nav>
          </header>
          <main style={{marginTop:18}}>{children}</main>
          <footer className="muted" style={{marginTop:28,fontSize:12}}>
            MVP build: auto-generated questions + strict learning. No paid services required.
          </footer>
        </div>
      </body>
    </html>
  );
}
