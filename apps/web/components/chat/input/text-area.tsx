import { HTMLAttributes } from "react";

export type TextAreaProps = {
  placeholder?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  textAreaRef?: React.RefObject<HTMLTextAreaElement>;
  rows?: number;
} & HTMLAttributes<HTMLTextAreaElement>;

export const TextArea = ({ placeholder, value, onChange, textAreaRef, rows }: TextAreaProps) => {
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