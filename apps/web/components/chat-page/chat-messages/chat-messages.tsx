"use client";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Expand } from "lucide-react";
import { ChatMessage } from "./chat-message";
import { TextPart, UIMessage } from "ai";

export type ChatMessagesProps = {
  messages: UIMessage[];
  nodes: any;
  expanded: boolean;
  onToggleExpand?: () => void;
}

export const ChatMessages = ({ nodes, expanded, onToggleExpand, messages }: ChatMessagesProps) => {

  return (
    <div className="w-full min-h-[40%] max-h-[60%] p-4  rounded-lg relative">
      {/* <Button variant="ghost" size="icon" onClick={onToggleExpand} className="absolute top-2 right-2">
        <Expand />
      </Button> */}
      <ScrollArea className="flex flex-col space-y-2 mr-24 ml-24">
        {messages.map((message) => {
          return message.role === "user" && <ChatMessage key={message.id} message={message} />;
        })}
      </ScrollArea>

    </div>
  );
}