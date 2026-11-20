import { useCallback, useRef, useState } from "react";

const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function useSSE() {
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [finalResult, setFinalResult] = useState(null);
  const [streamError, setStreamError] = useState("");
  const activeRequest = useRef(null);

  const reset = useCallback(() => {
    if (activeRequest.current) activeRequest.current.abort();
    activeRequest.current = null;
    setTimelineEvents([]);
    setFinalResult(null);
    setStreamError("");
  }, []);

  const hydrate = useCallback((detail) => {
    if (activeRequest.current) activeRequest.current.abort();
    activeRequest.current = null;
    setStreamError("");
    setTimelineEvents([
      { node: "error_parser", status: "complete", summary: `${detail.service_name || "Unknown"} / ${detail.error_type || "Unknown"}` },
      { node: "history_retriever", status: "complete", summary: "Historical investigation reloaded." },
      { node: "change_correlator", status: "complete", summary: "Historical change data unavailable." },
      { node: "hypothesis_agent", status: "complete", summary: "Top hypothesis reloaded." },
      { node: "report_writer", status: "complete", summary: "Incident report reloaded." },
    ]);
    setFinalResult({
      session_id: detail.id,
      hypotheses: detail.top_hypothesis_cause
        ? [{
            rank: 1,
            confidence: detail.top_hypothesis_confidence || 0,
            cause: detail.top_hypothesis_cause,
            evidence: "Reloaded from the stored investigation record.",
            fix: "See the incident report for remediation details.",
          }]
        : [],
      report_markdown: detail.report_markdown || "",
      warnings: detail.warnings || [],
    });
  }, []);

  const investigate = useCallback(async (incidentText, repoUrl) => {
    reset();
    const controller = new AbortController();
    activeRequest.current = controller;
    setTimelineEvents([]);
    setFinalResult(null);

    try {
      const response = await fetch(`${apiUrl}/api/investigate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          incident_text: incidentText,
          repo_url: repoUrl,
        }),
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`Investigation failed with status ${response.status}`);
      }
      if (!response.body) {
        throw new Error("Streaming is not supported by this browser.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        let boundary = buffer.indexOf("\n\n");
        while (boundary !== -1) {
          const block = buffer.slice(0, boundary);
          buffer = buffer.slice(boundary + 2);
          const dataLine = block
            .split("\n")
            .find((line) => line.startsWith("data:"));
          if (!dataLine) {
            boundary = buffer.indexOf("\n\n");
            continue;
          }

          try {
            const event = JSON.parse(dataLine.slice(5).trim());
            setTimelineEvents((current) => [...current, event]);
            if (event.status === "completed" && event.data) {
              setFinalResult(event.data);
            }
          } catch {
            setStreamError("Received an invalid event from the server.");
          }
          boundary = buffer.indexOf("\n\n");
        }
      }
    } catch (error) {
      if (error.name !== "AbortError") {
        setStreamError(error.message);
      }
    } finally {
      if (activeRequest.current === controller) activeRequest.current = null;
    }
  }, [reset]);

  return { timelineEvents, finalResult, streamError, investigate, reset, hydrate };
}
