import { createUIMessageStream, createUIMessageStreamResponse } from 'ai';

export const maxDuration = 30;

export async function POST(req: Request) {
    const payload = await req.json().catch(() => ({}));
    const graphId = payload.graphId ?? payload.body?.graphId;
    const maxGoals = payload.maxGoals ?? payload.body?.maxGoals ?? 8;
    const prompt = payload.prompt;
    
    
    const FASTAPI = process.env.NEXT_PUBLIC_API_BASE ?? 'http://127.0.0.1:8000';
    const upstream = await fetch(
        `${FASTAPI}/api/v1/graph/${encodeURIComponent(graphId)}/llm/decompose:stream`,
        {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, maxGoals }),
        }
    );

    const body = upstream.body;
    if (!body) return new Response(JSON.stringify({ error: 'no upstream body' }), { status: 502 });

    return createUIMessageStreamResponse({
        stream: createUIMessageStream({
            async execute({ writer }) {
                const textId = `t_${crypto.randomUUID()}`;
                writer.write({ type: 'start', messageId: crypto.randomUUID() });
                writer.write({ type: 'text-start', id: textId });

                const reader = body.getReader();
                const decoder = new TextDecoder();
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    writer.write({ type: 'text-delta', id: textId, delta: decoder.decode(value) });
                }

                writer.write({ type: 'text-end', id: textId });
                writer.write({ type: 'finish' });
            },
        }),
    });
};