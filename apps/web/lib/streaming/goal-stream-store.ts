import { JSONParser, type JSONParserOptions } from '@streamparser/json';
import { useSyncExternalStore } from 'react';

export type Listener<T> = (v: T) => void;

export interface Var<T> {
    get(): T;
    set(v: T): void;
    subscribe(l: Listener<T>): () => void;
}
export function createVar<T>(): Var<T | undefined>;
export function createVar<T>(initial: T): Var<T>;
export function createVar<T>(initial?: T) {
    let value = initial as T; 
    const listeners = new Set<(v: T) => void>();
    return {
        get: () => value,
        set: (v: T) => {
            value = v;
            listeners.forEach((l) => l(value));
        },
        subscribe: (l: (v: T) => void) => {
            listeners.add(l);
            return () => listeners.delete(l);
        },
    } as Var<T>;
}

export function useVar<T>(v: Var<T>): T {
    return useSyncExternalStore<T>(
        v.subscribe,
        v.get as () => T,
        v.get as () => T
    );
}
export type NodeStatus = string;
export type EdgeBase = Record<string, unknown>;
export type SmarterForGoal = any;

export type GoalNode = {
    nodeId: string;
    title: string;
    status?: NodeStatus;
    parent?: string | null;
    nodes?: Array<GoalNode>;
    edges?: Array<EdgeBase>;
    kind?: string;
    smarter: SmarterForGoal;
};

export type GoalNodeVars = {
    nodeId: Var<string | undefined>;
    title: Var<string | undefined>;
    status: Var<NodeStatus | undefined>;
    parent: Var<string | null | undefined>;
    kind: Var<string | undefined>;
    smarter: Var<SmarterForGoal | undefined>;
    extra: Map<string, Var<unknown>>;
};

function createGoalNodeVars(): GoalNodeVars {
    return {
        nodeId: createVar<string>(),
        title: createVar<string>(),
        status: createVar<NodeStatus>(),
        parent: createVar<string | null>(),
        kind: createVar<string>(),
        smarter: createVar<SmarterForGoal>(),
        extra: new Map(),
    };
}

function deepSet(obj: any, path: Array<string | number>, value: any): any {
    if (path.length === 0) return value;
    const [head, ...rest] = path;
    const isIndex = typeof head === 'number';
    const base = obj ?? (isIndex ? [] : {});
    const clone = Array.isArray(base) ? base.slice() : { ...base };
    (clone as any)[head] = deepSet((clone as any)[head], rest, value);
    return clone;
}

type StackElement = { key: string | number | undefined };

function buildPath(stack: StackElement[], key?: string | number): Array<string | number> {
    const path: Array<string | number> = [];
    for (const s of stack) {
        if (s.key !== undefined) path.push(s.key);
    }
    if (key !== undefined) path.push(key);
    return path;
}

type AssignmentEvent = { path: Array<string | number>; value: unknown };
type NodeKeyEvent = { nodeId: string; key: string; subpath?: Array<string | number>; value: unknown };

export class GoalStreamStore {
    // existing fields...
    private byId = new Map<string, GoalNodeVars>();
    private idxToId = new Map<number, string>();
    private pending = new Map<number, Array<{ key: string; value: unknown; subpath?: Array<string | number> }>>();
    private parser!: JSONParser;
    private parserOpts: JSONParserOptions;

    // NEW: reactive list of nodeIds
    private nodeIdsVar: Var<string[]> = createVar<string[]>([]);

    // NEW: debug subscribers
    private assignmentListeners = new Set<(e: AssignmentEvent) => void>();
    private nodeKeyListeners = new Set<(e: NodeKeyEvent) => void>();

    constructor(opts?: Partial<JSONParserOptions>) {
        this.parserOpts = { keepStack: true, emitPartialValues: false, ...(opts ?? {}) } as JSONParserOptions;
        this.initParser();
    }

    private initParser() {
        const p = new JSONParser(this.parserOpts);
        p.onValue = ({ value, key, stack, partial }) => {
            if (partial) return;
            const path = buildPath(stack as any, key as any);
            this.route(path, value);
        };
        p.onError = (err) => {
            console.error('[GoalStreamStore] parse error:', err);
        };
        this.parser = p;
    }

    write(chunk: string | Uint8Array | number[] | ArrayBufferView) {
        try {
            this.parser.write(chunk as any);
        } catch (err) {
            console.error('[GoalStreamStore] parse error:', err);
            // Auto-recover: reinitialize a fresh parser so we don’t get stuck in state=ERROR
            this.initParser();
            // Do NOT re-write the same (likely malformed) chunk.
        }
    }
    end() { this.parser.end(); }

    getNodeVars(nodeId: string): GoalNodeVars | undefined { return this.byId.get(nodeId); }
    ensureAndGetNodeVars(nodeId: string): GoalNodeVars {
        let vars = this.byId.get(nodeId);
        if (!vars) {
            vars = createGoalNodeVars();
            vars.nodeId.set(nodeId);
            this.byId.set(nodeId, vars);

            // NEW: push into reactive list
            const cur = this.nodeIdsVar.get() ?? [];
            if (!cur.includes(nodeId)) this.nodeIdsVar.set([...cur, nodeId]);
        }
        return vars;
    }
    listNodeIds(): string[] { return [...this.byId.keys()]; }

    // NEW: subscribe to the reactive list of nodeIds (for React)
    useNodeIds(): string[] {
        return useVar(this.nodeIdsVar); // returns string[]
    }

    // NEW: low-level debug subscriptions
    onAssignment(listener: (e: AssignmentEvent) => void) {
        this.assignmentListeners.add(listener);
        return () => this.assignmentListeners.delete(listener);
    }
    onNodeKeyUpdate(listener: (e: NodeKeyEvent) => void) {
        this.nodeKeyListeners.add(listener);
        return () => this.nodeKeyListeners.delete(listener);
    }
    private emitAssignment(e: AssignmentEvent) {
        for (const l of this.assignmentListeners) l(e);
    }
    private emitNodeKeyUpdate(e: NodeKeyEvent) {
        for (const l of this.nodeKeyListeners) l(e);
    }

    private route(path: Array<string | number>, value: unknown) {
        // 🔎 Emit raw path/value events for anything under $.nodes[*]
        if (path.length >= 2 && path[0] === 'nodes') {
            this.emitAssignment({ path, value });
        }
        if (path.length < 3 || path[0] !== 'nodes' || typeof path[1] !== 'number') return;

        const index = path[1] as number;
        const prop = String(path[2]);
        const subpath = path.slice(3);

        if (prop === 'nodeId' && typeof value === 'string') {
            this.idxToId.set(index, value);
            const vars = this.ensureAndGetNodeVars(value);
            vars.nodeId.set(value);

            // replay queued updates now that nodeId is known
            const queue = this.pending.get(index);
            if (queue?.length) {
                for (const u of queue) {
                    this.apply(vars, u.key, u.value, u.subpath);
                    this.emitNodeKeyUpdate({ nodeId: value, key: u.key, subpath: u.subpath, value: u.value });
                }
                this.pending.delete(index);
            }
            return;
        }

        const knownId = this.idxToId.get(index);
        if (knownId) {
            const vars = this.ensureAndGetNodeVars(knownId);
            this.apply(vars, prop, value, subpath);
            // 🔔 Emit a high-level “node key update” for direct consumption
            this.emitNodeKeyUpdate({ nodeId: knownId, key: prop, subpath, value });
        } else {
            const arr = this.pending.get(index) ?? [];
            arr.push({ key: prop, value, subpath });
            this.pending.set(index, arr);
        }
    }

    private apply(vars: GoalNodeVars, key: string, value: unknown, subpath?: Array<string | number>) {
        switch (key) {
            case 'title': vars.title.set(value as string); break;
            case 'status': vars.status.set(value as NodeStatus); break;
            case 'parent': vars.parent.set(value as string | null); break;
            case 'kind': vars.kind.set(value as string); break;
            case 'smarter': {
                const current = vars.smarter.get();
                const next = subpath && subpath.length ? deepSet(current, subpath, value) : value;
                vars.smarter.set(next as SmarterForGoal);
                break;
            }
            default: {
                let v = vars.extra.get(key);
                if (!v) { v = createVar<unknown>(); vars.extra.set(key, v); }
                const current = v.get();
                const next = subpath && subpath.length ? deepSet(current, subpath, value) : value;
                v.set(next);
            }
        }
    }
}