import { useState } from "react";

function renderInline(value) {
  return value.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return <code key={index}>{part.slice(1, -1)}</code>;
    }
    return part;
  });
}

function MarkdownText({ markdown }) {
  const blocks = markdown.split("\n");
  return (
    <div className="markdown-report">
      {blocks.map((line, index) => {
        if (line.startsWith("# ")) return <h3 key={index}>{renderInline(line.slice(2))}</h3>;
        if (line.startsWith("## ")) return <h4 key={index}>{renderInline(line.slice(3))}</h4>;
        if (line.startsWith("- ")) return <p key={index}>• {renderInline(line.slice(2))}</p>;
        if (line.startsWith("> ")) return <blockquote key={index}>{renderInline(line.slice(2))}</blockquote>;
        if (!line.trim()) return <br key={index} />;
        return <p key={index}>{renderInline(line)}</p>;
      })}
    </div>
  );
}

export default function IncidentReport({ timelineEvents, markdown }) {
  const [copyStatus, setCopyStatus] = useState("");
  const reportComplete = timelineEvents.some(
    (event) => event.node === "report_writer" && event.status === "complete",
  );
  if (!reportComplete) return null;

  async function copyReport() {
    try {
      await navigator.clipboard.writeText(markdown);
      setCopyStatus("Copied");
    } catch {
      setCopyStatus("Copy failed");
    }
  }

  return (
    <section className="incident-report">
      <div className="report-heading">
        <h2>Incident Report</h2>
        <button type="button" onClick={copyReport}>Copy Report</button>
      </div>
      <MarkdownText markdown={markdown || ""} />
      {copyStatus && <p role="status">{copyStatus}</p>}
    </section>
  );
}
