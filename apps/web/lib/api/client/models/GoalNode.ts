/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EdgeBase } from './EdgeBase';
import type { NodeStatus } from './NodeStatus';
import type { SmarterForGoal } from './SmarterForGoal';
export type GoalNode = {
    nodeId: string;
    title: string;
    status?: NodeStatus;
    parent?: (string | null);
    nodes?: Array<GoalNode>;
    edges?: Array<EdgeBase>;
    kind?: string;
    smarter: SmarterForGoal;
};

