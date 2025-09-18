"use client";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Expand } from "lucide-react";
import { ChatMessage } from "./chat-message";
import { UIMessage } from "ai";

export type ChatMessagesProps = {
  // messages: UIMessage[];
  nodes: any;
  expanded: boolean;
  onToggleExpand?: () => void;
}

export const ChatMessages = ({ nodes, expanded, onToggleExpand }: ChatMessagesProps) => {
  

  return (
    <div className="w-full min-h-[40%] max-h-[60%] p-4  rounded-lg relative">
      <Button variant="ghost" size="icon" onClick={onToggleExpand} className="absolute top-2 right-2">
        <Expand />
      </Button>
      <ScrollArea className="flex flex-col space-y-2 mr-24 ml-24">
        {nodes?.map((node: any) => (
          <div key={node.nodeId}>
            {node.nodeId && <div>{node.nodeId}</div>}
            {node.title && <div>{node.title}</div>}
            {node.explanation && <div>{node.explanation}</div>}
          </div>
        ))}
      </ScrollArea>

    </div>
  );
}