"use client";

import { useRef, useState } from "react";
import type { Doc, Failed } from "../../lib/api";

type Props = {
  docs: Doc[];
  failed: Failed[];
  uploading: string | null;
  onUpload: (files: File[]) => void;
  onRemove: (filename: string) => void;
  onClear: () => void;
};

export default function DocumentsPanel({ docs, failed, uploading, onUpload, onRemove, onClear }: Props) {
  const [dragging, setDragging] = useState(false);
  const picker = useRef<HTMLInputElement>(null);

  function pick(list: FileList | null) {
    if (list && list.length) onUpload(Array.from(list));
  }

  return (
    <section className="rounded border border-slate-300">
      <div className="flex items-center justify-between border-b border-slate-200 px-4 py-2">
        <h2 className="text-sm font-medium">Documents</h2>
        {docs.length > 0 && (
          <button
            onClick={onClear}
            disabled={uploading !== null}
            className="text-xs text-slate-600 underline underline-offset-2 hover:text-slate-900 disabled:text-slate-400"
          >
            Clear all
          </button>
        )}
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          pick(e.dataTransfer.files);
        }}
        onClick={() => picker.current?.click()}
        className={`m-4 cursor-pointer rounded border border-dashed px-4 py-6 text-center text-sm ${
          dragging ? "border-slate-500 bg-slate-50" : "border-slate-300"
        }`}
      >
        <input
          ref={picker}
          type="file"
          accept="application/pdf"
          multiple
          hidden
          onChange={(e) => {
            pick(e.target.files);
            e.target.value = "";
          }}
        />
        Drop pdfs here, or click to choose files
      </div>

      {uploading && (
        <p className="px-4 pb-3 text-sm text-slate-600">
          Indexing {uploading}, this takes a few seconds per file.
        </p>
      )}

      {docs.length === 0 && !uploading && (
        <p className="px-4 pb-4 text-sm text-slate-600">
          Nothing is indexed yet. Upload a pdf before asking a question.
        </p>
      )}

      {(docs.length > 0 || failed.length > 0) && (
        <ul className="border-t border-slate-200 text-sm">
          {docs.map((d) => (
            <li key={d.filename} className="flex items-center justify-between px-4 py-2">
              <span>
                {d.filename}
                <span className="ml-2 text-slate-500">
                  {d.pages} {d.pages === 1 ? "page" : "pages"} · {d.chunks} chunks
                </span>
              </span>
              <button
                onClick={() => onRemove(d.filename)}
                disabled={uploading !== null}
                className="text-xs text-slate-600 underline underline-offset-2 hover:text-slate-900 disabled:text-slate-400"
              >
                Remove
              </button>
            </li>
          ))}
          {failed.map((f) => (
            <li key={f.filename} className="px-4 py-2 text-red-700">
              {f.filename}
              <span className="ml-2 text-red-600">{f.error}</span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
