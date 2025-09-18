/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MeasurementUpdate } from './MeasurementUpdate';
import type { ResourceUpdate } from './ResourceUpdate';
import type { TimelineUpdate } from './TimelineUpdate';
export type ReadjustmentChanges = {
    scope?: (string | null);
    measurementUpdates?: Array<MeasurementUpdate>;
    timelineUpdates?: Array<TimelineUpdate>;
    resourceUpdates?: Array<ResourceUpdate>;
};

