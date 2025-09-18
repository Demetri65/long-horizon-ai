/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Achievable } from './Achievable';
import type { Evaluation } from './Evaluation';
import type { Metric } from './Metric';
import type { Readjustment } from './Readjustment';
import type { Relevant } from './Relevant';
import type { Specific } from './Specific';
import type { TimeBound } from './TimeBound';
export type SmarterForGoalPayload = {
    specific: Specific;
    measurable?: Array<Metric>;
    achievable?: Array<Achievable>;
    relevant: Relevant;
    timeBound: TimeBound;
    evaluate?: Array<Evaluation>;
    readjust?: Array<Readjustment>;
};

