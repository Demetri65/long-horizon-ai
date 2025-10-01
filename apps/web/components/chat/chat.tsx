'use client';

import { useRef, useState } from 'react';
import { Messages } from '../chat/messages/messages';
import { Input } from '../chat/input/input';
import { Graph, GraphService } from '@/lib/api/client';

import { DefaultChatTransport } from 'ai';
import { useChat } from '@ai-sdk/react';
import { useNodeStream } from '@/hooks/use-node-stream';
import { GraphSection } from '../chat/graph/graph';

export type RawNode = {
  nodeId: string;
  title?: string;
  status?: string;
  parent?: string | null;
  kind?: string;
  smarter?: unknown;
};


export const Chat = (project: any) => {
  const [graph, setGraph] = useState<Graph | null>(null);
  const graphIdRef = useRef<string | null>(null);


  const { messages, sendMessage, status } = useChat({
    transport: new DefaultChatTransport({
      api: '/api/decompose',
      prepareSendMessagesRequest: ({ messages, api }) => {
        const last = messages.at(-1);
        const text =
          (last?.parts ?? [])
            .filter((p: any) => p.type === 'text')
            .map((p: any) => p.text)
            .join('') || '';
        return {
          api,
          headers: { 'Content-Type': 'application/json' },
          body: { graphId: graphIdRef.current, maxGoals: 5, prompt: text },
        };
      },
    }),
  });

  const ensureGraph = async () => {
    if (graphIdRef.current) return graphIdRef.current;
    const id = crypto.randomUUID().slice(0, 8).toUpperCase();
    const created = await GraphService.graphCreateGraph({ requestBody: { graphId: id } });
    graphIdRef.current = created.graphId;
    setGraph(created);
    return created.graphId;
  };

  const handleSend = async (text: string) => {
    const gid = await ensureGraph();
    sendMessage(
      { role: 'user', parts: [{ type: 'text', text }] },
      { body: { graphId: gid, maxGoals: 5 } }
    ).catch((error) => console.error('Error sending message:', error));
  };



  const message = messages.at(-1);
  const fullText = (message?.parts ?? [])
    .filter((part: any) => part.type === 'text')
    .map((part: any) => part.text)
    .join(' ');

  const { displayedText, nodes } = useNodeStream(fullText);

  return (
    <div className="flex flex-col w-full place-items-center pb-0 bg-zinc-800">
      <GraphSection graph={nodes} messages={messages} streamStatus={status} />
      <Messages messages={messages} />
      <Input onSend={handleSend} />
    </div>
  );
}