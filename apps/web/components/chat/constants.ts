import ELK from "elkjs/lib/elk.bundled.js";

export const CIRCLE_SIZE = 120;  

export const elk = new ELK();
export const elkOptions = {
  "elk.algorithm": "layered",
  "elk.layered.spacing.nodeNodeBetweenLayers": "100",
  "elk.spacing.nodeNode": "80",
} as Record<string, string>;