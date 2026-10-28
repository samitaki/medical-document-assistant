const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Doc = { filename: string; pages: number; chunks: number };
export type Indexed = Doc & { tables: number };
export type Failed = { filename: string; error: string };
export type Citation = { n: number; filename: string; page: number; kind: string; snippet: string };
export type Answer = { answer: string; citations: Citation[] };
export type Turn = { role: "user" | "assistant"; content: string };

async function call(path: string, init?: RequestInit) {
  const res = await fetch(BASE + path, init);
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    // the api writes its error strings for a person to read, so pass them straight through
    throw new Error(body?.error ?? `Request failed (${res.status}).`);
  }
  return body;
}

export async function listDocuments(): Promise<Doc[]> {
  const body = await call("/documents");
  return body.documents;
}

export async function uploadDocument(file: File): Promise<{ indexed: Indexed[]; failed: Failed[] }> {
  const form = new FormData();
  form.append("files", file);
  return call("/documents", { method: "POST", body: form });
}

export async function removeDocument(filename: string): Promise<void> {
  await call(`/documents/${encodeURIComponent(filename)}`, { method: "DELETE" });
}

export async function clearDocuments(): Promise<void> {
  await call("/documents", { method: "DELETE" });
}

export async function ask(question: string, history: Turn[]): Promise<Answer> {
  return call("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, history }),
  });
}
