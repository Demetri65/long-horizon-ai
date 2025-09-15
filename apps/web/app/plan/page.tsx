"use client";
import { useState } from "react";
import { LlmService, type LLMRequest, type LLMResponse } from "@/lib/api/client";

export default function PlanPage() {
  const [input, setInput] = useState("");
  const [result, setResult] = useState<LLMResponse | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const req: LLMRequest = { input, max_steps: 8 };
      const res = await LlmService.llmStructure({ requestBody: req });
      setResult(res);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="p-6 max-w-2xl space-y-4">
      <h1 className="text-xl font-semibold">Prompt planner</h1>
      <form onSubmit={onSubmit} className="space-y-2">
        <textarea className="w-full h-32 border rounded p-2" value={input}
          onChange={(e)=>setInput(e.target.value)} placeholder="Describe your goal…" />
        <button className="border rounded px-4 py-2" disabled={loading}>
          {loading ? "Thinking…" : "Generate"}
        </button>
      </form>
      {result && (
        <section className="space-y-3">
          <div>
            <h2 className="font-medium">Steps</h2>
            <ol className="list-decimal ml-5">
              {result.plan.steps.map(s => <li key={s.id}><b>{s.title}</b>{s.detail ? ` — ${s.detail}` : ""}</li>)}
            </ol>
          </div>
          <div>
            <h2 className="font-medium">Final prompt</h2>
            <pre className="bg-neutral-100 p-3 rounded whitespace-pre-wrap">
              {result.plan.final_prompt}
            </pre>
          </div>
        </section>
      )}
    </main>
  );
}