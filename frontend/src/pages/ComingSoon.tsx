import { Link } from "react-router-dom";
import { Construction, ArrowLeft } from "lucide-react";

export default function ComingSoon({ title }: { title: string }) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
        <Construction size={26} />
      </span>
      <h1 className="mt-4 text-xl font-semibold tracking-tight text-slate-900">{title}</h1>
      <p className="mt-1 max-w-sm text-sm text-slate-500">
        This dashboard hasn't been built yet - the schema and seed data already support it, it just needs a page.
      </p>
      <Link
        to="/"
        className="mt-6 flex items-center gap-1.5 text-sm font-medium text-indigo-600 hover:text-indigo-700"
      >
        <ArrowLeft size={14} /> Back to Home
      </Link>
    </div>
  );
}
