export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export async function fetchSeaPaper(mode='full') {
  const res = await fetch(`${API_BASE}/sea/paper?mode=${encodeURIComponent(mode)}`, { cache: 'no-store' });
  if (!res.ok) throw new Error('Failed to fetch SEA paper');
  return await res.json();
}

export async function checkAnswer(user_input, correct_answer) {
  const res = await fetch(`${API_BASE}/answer/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input, correct_answer })
  });
  if (!res.ok) throw new Error('Failed to check answer');
  return await res.json();
}

export async function logAttempt(payload) {
  try {
    await fetch(`${API_BASE}/attempt/log`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
  } catch {
    // ignore logging failures in MVP
  }
}
