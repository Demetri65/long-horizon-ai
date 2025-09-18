import { useState, useEffect } from "react";

export type RawNode = {
  nodeId: string;
  title?: string;
  status?: string;
  parent?: string | null;
  kind?: string;
  smarter?: unknown;
};

/**
 * Incrementally "types" `fullText` and builds node objects as complete key/value pairs appear.
 *
 * - Preserves nested shape (e.g., smarter.specific, smarter.timeBound).
 * - Associates each parsed field with the nearest preceding top-level `"nodeId": "..."`.
 * - Avoids duplicates: primitives inside objects are skipped; nested objects aren’t promoted to root.
 *
 * @param fullText Streaming JSON-like text (grows over time).
 * @param speed    Typewriter delay per character (ms).
 * @returns        `{ displayedText, nodes }`
 */
export const useNodeStream = (fullText: string, speed = 15) => {
  const [displayedText, setDisplayedText] = useState(""), [i, setI] = useState(0);
  const [nodesMap, setNodesMap] = useState<Record<string, any>>({});
  const [id, setId] = useState<string | null>(null);
  const toArr = (m: Record<string, any>): RawNode[] =>
    Object.entries(m).map(([nid, v]) => ({ nodeId: nid, ...v }));

  const balanced = (s: string) => { let c = 0; for (const ch of s) { if (ch === "{") c++; else if (ch === "}") c--; if (c < 0) return false; } return c === 0; };

  // Typewriter
  useEffect(() => {
    if (!fullText || i >= fullText.length) return;
    const t = setTimeout(() => { setDisplayedText(p => p + fullText.charAt(i)); setI(p => p + 1); }, speed);
    return () => clearTimeout(t);
  }, [fullText, i, speed]);

  // Reset on new input
  useEffect(() => { setI(0); setDisplayedText(""); setNodesMap({}); setId(null); }, [fullText]);

  // Parser
  useEffect(() => {
    // 1) nodeId ownership (strings only)
    const idMs = [...displayedText.matchAll(/"nodeId"\s*:\s*"([^"]+)"/g)];
    if (idMs.length) setId(idMs[idMs.length - 1][1]);
    const idAt = (pos: number) => {
      let cur: string | null = null;
      for (const m of idMs) {
        const idx = (m as any).index as number;
        if (idx <= pos) cur = m[1]; else break;
      }
      return cur;
    };

    // 2) Objects: balanced scan + span tracking
    const objSpans: Array<[number, number]> = [];
    const rObjStart = /"([^"]+)"\s*:\s*\{/g;
    const findObjEnd = (s: string, from: number) => {
      let depth = 0, inStr = false, esc = false;
      for (let j = from; j < s.length; j++) {
        const ch = s[j];
        if (inStr) { if (esc) esc = false; else if (ch === "\\") esc = true; else if (ch === '"') inStr = false; continue; }
        if (ch === '"') { inStr = true; continue; }
        if (ch === "{") { depth++; continue; }
        if (ch === "}") { depth--; if (depth === 0) return j + 1; }
      }
      return -1;
    };

    let m: RegExpExecArray | null;
    while ((m = rObjStart.exec(displayedText))) {
      const key = m[1];
      const spanStart = (m as any).index as number;
      const braceStart = spanStart + m[0].length - 1;
      const end = findObjEnd(displayedText, braceStart);
      const owner = idAt(spanStart);
      if (!owner) continue;

      // MINIMAL: if this object starts inside any earlier object span, skip promoting it to root.
      if (objSpans.some(([s, e]) => spanStart > s && spanStart < e)) continue;

      if (end === -1) { objSpans.push([spanStart, displayedText.length + 1]); continue; }

      objSpans.push([spanStart, end]);
      try {
        const v = JSON.parse(displayedText.slice(braceStart, end));
        // On close, remove any root-level duplicates that belong under this object key.
        setNodesMap(prev => {
          const cur = prev[owner] || {};
          const cleaned = { ...cur };
          for (const kk of Object.keys(v)) if (kk in cleaned) delete cleaned[kk];
          return { ...prev, [owner]: { ...cleaned, [key]: { ...(cur[key] || {}), ...v } } };
        });
      } catch { /* ignore until fully valid */ }
    }

    // 3) Primitives outside any object span only
    const rPrim = /"([^"]+)"\s*:\s*("(?:[^"\\]|\\.)*"|\d+(?:\.\d+)?|true|false|null)/g;
    while ((m = rPrim.exec(displayedText))) {
      const start = (m as any).index as number;
      if (objSpans.some(([s, e]) => start >= s && start < e)) continue; // skip inside objects (open/closed)
      const k = m[1]; if (k === "nodeId") continue;
      const owner = idAt(start); if (!owner) continue;

      try {
        const v = JSON.parse(m[2]);
        setNodesMap(prev => ({ ...prev, [owner]: { ...(prev[owner] || {}), [k]: v } }));
      } catch {}
    }
  }, [displayedText]);

  return { displayedText, nodes: toArr(nodesMap) };
};