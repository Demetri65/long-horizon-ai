'use client';

import { useEffect, useRef, useState } from 'react';
import { GraphSection } from './graph-section/graph-section';
import { ChatMessages } from './chat-messages/chat-messages';
import { ChatInput } from './chat-input';
import { Graph, GraphService } from '@/lib/api/client';

import { DefaultChatTransport } from 'ai';
import { useChat } from '@ai-sdk/react'; // Streams parts with text-delta/text-end under the hood. :contentReference[oaicite:2]{index=2}
import { GoalStreamStore } from '@/lib/streaming/goal-stream-store';
import { useNodeStream } from '@/hooks/use-node-stream';
import { IncompleteJsonParser } from 'incomplete-json-parser';

export type RawNode = {
  nodeId: string;
  title?: string;
  status?: string;
  parent?: string | null;
  kind?: string;
  smarter?: unknown;
};


export default function ChatPage(project: any) {
  const [graph, setGraph] = useState<Graph | null>(null);
  const [expanded, setExpanded] = useState(false);
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
          body: { graphId: graphIdRef.current, maxGoals: 3, prompt: text },
        };
      },
    }),
  });

  console.log('Messages:', messages);

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
      { body: { graphId: gid, maxGoals: 3 } }
    ).catch((error) => console.error('Error sending message:', error));
  };



  const temp = messages.at(-1);
  const fullText = (temp?.parts ?? [])
    .filter((part: any) => part.type === 'text')
    .map((part: any) => part.text)
    .join(' '); // Join the array into a single string.

  // Use the custom hook with the full text and a typing speed (e.g., 50ms).
  const { displayedText, nodes } = useNodeStream(fullText);
  console.log('Nodes:', nodes);

  console.log(displayedText)

  return (
    <div className="flex flex-col w-full place-items-center pb-0 bg-zinc-800">
      <GraphSection graph={graph} messages={messages} />
      <ChatMessages
        nodes={nodes}
        expanded={expanded}
        onToggleExpand={() => setExpanded((prev) => !prev)}
      />
      <ChatInput onSend={handleSend} />
    </div>
  );
}