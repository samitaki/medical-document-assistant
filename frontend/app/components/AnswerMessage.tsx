"use client";

import { useState } from "react";
import type { Citation } from "../../lib/api";

type Props = { answer: string; citations: Citation[] };

export default function AnswerMessage({ answer, citations }: Props) {
  const [open, setOpen] = useState<number | null>(null);
  const byNumber = new Map(citations.map((c) => [c.n, c]));

  function toggle(n: number) {
    setOpen(open === n ? null : n);
  }

  return (
    <div className="max-w-[85%] rounded border border-slate-300 bg-white px-3 py-2 text-sm">
      <p className="whitespace-pre-wrap">
        {splitOnCitations(answer).map((part, i) =>
          typeof part === "string" ? (
            <span key={i}>{part}</span>
          ) : byNumber.has(part.n) ? (
            <button
              key={i}
              onClick={() => toggle(part.n)}
              className={`mx-0.5 rounded border px-1 align-baseline text-xs ${
                open === part.n
                  ? "border-slate-700 bg-slate-700 text-white"
                  : "border-slate-300 bg-slate-100 text-slate-700 hover:border-slate-500"
              }`}
            >
              {part.n}
            </button>
          ) : (
            // a number the model made up has no source behind it, leave it as plain text
            <span key={i}>[{part.n}]</span>
          )
        )}
      </p>

      {citations.length > 0 && (
        <div className="mt-3 border-t border-slate-200 pt-2">
          <p className="mb-1 text-xs uppercase tracking-wide text-slate-500">Sources</p>
          <ul className="space-y-1">
            {citations.map((c) => (
              <li key={c.n}>
                <button
                  onClick={() => toggle(c.n)}
                  className="text-left text-xs text-slate-700 hover:text-slate-900"
                >
                  <span className="text-slate-500">[{c.n}]</span> {c.filename} · page {c.page}
                  {c.kind === "table" && (
                    <span className="ml-2 rounded bg-slate-200 px-1 text-[10px] uppercase tracking-wide text-slate-700">
                      table
                    </span>
                  )}
                </button>
                {open === c.n && (
                  <p className="mt-1 overflow-x-auto whitespace-pre-wrap rounded bg-slate-50 p-2 font-mono text-[11px] leading-relaxed text-slate-700">
                    {c.snippet}
                  </p>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function splitOnCitations(text: string): (string | { n: number })[] {
  const out: (string | { n: number })[] = [];
  let last = 0;
  for (const m of text.matchAll(/\[(\d+)\]/g)) {
    const at = m.index ?? 0;
    if (at > last) out.push(text.slice(last, at));
    out.push({ n: Number(m[1]) });
    last = at + m[0].length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}
