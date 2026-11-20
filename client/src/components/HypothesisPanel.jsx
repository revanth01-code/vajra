import HypothesisCard from "./HypothesisCard.jsx";

export default function HypothesisPanel({ timelineEvents, hypotheses, sessionId }) {
  const hypothesisComplete = timelineEvents.some(
    (event) =>
      event.node === "hypothesis_agent" && event.status === "complete",
  );
  if (!hypothesisComplete) return null;

  return (
    <section className="hypothesis-panel">
      <h2>Root Cause Hypotheses</h2>
      <div className="hypothesis-list">
        {hypotheses.slice(0, 3).map((hypothesis) => (
          <HypothesisCard
            key={hypothesis.rank}
            hypothesis={hypothesis}
            sessionId={sessionId}
          />
        ))}
      </div>
    </section>
  );
}
