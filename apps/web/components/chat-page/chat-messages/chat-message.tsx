
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export const ChatMessage = ({ id, role, content }: ChatMessage) => {
  return (
    <div key={id} className={`flex ${role === "user" ? "justify-end" : "justify-start"}`}>
      <div
        className={`p-2 rounded-md text-base whitespace-pre-line leading-normal ${role === "user" ? "bg-zinc-800 text-slate-100 max-w-s rounded-full" : " text-gray-100 bg-transparent "
          }`}
      >
        {content}
      </div>
    </div>
  )
}