"use client";

import { SendButton } from "./send-button";
import { PlusButton } from "./plus-button";
import { TextArea } from "./text-area";
import { useChatInput } from "./use-chat-input";

export type ChatInputProps = {
  onSend: (text: string) => void | Promise<void>;
  placeholder?: string;
  children?: React.ReactNode;
};

export const Input = ({
  onSend,
  placeholder = "Send a message…",
  children,
}: ChatInputProps) => {
  const {
    value,
    rows,
    textareaRef,
    handleChange,
    handleSubmit,
    onKeyDown,
    toggleExpanded,
  } = useChatInput({ onSend, collapsedRows: 1, expandedRows: 3 });

  return (
    <div className="w-[60%] max-w-2xl min-h-[56px] rounded-[28px] flex items-center bg-zinc-700 sticky bottom-0 p-2 justify-between">
      <PlusButton toggleExpanded={toggleExpanded} />
      <TextArea
        placeholder={placeholder}
        textAreaRef={textareaRef}
        value={value}
        onChange={handleChange}
        rows={rows}
        onKeyDown={onKeyDown}
      />
      <SendButton onClick={handleSubmit} />
      {children}
    </div>
  );
}