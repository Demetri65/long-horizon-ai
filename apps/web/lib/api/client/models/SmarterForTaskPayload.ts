/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Readjustment } from './Readjustment';
import type { Relevant } from './Relevant';
import type { Specific } from './Specific';
import type { TimeBound } from './TimeBound';
export type SmarterForTaskPayload = {
    specific: Specific;
    relevant: Relevant;
    timeBound: TimeBound;
    readjust?: Array<Readjustment>;
};

