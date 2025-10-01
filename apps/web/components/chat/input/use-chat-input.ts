import { useCallback, useEffect, useRef, useState, FormEvent } from "react";

type UseChatInputOptions = {
  onSend: (text: string) => void | Promise<void>;
  collapsedRows?: number;
  expandedRows?: number;
};

export function useChatInput({
  onSend,
  collapsedRows = 1,
  expandedRows = 3,
}: UseChatInputOptions) {
  const [value, setValue] = useState("");
  const [expanded, setExpanded] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  const rows = expanded ? expandedRows : collapsedRows;

  const resize = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  }, []);

  useEffect(() => {
    resize();
  }, [value, rows, resize]);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setValue(e.target.value);
    },
    []
  );

  const handleSubmit = useCallback(
    async (e?: FormEvent) => {
      if (e) e.preventDefault();
      const trimmed = value.trim();
      if (!trimmed) return;

      await onSend(trimmed);
      setValue("");

      const el = textareaRef.current;
      if (el) el.style.height = "auto";
    },
    [onSend, value]
  );

  const onKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        void handleSubmit();
      }
    },
    [handleSubmit]
  );

  const toggleExpanded = useCallback(() => {
    setExpanded((prev) => !prev);
    setTimeout(() => textareaRef.current?.focus(), 0);
  }, []);

  return {
    value,
    setValue,
    rows,
    expanded,
    textareaRef,
    handleChange,
    handleSubmit,
    onKeyDown,
    toggleExpanded,
  };
}