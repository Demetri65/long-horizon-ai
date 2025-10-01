import { ArrowUp } from "lucide-react";
import { Button } from "../../ui/button";
import { HTMLAttributes } from "react";

export type SendButtonProps = HTMLAttributes<HTMLButtonElement>

export const SendButton = (props: SendButtonProps) => {
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

