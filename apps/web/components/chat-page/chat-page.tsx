'use client';

import { useRef, useState } from "react";
import { GraphSection } from "./graph-section/graph-section";
import { ChatMessages } from "./chat-messages/chat-messages";
import { ChatMessage } from "./chat-messages/chat-message";
import { ChatInput } from "./chat-input";
import {
  Graph,
  GraphService,
} from "@/lib/api/client";

export default function ChatPage(project) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [graph, setGraph] = useState<Graph | null>(null);
  const [expanded, setExpanded] = useState(false);
  const graphIdRef = useRef<string | null>(null);

  const ensureGraph = async () => {
    if (graphIdRef.current) return graphIdRef.current;

    const id = crypto.randomUUID().slice(0, 8).toUpperCase();

    const created = await GraphService.graphCreateGraph({ requestBody: { graphId: id } });;

    graphIdRef.current = created.graphId;
    setGraph(created);
    return created.graphId;
  };
  const handleSend = async (content: string) => {
    const userMsg: ChatMessage = { id: crypto.randomUUID(), role: "user", content };
    setMessages(prev => [...prev, userMsg]);

    try {
      const gid = await ensureGraph();

      const updated = await GraphService.graphDecompose({
        graphId: gid,
        requestBody: { prompt: content, maxGoals: 8 },
      });

      setGraph(updated);

      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: `Created a chronological set of high-level goals for graph ${gid}.`,
      };
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages(prev => [
        ...prev,
        { id: crypto.randomUUID(), role: "assistant", content: `Error: ${err?.message ?? "Unknown error"}` },
      ]);
    }
  };

  return (
    <div className="flex flex-col w-full place-items-center pb-0 bg-zinc-800">
      <GraphSection graph={graph} />
      <ChatMessages messages={messages} expanded={expanded} onToggleExpand={() => setExpanded((prev) => !prev)} />
      <ChatInput onSend={handleSend} />
    </div>
  );
}