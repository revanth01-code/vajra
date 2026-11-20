import { useState } from "react";

import InputView from "./components/InputView.jsx";
import ResultsView from "./components/ResultsView.jsx";
import Navbar from "./components/Navbar.jsx";
import useSSE from "./hooks/useSSE.js";

export default function App() {
  const [view, setView] = useState("input");
  const { timelineEvents, finalResult, streamError, investigate, reset, hydrate } = useSSE();

  async function startInvestigation(incidentText, repoUrl) {
    setView("results");
    await investigate(incidentText, repoUrl);
  }

  function newInvestigation() {
    reset();
    setView("input");
  }

  function reloadInvestigation(detail) {
    hydrate(detail);
    setView("results");
  }

  return (
    <>
      <Navbar onNewInvestigation={newInvestigation} />
      {view === "input" ? (
        <InputView onInvestigate={startInvestigation} />
      ) : (
        <ResultsView
          timelineEvents={timelineEvents}
          finalResult={finalResult}
          streamError={streamError}
          onNewInvestigation={newInvestigation}
          onReload={reloadInvestigation}
        />
      )}
    </>
  );
}
