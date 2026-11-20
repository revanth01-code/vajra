import { useState } from "react";

const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function HypothesisCard({ hypothesis, sessionId }) {
  const [rating, setRating] = useState("");
  const [feedbackError, setFeedbackError] = useState("");
  const confidence = Math.round(Number(hypothesis.confidence || 0) * 100);

  async function submitFeedback(value) {
    setFeedbackError("");
    try {
      const response = await fetch(`${apiUrl}/api/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          hypothesis_rank: hypothesis.rank,
          rating: value,
        }),
      });
      if (!response.ok) throw new Error("Could not save feedback.");
      setRating(value);
    } catch (error) {
      setFeedbackError(error.message);
    }
  }

  return (
    <article className={`hypothesis-card rank-${hypothesis.rank}`}>
      <div className="hypothesis-heading">
        <span className="rank">#{hypothesis.rank}</span>
        <span className="confidence-label">{confidence}% confidence</span>
      </div>
      <div className="confidence-bar" aria-label={`${confidence}% confidence`}>
        <span style={{ width: `${confidence}%` }} />
      </div>
      <dl>
        <dt>Cause</dt>
        <dd>{hypothesis.cause}</dd>
        <dt>Evidence</dt>
        <dd>{hypothesis.evidence}</dd>
        <dt>Fix</dt>
        <dd>{hypothesis.fix}</dd>
      </dl>
      <div className="feedback-buttons">
        <button
          type="button"
          className={`thumb-btn thumb-up ${rating === "up" ? "selected" : ""}`}
          onClick={() => submitFeedback("up")}
          aria-label="Thumbs up"
        >
          👍
        </button>
        <button
          type="button"
          className={`thumb-btn thumb-down ${rating === "down" ? "selected" : ""}`}
          onClick={() => submitFeedback("down")}
          aria-label="Thumbs down"
        >
          👎
        </button>
      </div>
      {feedbackError && <p role="alert">{feedbackError}</p>}
    </article>
  );
}
