'use client';

import { useState } from "react";
import { GraphSection } from "./graph-section/graph-section";
import { ChatMessage, ChatMessages } from "./chat-messages/chat-messages";
import { ChatInput } from "./chat-input";
import { StructuredPlan, LLMRequest, LLMResponse, LlmService } from "@/lib/api/client";

export default function ChatPage(project) {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [plan, setPlan] = useState<StructuredPlan | null>(null);
    const [expanded, setExpanded] = useState(false);
  
    // Sends a user message and requests a plan from the API. Updates both
    // message history and the plan state. Any errors will be surfaced as
    // assistant messages.
    const handleSend = async (content: string) => {
      const userMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content,
      };
      setMessages((prev) => [...prev, userMsg]);
      try {
        const requestBody: LLMRequest = { input: content, max_steps: 8 };
        const res: LLMResponse = await LlmService.llmStructure({ requestBody });
        const assistantContent = res?.plan?.final_prompt ??
          "The model returned an empty response.";
        const assistantMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: assistantContent,
        };
        setMessages((prev) => [...prev, assistantMsg]);
        setPlan(res.plan);
      } catch (error: any) {
        const errorMsg: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            typeof error?.message === "string"
              ? `Error: ${error.message}`
              : "An unexpected error occurred",
        };
        setMessages((prev) => [...prev, errorMsg]);
      }
    };

  return (
    <div className="flex flex-col w-full place-items-center pb-0">
        <GraphSection />
        <ChatMessages messages={messages} expanded={expanded} onToggleExpand={() => setExpanded((prev) => !prev)} />
        <ChatInput onSend={handleSend} />
    </div>
  );
}