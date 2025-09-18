/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ContributesToEdge } from './ContributesToEdge';
import type { DependencyEdge } from './DependencyEdge';
import type { GoalNode } from './GoalNode';
import type { MilestoneNode } from './MilestoneNode';
import type { NodeStatus } from './NodeStatus';
import type { RelatesToEdge } from './RelatesToEdge';
import type { SmarterForTask } from './SmarterForTask';
import type { ValidatesEdge } from './ValidatesEdge';
export type TaskNode = {
    nodeId: string;
    title: string;
    status?: NodeStatus;
    parent?: (string | null);
    nodes?: Array<(GoalNode | MilestoneNode | TaskNode)>;
    edges?: Array<(DependencyEdge | ContributesToEdge | RelatesToEdge | ValidatesEdge)>;
    kind?: string;
    smarter: SmarterForTask;
};

