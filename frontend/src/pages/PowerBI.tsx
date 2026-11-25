import { useState, type FormEvent } from "react";
import { PieChart, Settings } from "lucide-react";

const STORAGE_KEY = "hr_dashboard_powerbi_embed_url";

export default function PowerBI() {
  const [embedUrl, setEmbedUrl] = useState(() => localStorage.getItem(STORAGE_KEY));
  const [editing, setEditing] = useState(!embedUrl);
  const [draft, setDraft] = useState(embedUrl ?? "");

  function onSave(e: FormEvent) {
    e.preventDefault();
    const trimmed = draft.trim();
    if (!trimmed) return;
    localStorage.setItem(STORAGE_KEY, trimmed);
    setEmbedUrl(trimmed);
    setEditing(false);
  }

  function onClear() {
    localStorage.removeItem(STORAGE_KEY);
    setEmbedUrl(null);
    setDraft("");
    setEditing(true);
  }

  if (embedUrl && !editing) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Power BI</h1>
            <p className="mt-1 text-sm text-slate-500">Embedded report</p>
          </div>
          <button
            onClick={() => setEditing(true)}
            className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-600 shadow-sm transition-colors hover:bg-slate-50"
          >
            <Settings size={15} /> Change report
          </button>
        </div>
        <iframe
          title="Power BI report"
          src={embedUrl}
          className="h-[75vh] w-full rounded-2xl border border-slate-200 bg-white shadow-sm"
          allowFullScreen
        />
      </div>
    );
  }

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-500">
        <PieChart size={26} />
      </span>
      <h1 className="mt-4 text-xl font-semibold tracking-tight text-slate-900">Waiting for connection</h1>
      <p className="mt-1 max-w-md text-sm text-slate-500">
        No Power BI report is configured yet. Publish a report to a workspace,
        then paste its embed/publish URL below.
      </p>
      <form onSubmit={onSave} className="mt-6 flex w-full max-w-md flex-col gap-2 sm:flex-row">
        <input
          type="url"
          required
          placeholder="https://app.powerbi.com/reportEmbed?..."
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        <button
          type="submit"
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-indigo-500"
        >
          Connect
        </button>
      </form>
      {embedUrl && (
        <button onClick={onClear} className="mt-3 text-xs text-slate-400 hover:text-slate-600">
          Clear saved report
        </button>
      )}
    </div>
  );
}
