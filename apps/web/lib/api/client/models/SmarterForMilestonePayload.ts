/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Achievable } from './Achievable';
import type { Evaluation } from './Evaluation';
import type { Readjustment } from './Readjustment';
import type { Relevant } from './Relevant';
import type { Specific } from './Specific';
export type SmarterForMilestonePayload = {
    specific: Specific;
    achievable?: Array<Achievable>;
    relevant: Relevant;
    evaluate?: Array<Evaluation>;
    readjust?: Array<Readjustment>;
};

