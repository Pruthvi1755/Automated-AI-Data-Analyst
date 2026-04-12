import { useState, useCallback, useRef, useEffect } from "react";
import Plotly from "plotly.js-dist-min";

// ── Inline styles & CSS vars ────────────────────────────────────────────────
const CSS = `
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Syne:wght@400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg0: #050810;
  --bg1: #080d1a;
  --bg2: #0d1425;
  --bg3: #111a30;
  --bg4: #162038;
  --cyan: #22d3ee;
  --cyan-dim: rgba(34,211,238,0.15);
  --cyan-border: rgba(34,211,238,0.25);
  --blue: #3b82f6;
  --violet: #8b5cf6;
  --pink: #f472b6;
  --green: #10b981;
  --amber: #f59e0b;
  --red: #ef4444;
  --text0: #f0f4ff;
  --text1: #cbd5e1;
  --text2: #64748b;
  --text3: #334155;
  --border: rgba(255,255,255,0.06);
  --radius: 12px;
  --radius-lg: 18px;
  --shadow: 0 8px 32px rgba(0,0,0,0.5);
}

html, body { background: var(--bg0); color: var(--text0); font-family: 'Syne', sans-serif; height: 100%; overflow-x: hidden; }

#root { min-height: 100vh; }

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg1); }
::-webkit-scrollbar-thumb { background: var(--bg4); border-radius: 2px; }

.mono { font-family: 'DM Mono', monospace; }

/* Layout */
.app { display: flex; min-height: 100vh; }
.sidebar { width: 280px; min-width: 280px; background: var(--bg1); border-right: 1px solid var(--border); display: flex; flex-direction: column; overflow-y: auto; }
.main { flex: 1; overflow-y: auto; }

/* Sidebar */
.sidebar-logo { padding: 24px 20px 20px; border-bottom: 1px solid var(--border); }
.logo-text { font-size: 18px; font-weight: 800; letter-spacing: -0.03em; }
.logo-glyph { font-family: 'DM Mono', monospace; color: var(--cyan); }
.logo-sub { font-size: 10px; color: var(--text2); font-family: 'DM Mono', monospace; letter-spacing: 0.12em; text-transform: uppercase; margin-top: 3px; }

.sidebar-section { padding: 16px 20px; border-bottom: 1px solid var(--border); }
.sidebar-label { font-size: 10px; font-family: 'DM Mono', monospace; letter-spacing: 0.14em; text-transform: uppercase; color: var(--text2); margin-bottom: 10px; }

/* Upload zone */
.upload-zone { border: 2px dashed var(--bg4); border-radius: var(--radius); padding: 24px 16px; text-align: center; cursor: pointer; transition: all 0.2s; position: relative; overflow: hidden; }
.upload-zone:hover, .upload-zone.dragging { border-color: var(--cyan); background: var(--cyan-dim); }
.upload-zone input { position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%; }
.upload-icon { font-size: 28px; margin-bottom: 8px; }
.upload-text { font-size: 12px; color: var(--text1); font-family: 'DM Mono', monospace; }
.upload-sub { font-size: 10px; color: var(--text2); margin-top: 4px; }

/* Dataset info */
.dataset-info { background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius); padding: 12px; }
.dataset-name { font-size: 12px; font-weight: 600; color: var(--cyan); font-family: 'DM Mono', monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.dataset-meta { display: flex; gap: 12px; margin-top: 6px; }
.meta-chip { font-size: 10px; color: var(--text2); font-family: 'DM Mono', monospace; }

/* Schema tags */
.schema-group { margin-top: 8px; }
.schema-group-label { font-size: 9px; font-family: 'DM Mono', monospace; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text3); margin-bottom: 4px; }
.tags { display: flex; flex-wrap: wrap; gap: 4px; }
.tag { font-size: 9px; font-family: 'DM Mono', monospace; padding: 2px 7px; border-radius: 4px; white-space: nowrap; max-width: 120px; overflow: hidden; text-overflow: ellipsis; }
.tag-num { background: rgba(34,211,238,0.1); color: var(--cyan); border: 1px solid rgba(34,211,238,0.2); }
.tag-cat { background: rgba(139,92,246,0.1); color: var(--violet); border: 1px solid rgba(139,92,246,0.2); }
.tag-dt  { background: rgba(244,114,182,0.1); color: var(--pink); border: 1px solid rgba(244,114,182,0.2); }

/* History */
.history-list { display: flex; flex-direction: column; gap: 6px; }
.history-item { background: var(--bg2); border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px; cursor: pointer; transition: all 0.15s; }
.history-item:hover { border-color: var(--cyan-border); background: var(--bg3); }
.history-q { font-size: 11px; color: var(--text1); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.4; }
.history-meta { display: flex; justify-content: space-between; margin-top: 3px; }
.history-intent { font-size: 9px; font-family: 'DM Mono', monospace; color: var(--cyan); text-transform: uppercase; }
.history-time { font-size: 9px; font-family: 'DM Mono', monospace; color: var(--text3); }

/* Main content */
.main-inner { max-width: 1100px; margin: 0 auto; padding: 32px 32px 80px; }

/* Header */
.page-header { margin-bottom: 32px; }
.page-title { font-size: 32px; font-weight: 800; letter-spacing: -0.04em; line-height: 1.1; }
.page-title span { background: linear-gradient(90deg, var(--cyan), var(--blue), var(--violet)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.page-sub { font-size: 13px; color: var(--text2); font-family: 'DM Mono', monospace; margin-top: 6px; }

/* Stat cards */
.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 28px; }
.stat-card { background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; }
.stat-value { font-size: 26px; font-weight: 800; font-family: 'DM Mono', monospace; color: var(--cyan); letter-spacing: -0.04em; }
.stat-label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--text2); margin-top: 4px; }

/* Query section */
.query-section { background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 24px; margin-bottom: 28px; }
.query-label { font-size: 11px; font-family: 'DM Mono', monospace; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text2); margin-bottom: 12px; }
.query-input-wrap { position: relative; }
.query-input { width: 100%; background: var(--bg1); border: 1.5px solid var(--bg4); border-radius: 10px; padding: 14px 16px; color: var(--text0); font-family: 'Syne', sans-serif; font-size: 15px; resize: none; outline: none; transition: border-color 0.2s; }
.query-input:focus { border-color: var(--cyan); box-shadow: 0 0 0 3px rgba(34,211,238,0.1); }
.query-input::placeholder { color: var(--text3); }
.query-actions { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; }

/* Suggestions */
.suggestions { display: flex; flex-wrap: wrap; gap: 6px; }
.suggestion-chip { background: var(--bg3); border: 1px solid var(--border); border-radius: 6px; padding: 4px 10px; font-size: 11px; font-family: 'DM Mono', monospace; color: var(--text1); cursor: pointer; transition: all 0.15s; white-space: nowrap; }
.suggestion-chip:hover { border-color: var(--cyan-border); color: var(--cyan); background: var(--cyan-dim); }

/* Buttons */
.btn-primary { background: linear-gradient(135deg, var(--cyan), var(--blue)); color: var(--bg0); font-family: 'DM Mono', monospace; font-weight: 500; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; border: none; border-radius: 8px; padding: 10px 24px; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(34,211,238,0.3); }
.btn-primary:disabled { opacity: 0.4; cursor: not-allowed; transform: none; box-shadow: none; }
.btn-ghost { background: transparent; border: 1px solid var(--border); color: var(--text1); font-family: 'DM Mono', monospace; font-size: 11px; border-radius: 7px; padding: 7px 14px; cursor: pointer; transition: all 0.15s; }
.btn-ghost:hover { border-color: var(--cyan-border); color: var(--cyan); }

/* Intent badge */
.intent-badge { display: inline-flex; align-items: center; gap: 5px; background: var(--cyan-dim); border: 1px solid var(--cyan-border); color: var(--cyan); font-family: 'DM Mono', monospace; font-size: 10px; font-weight: 500; letter-spacing: 0.1em; text-transform: uppercase; padding: 3px 10px; border-radius: 999px; }
.intent-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--cyan); animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.3;} }

/* Result section */
.result-section { background: var(--bg2); border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; margin-bottom: 24px; }
.result-header { padding: 16px 24px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
.result-body { padding: 24px; }
.result-raw { font-family: 'DM Mono', monospace; font-size: 12px; color: var(--text1); background: var(--bg1); border: 1px solid var(--border); border-radius: 8px; padding: 14px 16px; line-height: 1.7; white-space: pre-wrap; word-break: break-word; margin-bottom: 20px; }

/* Insight */
.insight-box { background: linear-gradient(135deg, rgba(34,211,238,0.05), rgba(59,130,246,0.05)); border: 1px solid rgba(34,211,238,0.15); border-radius: 10px; padding: 16px 20px; }
.insight-label { font-size: 9px; font-family: 'DM Mono', monospace; letter-spacing: 0.14em; text-transform: uppercase; color: var(--cyan); margin-bottom: 8px; }
.insight-text { font-size: 14px; color: var(--text1); line-height: 1.7; }
.insight-text strong { color: var(--text0); }

/* Chart */
.chart-container { background: var(--bg1); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; margin: 20px 0; }
.chart-title { padding: 12px 16px; font-size: 11px; font-family: 'DM Mono', monospace; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text2); border-bottom: 1px solid var(--border); }

/* Tabs */
.tabs { display: flex; gap: 2px; background: var(--bg1); border-radius: 10px; padding: 4px; margin-bottom: 20px; }
.tab { padding: 7px 16px; font-size: 12px; font-family: 'DM Mono', monospace; border-radius: 7px; cursor: pointer; color: var(--text2); border: none; background: transparent; transition: all 0.15s; }
.tab.active { background: var(--bg3); color: var(--text0); }

/* Table */
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 12px; font-family: 'DM Mono', monospace; }
thead tr { border-bottom: 1px solid var(--border); }
th { padding: 10px 12px; text-align: left; color: var(--text2); font-weight: 500; font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; white-space: nowrap; }
td { padding: 9px 12px; color: var(--text1); border-bottom: 1px solid rgba(255,255,255,0.03); white-space: nowrap; max-width: 160px; overflow: hidden; text-overflow: ellipsis; }
tr:hover td { background: rgba(255,255,255,0.02); }

/* Empty state */
.empty-state { text-align: center; padding: 60px 20px; }
.empty-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.4; }
.empty-title { font-size: 20px; font-weight: 700; color: var(--text1); margin-bottom: 8px; }
.empty-sub { font-size: 13px; color: var(--text2); font-family: 'DM Mono', monospace; }

/* Loading */
.loading-overlay { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; padding: 48px; }
.spinner { width: 36px; height: 36px; border: 2px solid var(--bg4); border-top-color: var(--cyan); border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { font-family: 'DM Mono', monospace; font-size: 12px; color: var(--text2); letter-spacing: 0.08em; }

/* Scrollable sidebar section */
.sidebar-history { flex: 1; padding: 16px 20px; overflow-y: auto; }

/* Toast */
.toast { position: fixed; bottom: 24px; right: 24px; background: var(--bg3); border: 1px solid var(--border); border-radius: 10px; padding: 12px 18px; font-size: 12px; font-family: 'DM Mono', monospace; color: var(--text1); box-shadow: var(--shadow); z-index: 9999; animation: slide-in 0.2s ease; }
.toast.error { border-color: rgba(239,68,68,0.4); color: #fca5a5; }
.toast.success { border-color: rgba(16,185,129,0.4); color: #6ee7b7; }
@keyframes slide-in { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

/* PDF button */
.pdf-btn { display: inline-flex; align-items: center; gap: 6px; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); color: var(--green); font-family: 'DM Mono', monospace; font-size: 11px; border-radius: 7px; padding: 7px 14px; cursor: pointer; transition: all 0.15s; text-decoration: none; }
.pdf-btn:hover { background: rgba(16,185,129,0.2); }

/* Columns used */
.cols-used { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 8px; }
.col-chip { font-size: 10px; font-family: 'DM Mono', monospace; background: var(--bg3); border: 1px solid var(--border); color: var(--text2); padding: 2px 8px; border-radius: 4px; }

@media (max-width: 768px) {
  .app { flex-direction: column; }
  .sidebar { width: 100%; min-width: unset; }
  .stat-grid { grid-template-columns: repeat(2, 1fr); }
  .main-inner { padding: 20px 16px 60px; }
}
`;

// ── API base ────────────────────────────────────────────────────────────────
const API = "http://localhost:8000";

// ── PlotlyChart component ────────────────────────────────────────────────────
function PlotlyChart({ data }) {
  const ref = useRef(null);
  useEffect(() => {
    if (!ref.current || !data) return;
    try {
      Plotly.react(ref.current, data.data || [], {
        ...data.layout,
        autosize: true,
        margin: { t: 50, b: 40, l: 50, r: 20 },
      }, { responsive: true, displayModeBar: false });
    } catch (e) { console.error("Plotly error", e); }
    return () => { try { Plotly.purge(ref.current); } catch {} };
  }, [data]);
  return <div ref={ref} style={{ width: "100%", height: 360 }} />;
}

// ── InsightText helper ───────────────────────────────────────────────────────
function InsightText({ text }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <span className="insight-text">
      {parts.map((p, i) =>
        p.startsWith("**") ? <strong key={i}>{p.slice(2, -2)}</strong> : p
      )}
    </span>
  );
}

// ── Toast ────────────────────────────────────────────────────────────────────
function Toast({ msg, type, onClose }) {
  useEffect(() => { const t = setTimeout(onClose, 3500); return () => clearTimeout(t); }, []);
  return <div className={`toast ${type}`}>{msg}</div>;
}

// ── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [dataset, setDataset] = useState(null);      // upload response
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [history, setHistory] = useState([]);
  const [activeTab, setActiveTab] = useState("preview");
  const [dragging, setDragging] = useState(false);
  const [toast, setToast] = useState(null);
  const fileRef = useRef(null);

  const showToast = (msg, type = "info") => setToast({ msg, type });

  // ── Upload ────────────────────────────────────────────────────────────────
  const handleUpload = useCallback(async (file) => {
    if (!file) return;
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch(`${API}/upload`, { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      setDataset(data);
      setResult(null);
      setHistory([]);
      setActiveTab("preview");
      showToast(`✓ ${file.name} loaded — ${data.rows.toLocaleString()} rows`, "success");
    } catch (e) {
      showToast(e.message, "error");
    } finally {
      setUploading(false);
    }
  }, []);

  const onFileChange = (e) => handleUpload(e.target.files[0]);
  const onDrop = (e) => { e.preventDefault(); setDragging(false); handleUpload(e.dataTransfer.files[0]); };

  // ── Analyze ───────────────────────────────────────────────────────────────
  const handleAnalyze = useCallback(async (q) => {
    const finalQuery = (q || query).trim();
    if (!finalQuery) return showToast("Enter a query first", "error");
    if (!dataset) return showToast("Upload a dataset first", "error");
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch(`${API}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: finalQuery }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Analysis failed");
      setResult(data);
      if (q) setQuery(q);

      // Refresh history
      const hist = await fetch(`${API}/history`).then(r => r.json());
      setHistory(hist.history || []);
    } catch (e) {
      showToast(e.message, "error");
    } finally {
      setLoading(false);
    }
  }, [query, dataset]);

  const intentColor = {
    aggregation: "#22d3ee", trend: "#f472b6", correlation: "#8b5cf6",
    comparison: "#f59e0b", prediction: "#10b981", distribution: "#3b82f6",
    anomaly: "#ef4444", general: "#64748b",
  };

  return (
    <>
      <style>{CSS}</style>
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}
      <div className="app">
        {/* ── Sidebar ──────────────────────────────────────────────────── */}
        <aside className="sidebar">
          <div className="sidebar-logo">
            <div className="logo-text"><span className="logo-glyph">⬡ </span>DataMind</div>
            <div className="logo-sub">Autonomous AI Analyst</div>
          </div>

          {/* Upload */}
          <div className="sidebar-section">
            <div className="sidebar-label">Dataset</div>
            <div
              className={`upload-zone${dragging ? " dragging" : ""}`}
              onDragOver={e => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              onClick={() => fileRef.current?.click()}
            >
              <input ref={fileRef} type="file" accept=".csv,.xlsx,.xls" onChange={onFileChange} />
              {uploading ? (
                <><div className="spinner" style={{ margin: "0 auto 8px" }} /><div className="upload-text">Processing…</div></>
              ) : (
                <>
                  <div className="upload-icon">⬆</div>
                  <div className="upload-text">Drop CSV or XLSX here</div>
                  <div className="upload-sub">or click to browse</div>
                </>
              )}
            </div>

            {dataset && (
              <div className="dataset-info" style={{ marginTop: 10 }}>
                <div className="dataset-name">{dataset.filename}</div>
                <div className="dataset-meta">
                  <span className="meta-chip">{dataset.rows.toLocaleString()} rows</span>
                  <span className="meta-chip">{dataset.cols} cols</span>
                </div>
                {dataset.schema && (
                  <>
                    {dataset.schema.numeric.length > 0 && (
                      <div className="schema-group">
                        <div className="schema-group-label">Numeric</div>
                        <div className="tags">{dataset.schema.numeric.map(c => <span key={c} className="tag tag-num" title={c}>{c}</span>)}</div>
                      </div>
                    )}
                    {dataset.schema.categorical.length > 0 && (
                      <div className="schema-group">
                        <div className="schema-group-label">Categorical</div>
                        <div className="tags">{dataset.schema.categorical.slice(0,10).map(c => <span key={c} className="tag tag-cat" title={c}>{c}</span>)}</div>
                      </div>
                    )}
                    {dataset.schema.datetime.length > 0 && (
                      <div className="schema-group">
                        <div className="schema-group-label">Datetime</div>
                        <div className="tags">{dataset.schema.datetime.map(c => <span key={c} className="tag tag-dt" title={c}>{c}</span>)}</div>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}
          </div>

          {/* History */}
          <div className="sidebar-history">
            <div className="sidebar-label">Recent Queries</div>
            {history.length === 0 ? (
              <div style={{ fontSize: 11, color: "var(--text3)", fontFamily: "'DM Mono', monospace" }}>No queries yet</div>
            ) : (
              <div className="history-list">
                {history.map(item => (
                  <div key={item.id} className="history-item" onClick={() => handleAnalyze(item.query)}>
                    <div className="history-q">{item.query}</div>
                    <div className="history-meta">
                      <span className="history-intent" style={{ color: intentColor[item.intent] || "#64748b" }}>{item.intent}</span>
                      <span className="history-time">{item.timestamp ? new Date(item.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </aside>

        {/* ── Main ─────────────────────────────────────────────────────── */}
        <main className="main">
          <div className="main-inner">
            <div className="page-header">
              <div className="page-title"><span>Autonomous AI</span><br />Data Analyst</div>
              <div className="page-sub">Upload any dataset → Ask anything in plain English → Get insights + charts</div>
            </div>

            {/* Stats */}
            {dataset && (
              <div className="stat-grid">
                <div className="stat-card">
                  <div className="stat-value">{dataset.rows.toLocaleString()}</div>
                  <div className="stat-label">Total Rows</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{dataset.cols}</div>
                  <div className="stat-label">Columns</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{dataset.schema?.numeric.length ?? 0}</div>
                  <div className="stat-label">Numeric</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value">{dataset.schema?.datetime.length ?? 0}</div>
                  <div className="stat-label">Datetime</div>
                </div>
              </div>
            )}

            {/* Dataset preview / stats tabs */}
            {dataset && (
              <div className="result-section" style={{ marginBottom: 28 }}>
                <div className="result-header">
                  <div className="tabs" style={{ margin: 0 }}>
                    {["preview", "stats"].map(t => (
                      <button key={t} className={`tab${activeTab === t ? " active" : ""}`} onClick={() => setActiveTab(t)}>{t}</button>
                    ))}
                  </div>
                </div>
                <div style={{ padding: "16px 20px" }}>
                  {activeTab === "preview" && (
                    <div className="table-wrap">
                      <table>
                        <thead><tr>{dataset.preview[0] && Object.keys(dataset.preview[0]).map(k => <th key={k}>{k}</th>)}</tr></thead>
                        <tbody>{dataset.preview.slice(0,12).map((row, i) => (
                          <tr key={i}>{Object.values(row).map((v, j) => <td key={j} title={String(v ?? "")}>{v === null || v === undefined ? <span style={{color:"var(--text3)"}}>—</span> : String(v)}</td>)}</tr>
                        ))}</tbody>
                      </table>
                    </div>
                  )}
                  {activeTab === "stats" && dataset.stats && (
                    <div className="table-wrap">
                      <table>
                        <thead><tr><th>Column</th><th>Mean</th><th>Min</th><th>Max</th><th>Std</th></tr></thead>
                        <tbody>{Object.entries(dataset.stats).map(([col, s]) => (
                          <tr key={col}>
                            <td><span className="tag tag-num">{col}</span></td>
                            <td>{s.mean?.toLocaleString()}</td>
                            <td>{s.min?.toLocaleString()}</td>
                            <td>{s.max?.toLocaleString()}</td>
                            <td>{s.std?.toLocaleString()}</td>
                          </tr>
                        ))}</tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Query */}
            <div className="query-section">
              <div className="query-label">Ask your data anything</div>
              <div className="query-input-wrap">
                <textarea
                  className="query-input"
                  rows={3}
                  placeholder={
                    dataset
                      ? 'e.g. "What is the average revenue by region?" or "Predict next month sales"'
                      : "Upload a dataset to start asking questions…"
                  }
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
                      handleAnalyze();
                    }
                  }}
                />
              </div>
              <div className="query-actions">
                <div className="suggestions">
                  {(dataset?.suggestions || [
                    "What is the average sales?",
                    "Show distribution of price",
                    "Compare revenue by region",
                    "Detect anomalies",
                    "Show trend over time",
                    "Predict future values",
                  ]).slice(0, 5).map(s => (
                    <span key={s} className="suggestion-chip" onClick={() => handleAnalyze(s)}>{s}</span>
                  ))}
                </div>
                <button className="btn-primary" onClick={() => handleAnalyze()} disabled={loading || !dataset}>
                  {loading ? "Analysing…" : "⚡ Analyse"}
                </button>
              </div>
            </div>

            {/* Result */}
            {loading && (
              <div className="result-section">
                <div className="loading-overlay">
                  <div className="spinner" />
                  <div className="loading-text">Running analysis…</div>
                </div>
              </div>
            )}

            {result && !loading && (
              <div className="result-section">
                <div className="result-header">
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <span className="intent-badge" style={{ borderColor: `${intentColor[result.intent]}40`, color: intentColor[result.intent], background: `${intentColor[result.intent]}15` }}>
                      <span className="intent-dot" style={{ background: intentColor[result.intent] }} />
                      {result.intent}
                    </span>
                    {result.group_by && <span className="mono" style={{ fontSize: 11, color: "var(--text2)" }}>grouped by {result.group_by}</span>}
                  </div>
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    {result.pdf_link && (
                      <a className="pdf-btn" href={`${API}${result.pdf_link}`} download target="_blank" rel="noreferrer">
                        ⬇ PDF Report
                      </a>
                    )}
                  </div>
                </div>
                <div className="result-body">
                  {/* Raw result */}
                  <div className="result-raw">{result.result}</div>

                  {/* Columns used */}
                  {result.columns_used?.length > 0 && (
                    <div className="cols-used">
                      <span className="mono" style={{ fontSize: 10, color: "var(--text3)", marginRight: 4 }}>cols:</span>
                      {result.columns_used.map(c => <span key={c} className="col-chip">{c}</span>)}
                    </div>
                  )}

                  {/* Chart */}
                  {result.graph && (
                    <div className="chart-container" style={{ marginTop: 20 }}>
                      <div className="chart-title">Visualization</div>
                      <PlotlyChart data={result.graph} />
                    </div>
                  )}

                  {/* Insight */}
                  {result.insight && (
                    <div className="insight-box" style={{ marginTop: 20 }}>
                      <div className="insight-label">🧠 Key Insight</div>
                      <InsightText text={result.insight} />
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Empty state */}
            {!dataset && !loading && (
              <div className="empty-state">
                <div className="empty-icon">⬡</div>
                <div className="empty-title">No dataset loaded</div>
                <div className="empty-sub">Upload a CSV or XLSX file from the sidebar to begin</div>
              </div>
            )}
          </div>
        </main>
      </div>
    </>
  );
}