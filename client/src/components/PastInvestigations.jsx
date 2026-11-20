import { useEffect, useState } from "react";

const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function PastInvestigations({ onReload }) {
  const [open, setOpen] = useState(false);
  const [sessions, setSessions] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${apiUrl}/api/history`)
      .then((response) => {
        if (!response.ok) throw new Error("Could not load past investigations.");
        return response.json();
      })
      .then(setSessions)
      .catch((requestError) => setError(requestError.message));
  }, []);

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
    <section className="past-investigations">
      <button
        type="button"
        className="collapse-button"
        onClick={() => setOpen((current) => !current)}
        aria-expanded={open}
      >
        Past Investigations {open ? "▲" : "▼"}
      </button>
      {open && (
        <div>
          {error && <p role="alert">{error}</p>}
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
