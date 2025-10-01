import { memo } from "react";
import { CIRCLE_SIZE } from "../../constants";
import { GoalNodeProps } from "../../types";
import { Handle, Position } from "@xyflow/react";
import { useScaleNode } from "../hooks/use-scale-node";

export const GoalNode = memo(
  ({ data, sourcePosition, targetPosition, selected }: GoalNodeProps) => {
    const { ref, scale } = useScaleNode();

    return (
      <div
        style={{
          width: CIRCLE_SIZE,
          height: CIRCLE_SIZE,
          borderRadius: "50%",
          background: "transparent",
          border: "2px solid orange-600",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxSizing: "border-box",
          padding: 8,
          containerType: "size",
        }}
        className="border-4 border-solid border-green-600 p-4"
      >
        <div
          ref={ref}
          style={{
            transform: `scale(${scale})`,
            transformOrigin: "center center",
            display: "block",
            maxWidth: "100%",
            maxHeight: "100%",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              fontSize: "clamp(10px, 10cqw, 14px)",
              lineHeight: 1.2,
              textAlign: "center",
              wordBreak: "break-word",
              overflowWrap: "anywhere",
            }}
          >
            <div style={{ fontWeight: 600 }}>{data?.title ?? "(untitled)"}</div>
            {data?.status && <div style={{ opacity: 0.9 }}>{data.status}</div>}
            <div style={{ opacity: 0.6 }}>{data?.nodeId}</div>
            {data?.kind && <div style={{ opacity: 0.6 }}>kind: {data.kind}</div>}
            {data?.parent && <div style={{ opacity: 0.6 }}>parent: {data.parent}</div>}
          </div>
        </div>

        <Handle type="target" position={targetPosition ?? Position.Top} />
        <Handle type="source" position={sourcePosition ?? Position.Bottom} />
      </div>
    );
  }
);
