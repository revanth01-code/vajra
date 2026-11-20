import { useState } from "react";

export default function InputView({ onInvestigate }) {
  const [incidentText, setIncidentText] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [repoError, setRepoError] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    if (!incidentText.trim()) return;
    onInvestigate(incidentText, repoUrl.trim() || null);
  }

  function handleRepoBlur() {
    const value = repoUrl.trim();
    if (value && !value.startsWith("https://github.com/")) {
      setRepoError("Must be a full GitHub repository URL");
      setRepoUrl("");
    } else {
      setRepoError("");
    }
  }

  return (
    <main className="input-page">
      <div className="input-hero">
        <h1>vajra</h1>
        <p>Agentic production incident investigator</p>
      </div>

      <div className="stats-row">
        <div className="stat-card">
          <span className="stat-value">&lt; 90s</span>
          <span className="stat-label">Mean time to hypothesis</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">5</span>
          <span className="stat-label">AI agents in sequence</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">20+</span>
          <span className="stat-label">Incident patterns in KB</span>
        </div>
      </div>

      <div className="kb-section">
        <p className="kb-label">Knowledge base covers</p>
        <div className="kb-tags">
          {[
            "Database Connection Pool",
            "Memory Leak",
            "Redis Timeout",
            "API Rate Limit",
            "Auth Token Expiry",
            "Config Deployment Error",
            "Disk Space Exhaustion",
            "Network Partition",
            "Cascading Failure",
            "Third-party Outage",
            "OOM Kill",
            "SSL Certificate",
            "DNS Resolution",
            "Queue Backlog",
            "Cold Start Latency",
          ].map((tag) => (
            <span className="kb-tag" key={tag}>{tag}</span>
          ))}
        </div>
      </div>

      <form className="input-form" onSubmit={handleSubmit}>
        <div>
          <label className="form-label" htmlFor="incident-text">
            Paste your error log, stack trace, or describe the incident
          </label>
          <textarea
            className="form-textarea"
            id="incident-text"
            value={incidentText}
            onChange={(event) => setIncidentText(event.target.value)}
            maxLength={10000}
            required
          />
        </div>

        <div>
          <div className="label-row">
            <label className="form-label" htmlFor="repo-url">
              GitHub Repository (optional)
            </label>
            <span
              className="info-icon"
              data-tooltip="Paste your repo URL to correlate the incident with recent commits. Example: https://github.com/your-org/your-repo"
              tabIndex={0}
              aria-label="GitHub repository help"
            >
              ⓘ
            </span>
          </div>
          <input
            className="form-input"
            id="repo-url"
            type="url"
            value={repoUrl}
            onChange={(event) => {
              setRepoUrl(event.target.value);
              if (repoError) setRepoError("");
            }}
            onBlur={handleRepoBlur}
            placeholder="https://github.com/your-org/your-repo"
          />
          {repoError && <span className="field-error">{repoError}</span>}
        </div>

        <button className="submit-btn" type="submit" disabled={!incidentText.trim()}>
          Investigate
        </button>
        <p className="privacy-note">
          Processed by open-source AI. Your data is never stored externally.
        </p>
      </form>
    </main>
  );
}
