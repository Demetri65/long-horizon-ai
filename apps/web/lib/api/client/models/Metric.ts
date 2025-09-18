/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MetricType } from './MetricType';
export type Metric = {
    metricId: string;
    name: string;
    type: MetricType;
    value: (number | string);
    target: (number | string);
    unit?: (string | null);
    description: string;
};

