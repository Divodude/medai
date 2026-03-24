import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
  baseURL: API_URL,
  timeout: 120000, // 2 min for AI analysis
});

export default client;

// ─── API helpers ─────────────────────────────────────────────────────────────

export const analyzeReport = async ({ file, sessionId, lat, lng, city, patientName }) => {
  const formData = new FormData();
  formData.append('file', file);
  if (sessionId) formData.append('session_id', sessionId);
  if (lat != null) formData.append('lat', lat);
  if (lng != null) formData.append('lng', lng);
  if (city) formData.append('city', city);
  if (patientName) formData.append('patient_name', patientName);

  const { data } = await client.post('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
};

export const getHistory = async (sessionId) => {
  const { data } = await client.get(`/history/${sessionId}`);
  return data;
};

export const getAllSessions = async () => {
  const { data } = await client.get('/sessions');
  return data;
};

export const logDiet = async (sessionId, mealName) => {
  await client.post('/log/diet', { session_id: sessionId, meal_name: mealName });
};

export const logExercise = async (sessionId, exerciseName, completed) => {
  await client.post('/log/exercise', {
    session_id: sessionId,
    exercise_name: exerciseName,
    completed,
  });
};

export const searchDoctors = async (specialty, city, sessionId) => {
  const params = { specialty, city };
  if (sessionId) params.session_id = sessionId;
  const { data } = await client.get('/doctors', { params });
  return data.doctors;
};

// Streaming chat — returns a ReadableStream
export const sendChatMessage = async (sessionId, message, analysisContext = null) => {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      analysis_context: analysisContext,
    }),
  });
  return response;
};
