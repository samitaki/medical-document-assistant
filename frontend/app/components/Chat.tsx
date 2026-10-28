"use client";

import { useState } from "react";
import { ask, type Citation, type Turn } from "../../lib/api";
import AnswerMessage from "./AnswerMessage";

type Msg = { role: "user" | "assistant"; content: string; citations?: Citation[] };

// enough for a follow-up like "and his potassium?" without resending the whole thread
const HISTORY_TURNS = 6;

export default function Chat({ ready }: { ready: boolean }) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send() {
    const question = input.trim();
    if (!question || pending) return;

    const history: Turn[] = messages.slice(-HISTORY_TURNS).map((m) => ({ role: m.role, content: m.content }));
    setMessages([...messages, { role: "user", content: question }]);
    setInput("");
    setError(null);
    setPending(true);

    try {
      const res = await ask(question, history);
      setMessages((prev) => [...prev, { role: "assistant", content: res.answer, citations: res.citations }]);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setPending(false);
    }
  }

  return (
    <section className="mt-6">
      <div className="space-y-3">
        {messages.map((m, i) =>
          m.role === "user" ? (
            <div key={i} className="flex justify-end">
              <p className="max-w-[85%] rounded bg-slate-700 px-3 py-2 text-sm text-white">{m.content}</p>
            </div>
          ) : (
            <div key={i} className="flex justify-start">
              <AnswerMessage answer={m.content} citations={m.citations ?? []} />
            </div>
          )
        )}

        {pending && (
          <div className="flex justify-start">
            <p className="rounded border border-slate-300 px-3 py-2 text-sm text-slate-500">Thinking...</p>
          </div>
        )}
      </div>

      {error && <p className="mt-3 rounded border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">{error}</p>}

      <div className="mt-4 flex gap-2">
        <textarea
          rows={2}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send();
            }
          }}
          disabled={!ready || pending}
          placeholder={ready ? "Ask about the uploaded documents" : "Upload a pdf first"}
          className="flex-1 resize-none rounded border border-slate-300 px-3 py-2 text-sm disabled:bg-slate-100 disabled:text-slate-500"
        />
        <button
          onClick={send}
          disabled={!ready || pending || !input.trim()}
          className="h-fit self-end rounded bg-slate-700 px-4 py-2 text-sm text-white disabled:bg-slate-300"
        >
          {pending ? "..." : "Send"}
        </button>
      </div>
      <p className="mt-1 text-xs text-slate-500">Enter to send, shift+enter for a new line.</p>
    </section>
  );
}
