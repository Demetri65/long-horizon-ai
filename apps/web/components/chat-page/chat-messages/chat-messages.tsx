"use client";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Expand } from "lucide-react";
import { ChatMessage } from "./chat-message";

export type ChatMessagesProps = {
  messages: ChatMessage[];
  expanded: boolean;
  onToggleExpand?: () => void;
}

export const ChatMessages = ({ messages, expanded, onToggleExpand }: ChatMessagesProps) => {
  return (
    <div className="w-full min-h-[40%] max-h-[60%] p-4 zinc-800 rounded-lg relative">
      <Button variant="ghost" size="icon" onClick={onToggleExpand} className="absolute top-2 right-2">
        <Expand />
      </Button>
      <ScrollArea className="flex flex-col space-y-2 mr-24 ml-24">
        {messages.map((msg) => (
          <ChatMessage {...msg} />
        ))}
      </ScrollArea>

    </div>
  );
}