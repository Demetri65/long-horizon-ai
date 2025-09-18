/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ContributesToEdge } from './ContributesToEdge';
import type { DependencyEdge } from './DependencyEdge';
import type { GoalNode } from './GoalNode';
import type { MilestoneNode } from './MilestoneNode';
import type { RelatesToEdge } from './RelatesToEdge';
import type { TaskNode } from './TaskNode';
import type { ValidatesEdge } from './ValidatesEdge';
export type Graph = {
    graphId: string;
    nodes?: Array<(GoalNode | MilestoneNode | TaskNode)>;
    edges?: Array<(DependencyEdge | ContributesToEdge | RelatesToEdge | ValidatesEdge)>;
};

