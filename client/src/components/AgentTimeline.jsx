const STEP_DEFINITIONS = [
  {
    key: "error_parser",
    label: "Parsing error",
    subtitle: "Extracting service, error type, and file paths",
  },
  {
    key: "history_retriever",
    label: "Searching past incidents",
    subtitle: "Finding similar cases in the knowledge base",
  },
  {
    key: "change_correlator",
    label: "Checking recent changes",
    subtitle: "Correlating with GitHub commits in last 48h",
  },
  {
    key: "hypothesis_agent",
    label: "Generating hypotheses",
    subtitle: "Claude reasoning over evidence to rank causes",
  },
  {
    key: "report_writer",
    label: "Writing report",
    subtitle: "Producing the full incident report",
  },
];

function StepIcon({ status }) {
  if (status === "running") {
    return (
      <div className="step-icon icon-running">
        <div className="spinner" />
      </div>
    );
  }
  if (status === "complete") {
    return (
      <div className="step-icon icon-complete">
        <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
          <circle cx="10" cy="10" r="9" fill="currentColor" />
          <path d="M6 10l3 3 5-5" stroke="white" strokeWidth="2" strokeLinecap="round" />
        </svg>
      </div>
    );
  }
  if (status === "warning") {
    return (
      <div className="step-icon icon-warning" aria-label="Warning">
        <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
          <circle cx="10" cy="10" r="9" fill="currentColor" />
          <path d="M10 5v6M10 14v1" stroke="white" strokeWidth="2" strokeLinecap="round" />
        </svg>
      </div>
    );
  }
  if (status === "error") {
    return (
      <div className="step-icon icon-error" aria-label="Error">
        <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
          <circle cx="10" cy="10" r="9" fill="currentColor" />
          <path d="M7 7l6 6m0-6-6 6" stroke="white" strokeWidth="2" strokeLinecap="round" />
        </svg>
      </div>
    );
  }
  return <div className="step-icon icon-pending" />;
}

export default function AgentTimeline({ timelineEvents = [], steps }) {
  const eventMap = timelineEvents.reduce((map, event) => {
    map[event.node] = event;
    return map;
  }, {});

  const renderedSteps = (steps || STEP_DEFINITIONS).map((step) => {
    const key = step.key || step.node;
    const event = eventMap[key];
    return {
      ...step,
      key,
      status: event?.status || step.status || "pending",
      summary: event?.summary || step.summary || "",
    };
  });

  return (
    <section className="timeline-card">
      <h3>Investigating incident...</h3>
      <p>AI agents working in sequence — results appear as each step completes</p>
      {renderedSteps.map((step, index) => (
        <div
          className={`step-row step-${step.status}`}
          key={step.key}
        >
          <div className="step-icon-col">
            <StepIcon status={step.status} />
            {index < renderedSteps.length - 1 && (
              <div
                className={`connector${step.status === "running" ? " connector-active" : ""}`}
              />
            )}
          </div>
          <div className="step-content">
            <h4>{step.label}</h4>
            <p>{step.subtitle}</p>
            {step.summary && step.status !== "running" && (
              <span className="step-badge">{step.summary}</span>
            )}
          </div>
        </div>
      ))}
      <p className="timeline-footer">
        Usually takes 30–90 seconds depending on GitHub correlation.
      </p>
    </section>
  );
}
