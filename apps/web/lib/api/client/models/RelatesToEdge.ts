/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EdgeStatus } from './EdgeStatus';
export type RelatesToEdge = {
    edgeId: string;
    fromNode: string;
    toNode: string;
    label?: (string | null);
    status?: EdgeStatus;
    createdAt?: (string | null);
    updatedAt?: (string | null);
    metadata?: (Record<string, any> | null);
    kind?: string;
    tags?: Array<string>;
    rationale?: (string | null);
};

