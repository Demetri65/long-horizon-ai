'use client';
import * as React from 'react';
import { UIMessage } from 'ai';

type Props = { message: UIMessage };

export const Message: React.FC<Props> = ({ message }) => {
  const text = message.parts
    .filter((p) => p.type === 'text')
    .map((p: any) => p.text)
    .join('');

  return (
    <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
      <div
        className={`p-2 rounded-md text-base whitespace-pre-line leading-normal "bg-zinc-800 text-slate-100 max-w-s rounded-full"
          }`}
      >
        {message.role === "user" && <span className="text-gray-100">{text}</span>}
      </div>
    </div>
  );
};