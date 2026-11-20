import AgentTimeline from "./AgentTimeline.jsx";
import HypothesisPanel from "./HypothesisPanel.jsx";
import IncidentReport from "./IncidentReport.jsx";
import PastInvestigations from "./PastInvestigations.jsx";

export default function ResultsView({
  timelineEvents,
  finalResult,
  streamError,
  onNewInvestigation,
  onReload,
}) {
  return (
    <main className="results-view">
      {streamError && <p className="stream-error" role="alert">{streamError}</p>}
      <div className="results-grid">
        <AgentTimeline timelineEvents={timelineEvents} />
        <HypothesisPanel
          timelineEvents={timelineEvents}
          hypotheses={finalResult?.hypotheses || []}
          sessionId={finalResult?.session_id}
        />
        <IncidentReport
          timelineEvents={timelineEvents}
          markdown={finalResult?.report_markdown || ""}
        />
      </div>
      <button
        type="button"
        className="new-investigation"
        onClick={onNewInvestigation}
      >
        New Investigation
      </button>
      <PastInvestigations onReload={onReload} />
    </main>
  );
}
