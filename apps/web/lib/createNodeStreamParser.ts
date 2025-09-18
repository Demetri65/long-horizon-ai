import JSONParser from 'jsonparse';

export interface RawNode {
  nodeId?: string;
  title?: string;
  status?: string;
  kind?: string;
  [key: string]: any;
}

export type NodeHandler = (node: RawNode) => void;

/**
 * Creates a streaming parser that accumulates key–value pairs into node objects.
 * When a closing brace is encountered and the node has a nodeId, the complete
 * node is emitted via the provided handler.
 *
 * @param onNodeComplete A callback invoked whenever a node object is complete.
 */
export const createNodeStreamParser = (onNodeComplete: NodeHandler) => {
  // partial node storage keyed by nodeId
  const partialNodes: Record<string, RawNode> = {};

  // Keep track of current key while parsing
  let currentKey: string | null = null;

  // Initialize JSON parser
  const parser = new JSONParser();

  // Called when a token (like '{', '}', etc.) is encountered
  parser.onToken = (token: string) => {
    if (token === '}') {
      const obj = parser.value as RawNode;
      const id = obj?.nodeId;
      if (id) {
        // Merge any previous partial state with current object
        const merged = { ...(partialNodes[id] || {}), ...obj };
        delete partialNodes[id];
        onNodeComplete(merged);
      }
    }
  };

  // Called when a complete value is parsed
  parser.onValue = (value: any) => {
    if (parser.stack && parser.stack.length >= 1) {
      const container = parser.stack[parser.stack.length - 1];

      // New key encountered (strings in object keys)
      if (typeof value === 'string' && currentKey === null && container.key === null) {
        currentKey = value;
        return;
      }

      // Value for the previously read key
      if (currentKey !== null) {
        // Determine the nodeId so we can merge into correct partial object
        let nodeId = (container.value as RawNode).nodeId ?? null;
        if (currentKey === 'nodeId') {
          nodeId = value;
        }

        if (nodeId) {
          const target = partialNodes[nodeId] ?? {};
          (target as any)[currentKey] = value;
          partialNodes[nodeId] = target;
        }

        currentKey = null;
      }
    }
  };

  return (chunk: string | Buffer) => {
    parser.write(chunk);
  };
}