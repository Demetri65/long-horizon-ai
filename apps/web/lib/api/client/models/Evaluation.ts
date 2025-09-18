/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EvaluationHistoryEntry } from './EvaluationHistoryEntry';
import type { Frequency } from './Frequency';
export type Evaluation = {
    evalId: number;
    criteria?: Array<string>;
    metrics?: Array<string>;
    frequency: Frequency;
    methods?: Array<string>;
    outcome: string;
    history?: Array<EvaluationHistoryEntry>;
};

