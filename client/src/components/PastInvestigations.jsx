import { useCallback, useEffect, useState } from "react";

const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function PastInvestigations({ onReload }) {
  const [open, setOpen] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [error, setError] = useState("");
  const [hasLoaded, setHasLoaded] = useState(false);

  const loadHistory = useCallback(() => {
    console.log(`Fetching history from ${apiUrl}/api/history`);
    setError("");
    fetch(`${apiUrl}/api/history`)
      .then((response) => {
        if (!response.ok) throw new Error("Could not load past investigations.");
        return response.json();
      })
      .then((items) => {
        setSessions(items);
        setHasLoaded(true);
      })
      .catch(() => setError("Could not load history"));
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  function togglePanel() {
    setOpen((current) => {
      const next = !current;
      if (next && !hasLoaded) loadHistory();
      return next;
    });
  }

  async function reload(sessionId) {
    try {
      const response = await fetch(`${apiUrl}/api/history/${sessionId}`);
      if (!response.ok) throw new Error("Could not reload this investigation.");
      const detail = await response.json();
      onReload(detail);
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  return (
    <section id="past-investigations" className="past-investigations">
      <button
        type="button"
        className={`collapse-button ${open ? "open" : ""}`}
        onClick={togglePanel}
        aria-expanded={open}
      >
        Past Investigations {open ? "▲" : "▼"}
      </button>
      {open && (
        <div>
          {error && <p className="past-history-error" role="alert">{error}</p>}
          {sessions.length === 0 && !error && <p>No investigations yet.</p>}
          {sessions.map((session) => (
            <article key={session.id} className="past-session">
              <div>
                <strong>{session.service_name || "Unknown service"}</strong>
                <span>{new Date(session.created_at).toLocaleString()}</span>
                <p>{session.top_hypothesis_cause || "No hypothesis recorded"}</p>
              </div>
              <button type="button" onClick={() => reload(session.id)}>
                Reload
              </button>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
