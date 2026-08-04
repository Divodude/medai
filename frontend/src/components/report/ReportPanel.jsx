import { useApp } from '../../context/AppContext.jsx';
import SummarySection from './SummarySection.jsx';
import KeyFindingsSection from './KeyFindingsSection.jsx';
import ProfileSection from './ProfileSection.jsx';
import DietSection from './DietSection.jsx';
import ExerciseSection from './ExerciseSection.jsx';
import RemediesSection from './RemediesSection.jsx';
import DoctorsSection from './DoctorsSection.jsx';

export default function ReportPanel() {
  const { state } = useApp();
  const { analysis, reportOpen } = state;

  if (!analysis) return null;

  return (
    <div className={`report-panel-wrapper${reportOpen ? ' open' : ''}`}>
      <div className="report-panel">
        {/* Condition header */}
        <div className="condition-header">
          <span className="condition-name">{analysis.condition}</span>
          <span className={`severity-badge severity-${analysis.severity}`}>
            {analysis.severity === 'HIGH'   ? '🔴' :
             analysis.severity === 'MEDIUM' ? '🟡' : '🟢'} {analysis.severity}
          </span>
          {analysis.specialty && (
            <span className="specialty-tag">👨‍⚕️ {analysis.specialty}</span>
          )}
        </div>

        <SummarySection     analysis={analysis} />
        <KeyFindingsSection analysis={analysis} />
        <ProfileSection     analysis={analysis} />
        <DietSection        analysis={analysis} />
        <ExerciseSection    analysis={analysis} />
        <RemediesSection    analysis={analysis} />
        <DoctorsSection     analysis={analysis} />
      </div>
    </div>
  );
}
