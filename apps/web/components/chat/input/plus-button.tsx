import { Plus } from "lucide-react";
import { Button } from "../../ui/button";

export type PlusButtonProps = {
  toggleExpanded: () => void;
};

export const PlusButton = ({ toggleExpanded }: PlusButtonProps) => {
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