const timelineSteps = [
  { node: "error_parser", label: "Parsing error" },
  { node: "history_retriever", label: "Searching past incidents" },
  { node: "change_correlator", label: "Checking recent changes" },
  { node: "hypothesis_agent", label: "Generating hypotheses" },
  { node: "report_writer", label: "Writing report" },
];

function StatusIcon({ status }) {
  if (status === "running") return <span className="status-icon spinning" aria-label="Running" />;
  if (status === "complete") return <span className="status-icon check" aria-label="Complete">✓</span>;
  if (status === "warning") return <span className="status-icon warning" aria-label="Warning">▲</span>;
  if (status === "error") return <span className="status-icon error" aria-label="Error">×</span>;
  return <span className="status-icon pending" aria-label="Pending" />;
}

export default function AgentTimeline({ timelineEvents }) {
  return (
    <section className="timeline-panel">
      <h2>Live Agent Timeline</h2>
      <ol className="timeline">
        {timelineSteps.map((step) => {
          const events = timelineEvents.filter((event) => event.node === step.node);
          const latest = events.at(-1);
          const status = latest?.status || "pending";
          return (
            <li key={step.node} className={`timeline-step ${status}`}>
              <StatusIcon status={status} />
              <div>
                <strong>{step.label}</strong>
                {latest?.summary && status !== "running" && (
                  <p>{latest.summary}</p>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
