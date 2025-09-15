/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Edge } from './Edge';
import type { Node } from './Node';
import type { PlanStep } from './PlanStep';
export type StructuredPlan = {
    steps: Array<PlanStep>;
    final_prompt: string;
    nodes?: (Array<Node> | null);
    edges?: (Array<Edge> | null);
};

