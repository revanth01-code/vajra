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
  const hypotheses = finalResult?.hypotheses || [];
  const topCause = hypotheses[0]?.cause || "";
  const unavailable =
    /unavailable|failed/i.test(topCause) || /unavailable|failed/i.test(streamError || "");
  const statusText = unavailable
    ? "AI API unavailable — check your API key"
    : "Investigation complete — 3 hypotheses generated";

  return (
    <main className="results-page">
      <div className="breadcrumb">
        <button type="button" onClick={onNewInvestigation}>New Investigation</button>
        <span>› Results</span>
      </div>
      {finalResult && (
        <div
          className={`status-banner ${unavailable ? "status-error" : "status-success"}`}
          role="status"
        >
          {statusText}
        </div>
      )}
      {streamError && <p className="stream-error" role="alert">{streamError}</p>}
      <div className="results-grid">
        <AgentTimeline timelineEvents={timelineEvents} />
        <HypothesisPanel
          timelineEvents={timelineEvents}
          hypotheses={hypotheses}
          sessionId={finalResult?.session_id}
        />
        <IncidentReport
          timelineEvents={timelineEvents}
          markdown={finalResult?.report_markdown || ""}
        />
      </div>
      <div id="past-investigations">
        <PastInvestigations onReload={onReload} />
      </div>
    </main>
  );
}
