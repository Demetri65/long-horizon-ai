"use client";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Message } from "./message";
import { UIMessage } from "ai";

export type MessagesProps = {
  messages: UIMessage[];
}

// todo - add thinking state then come up with solution for discerning graph message and ai message
export const Messages = ({ messages }: MessagesProps) => {
  return (
    <div className="w-full min-h-[40%] max-h-[60%] p-4  rounded-lg relative">
      <ScrollArea className="flex flex-col space-y-2 mr-24 ml-24">
        {messages.map((message) => {
          return message.role === "user" && <Message key={message.id} message={message} />;
        })}
      </ScrollArea>

    </div>
  );
}