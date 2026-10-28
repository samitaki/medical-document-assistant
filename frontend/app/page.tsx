"use client";

import { useEffect, useState } from "react";
import Chat from "./components/Chat";
import DocumentsPanel from "./components/DocumentsPanel";
import { clearDocuments, listDocuments, removeDocument, uploadDocument, type Doc, type Failed } from "../lib/api";

export default function Page() {
  const [docs, setDocs] = useState<Doc[]>([]);
  const [failed, setFailed] = useState<Failed[]>([]);
  const [uploading, setUploading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    refresh();
  }, []);

  async function refresh() {
    try {
      setDocs(await listDocuments());
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  // one request per file, so the panel can name the file that is currently being indexed
  async function onUpload(files: File[]) {
    setError(null);
    setFailed([]);
    for (const file of files) {
      setUploading(file.name);
      try {
        const res = await uploadDocument(file);
        setFailed((prev) => [...prev, ...res.failed]);
      } catch (e) {
        setFailed((prev) => [...prev, { filename: file.name, error: (e as Error).message }]);
      }
      await refresh();
    }
    setUploading(null);
  }

  async function onRemove(filename: string) {
    try {
      await removeDocument(filename);
    } catch (e) {
      setError((e as Error).message);
    }
    await refresh();
  }

  async function onClear() {
    try {
      await clearDocuments();
      setFailed([]);
    } catch (e) {
      setError((e as Error).message);
    }
    await refresh();
  }

  return (
    <main className="mx-auto max-w-[800px] px-4 py-8">
      <h1 className="text-lg font-semibold">Medical document assistant</h1>
      <p className="mb-6 mt-1 text-sm text-slate-600">
        Upload medical pdfs and ask questions about them. Answers cite the file and page they came from.
      </p>

      {error && (
        <p className="mb-4 rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p>
      )}

      <DocumentsPanel
        docs={docs}
        failed={failed}
        uploading={uploading}
        onUpload={onUpload}
        onRemove={onRemove}
        onClear={onClear}
      />

      <Chat ready={docs.length > 0} />

      <footer className="mt-10 border-t border-slate-200 pt-3 text-xs text-slate-500">
        Informational only, not medical advice. Do not use for clinical decisions.
      </footer>
    </main>
  );
}
