"use client";

import * as React from "react";
import { useState, useRef, FormEvent } from "react";
import { ArrowUp, Plus } from "lucide-react";
import { HTMLAttributes } from "react";
import { Button } from "../ui/button";

export type PlusButtonProps = {
  toggleExpanded: () => void;
};

export default function PlusButton({ toggleExpanded }: PlusButtonProps) {
  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggleExpanded}
      className="size-[36px] rounded-full"
    >
      <Plus size={20} />
    </Button>
  )
}


export const SendButton = (props: HTMLAttributes<HTMLButtonElement>) => {
  return (
    <Button
      type="submit"
      variant="ghost"
      size="icon"
      className="size-[36px] rounded-full"
      {...props}
    >
      <ArrowUp size={20} />
    </Button>
  )
}

export type InputAreaProps = {
  placeholder?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  textAreaRef?: React.RefObject<HTMLTextAreaElement>;
  rows?: number;
} & HTMLAttributes<HTMLTextAreaElement>;

export const InputArea = ({ placeholder, value, onChange, textAreaRef, rows }: InputAreaProps) => {
  return (
    <textarea
      ref={textAreaRef}
      value={value}
      onChange={onChange}
      rows={1}
      className="border-none bg-transparent resize-none outline-none justify-start flex-grow ml-2"
      placeholder={placeholder}
    />
  )
}

export type ChatInputProps = {
  onSend: any;
  placeholder?: string;
  children?: React.ReactNode;
}

export function ChatInput({
  onSend,
  placeholder = "Send a message…",
  children,
}: ChatInputProps) {
  const [value, setValue] = useState("");
  const [expanded, setExpanded] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const resizeTextarea = () => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    resizeTextarea();
  };

  const handleSubmit = (e?: FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed) return;
    onSend(trimmed);
    setValue("");
    // Reset height back to single line after sending
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const toggleExpanded = () => {
    setExpanded((prev) => !prev);
    setTimeout(() => {
      textareaRef.current?.focus();
    }, 0);
  };

  return (
    <div className="w-[60%] max-w-2xl min-h-[56px] rounded-[28px] flex items-center bg-zinc-700 sticky bottom-0 p-2 justify-between">
      <PlusButton toggleExpanded={toggleExpanded} />
      <InputArea
        placeholder={placeholder}
        textAreaRef={textareaRef}
        value={value}
        onChange={handleChange}
        rows={expanded ? 3 : 1}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
          }
        }}
      />
      <SendButton onClick={handleSubmit} />
    </div>
  );
}