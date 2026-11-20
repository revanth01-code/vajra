export default function Navbar({ onNewInvestigation, repoUrl }) {
  return (
    <nav className="navbar">
      <span className="navbar-logo">⚡ vajra</span>
      <div className="navbar-links">
        <button className="nav-btn" onClick={onNewInvestigation}>New Investigation</button>
        <button
          className="nav-btn"
          onClick={() =>
            document.getElementById("past-investigations")?.scrollIntoView({
              behavior: "smooth",
            })
          }
        >
          History
        </button>
        <a
          className="nav-btn"
          href="https://github.com/revanth01-code/vajra"
          target="_blank"
          rel="noreferrer"
        >
          GitHub
        </a>
      </div>
    </nav>
  );
}
