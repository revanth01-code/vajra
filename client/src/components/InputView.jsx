import { useState } from "react";

export default function InputView({ onInvestigate }) {
  const [incidentText, setIncidentText] = useState("");
  const [repoUrl, setRepoUrl] = useState("");

  function handleSubmit(event) {
    event.preventDefault();
    if (!incidentText.trim()) return;
    onInvestigate(incidentText, repoUrl.trim() || null);
  }

  return (
    <main className="input-view">
      <h1>IncidentSense</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="incident-text">
          Paste your error log, stack trace, or describe the incident
        </label>
        <textarea
          id="incident-text"
          value={incidentText}
          onChange={(event) => setIncidentText(event.target.value)}
          maxLength={10000}
          rows={12}
          required
        />

        <label htmlFor="repo-url">GitHub repo URL (optional)</label>
        <input
          id="repo-url"
          type="url"
          value={repoUrl}
          onChange={(event) => setRepoUrl(event.target.value)}
          placeholder="https://github.com/owner/repository"
        />

        <button type="submit" disabled={!incidentText.trim()}>
          Investigate
        </button>
        <p className="privacy-note">
          Anthropic does not retain prompt or completion data on the standard API tier.
          Sanitized investigations are stored locally in SQLite for history.
        </p>
      </form>
    </main>
  );
}
