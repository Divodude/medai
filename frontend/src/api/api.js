const BASE = 'http://localhost:8000';

// ─── Helpers ────────────────────────────────────────────────────────────────

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

async function get(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ─── API Functions ──────────────────────────────────────────────────────────

/**
 * Upload a medical document and run the ETL pipeline.
 * @param {File} file
 * @param {string} sessionId
 * @param {string} patientName
 * @param {string} city
 */
export async function analyzeReport(file, sessionId, patientName, city = '') {
  const form = new FormData();
  form.append('file', file);
  if (sessionId)   form.append('session_id', sessionId);
  if (patientName) form.append('patient_name', patientName);
  if (city)        form.append('city', city);

  const res = await fetch(`${BASE}/analyze`, { method: 'POST', body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

/**
 * Send a chat message. Streams the AI response back, calling onChunk for each piece.
 * @param {string} sessionId
 * @param {string} message
 * @param {(chunk: string) => void} onChunk
 */
export async function sendChat(sessionId, message, onChunk) {
  const res = await fetch(`${BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message }),
  });

  if (!res.ok) throw new Error(`Chat failed: HTTP ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value, { stream: true });
    onChunk(chunk);
  }
}

/** GET /sessions — list all sessions */
export async function listSessions() {
  return get('/sessions');
}

/** GET /history/{session_id} */
export async function getHistory(sessionId) {
  return get(`/history/${sessionId}`);
}

/** POST /log/diet */
export async function logDiet(sessionId, mealName) {
  return post('/log/diet', { session_id: sessionId, meal_name: mealName });
}

/** POST /log/exercise */
export async function logExercise(sessionId, exerciseName, completed = true) {
  return post('/log/exercise', { session_id: sessionId, exercise_name: exerciseName, completed });
}

/**
 * GET /doctors?specialty=&city=&session_id=
 */
export async function searchDoctors(specialty, city, sessionId) {
  const params = new URLSearchParams({ specialty });
  if (city)      params.set('city', city);
  if (sessionId) params.set('session_id', sessionId);
  return get(`/doctors?${params}`);
}

/** GET /pipeline-runs/{session_id} */
export async function getPipelineRuns(sessionId) {
  return get(`/pipeline-runs/${sessionId}`);
}

/** GET all sessions with pipeline runs for admin page */
export async function getAllPipelineRuns() {
  // Fetch all sessions then runs for each
  const sessions = await listSessions();
  const results = await Promise.all(
    sessions.map(async (s) => {
      try {
        const data = await getPipelineRuns(s.id);
        return data.pipeline_runs.map((r) => ({ ...r, patient_name: s.patient_name, session_id: s.id }));
      } catch {
        return [];
      }
    })
  );
  return results.flat().sort((a, b) => new Date(b.started_at) - new Date(a.started_at));
}
