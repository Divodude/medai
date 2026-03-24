import React, { useState } from 'react';
import UploadZone from '../components/UploadZone';
import InlineChat from '../components/InlineChat';
import DietCard from '../components/DietCard';
import ExerciseCard from '../components/ExerciseCard';
import RemedyCard from '../components/RemedyCard';
import DoctorCard from '../components/DoctorCard';
import ProgressRing from '../components/ProgressRing';
import useHealthStore from '../store/useHealthStore';
import { searchDoctors } from '../api/client';
import { Stethoscope, Salad, Dumbbell, Leaf, AlertCircle, MapPin, Loader2 } from 'lucide-react';

const SEVERITY_COLORS = {
  LOW: 'var(--teal)',
  MEDIUM: 'var(--amber)',
  HIGH: 'var(--red)',
};

function SectionHeader({ icon: Icon, title, color, children }) {
  return (
    <div className="section-header">
      <Icon size={20} color={color} />
      <h2 className="section-title" style={{ color }}>{title}</h2>
      {children}
    </div>
  );
}

export default function Dashboard() {
  const { analysisResult, completedExercises, loggedMeals, sessionId, userLocation, setUserLocation } = useHealthStore();
  const [doctors, setDoctors] = useState(analysisResult?.nearby_doctors || []);
  const [loadingDocs, setLoadingDocs] = useState(false);

  const fetchDoctors = async () => {
    if (!analysisResult?.specialty) return;
    setLoadingDocs(true);
    try {
      let city = userLocation || '';
      if (!city && navigator.geolocation) {
        await new Promise((res) => {
          navigator.geolocation.getCurrentPosition(async (pos) => {
            try {
              const r = await fetch(
                `https://nominatim.openstreetmap.org/reverse?lat=${pos.coords.latitude}&lon=${pos.coords.longitude}&format=json`
              );
              const d = await r.json();
              city = d.address?.city || d.address?.town || '';
              if (city) setUserLocation(city);
            } catch (_) { }
            res();
          }, res);
        });
      }
      const results = await searchDoctors(analysisResult.specialty, city, sessionId);
      setDoctors(results);
    } finally {
      setLoadingDocs(false);
    }
  };

  const totalEx = (analysisResult?.exercise_plan || []).length;
  const doneEx = totalEx > 0 ? Object.values(completedExercises).filter(Boolean).length : 0;
  const totalMeals = (analysisResult?.diet_plan || []).length;
  const doneMeals = totalMeals > 0 ? Object.values(loggedMeals).filter(Boolean).length : 0;

  return (
    <div className="dashboard">

      {/* ── Hero: Upload + Chat side by side ────────────────────── */}
      <section className="hero-section-v2">
        <div className="hero-left">
          <h1 className="hero-title">Your AI Health Assistant</h1>
          <p className="hero-sub">
            Upload a medical report to get a personalised plan, or simply chat with the AI about your health.
          </p>
          <UploadZone />
        </div>
        <InlineChat />
      </section>

      {/* ── Analysis result banner ───────────────────────────────── */}
      {analysisResult && (
        <div
          className="analysis-banner"
          style={{ '--severity-color': SEVERITY_COLORS[analysisResult.severity] || 'var(--teal)' }}
        >
          <AlertCircle size={18} color={SEVERITY_COLORS[analysisResult.severity]} />
          <div className="banner-text">
            <strong>{analysisResult.condition}</strong>
            <span className="severity-pill" style={{ background: SEVERITY_COLORS[analysisResult.severity] }}>
              {analysisResult.severity}
            </span>
          </div>
          <p className="banner-summary">{analysisResult.summary}</p>
          {analysisResult.key_findings?.length > 0 && (
            <ul className="findings-list">
              {analysisResult.key_findings.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
          )}
        </div>
      )}

      {/* ── Progress rings ───────────────────────────────────────── */}
      {analysisResult && (
        <div className="progress-section">
          <ProgressRing value={doneEx} total={totalEx} size={80} label="Exercises" />
          <ProgressRing value={doneMeals} total={totalMeals} size={80} label="Meals" />
        </div>
      )}

      {/* ── Diet plan ────────────────────────────────────────────── */}
      {analysisResult?.diet_plan?.length > 0 && (
        <section className="cards-section">
          <SectionHeader icon={Salad} title="Diet Plan" color="var(--teal)" />
          <div className="cards-grid">
            {analysisResult.diet_plan.map((m, i) => <DietCard key={i} meal={m} />)}
          </div>
        </section>
      )}

      {/* ── Exercise plan ─────────────────────────────────────────── */}
      {analysisResult?.exercise_plan?.length > 0 && (
        <section className="cards-section">
          <SectionHeader icon={Dumbbell} title="Exercise Plan" color="var(--amber)" />
          <div className="cards-grid">
            {analysisResult.exercise_plan.map((e, i) => <ExerciseCard key={i} exercise={e} />)}
          </div>
        </section>
      )}

      {/* ── Home remedies ─────────────────────────────────────────── */}
      {analysisResult?.home_remedies?.length > 0 && (
        <section className="cards-section">
          <SectionHeader icon={Leaf} title="Home Remedies" color="var(--green)" />
          <div className="cards-grid">
            {analysisResult.home_remedies.map((r, i) => <RemedyCard key={i} remedy={r} />)}
          </div>
        </section>
      )}

      {/* ── Nearby doctors ───────────────────────────────────────── */}
      {analysisResult && (
        <section className="cards-section">
          <SectionHeader icon={Stethoscope} title={`Nearby ${analysisResult.specialty ? `${analysisResult.specialty}s` : 'Doctors'}`} color="var(--violet)">
            <button className="refresh-btn" onClick={fetchDoctors} disabled={loadingDocs}>
              {loadingDocs ? <Loader2 size={14} className="spin" /> : <MapPin size={14} />}
              {loadingDocs ? 'Searching…' : 'Find Near Me'}
            </button>
          </SectionHeader>
          {doctors.length > 0 ? (
            <div className="cards-grid">
              {doctors.map((d, i) => <DoctorCard key={i} doctor={d} />)}
            </div>
          ) : (
            !loadingDocs && <p className="empty-hint">Click "Find Near Me" to search for nearby doctors.</p>
          )}
        </section>
      )}
    </div>
  );
}
