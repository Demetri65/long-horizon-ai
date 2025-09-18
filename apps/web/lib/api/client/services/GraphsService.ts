/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BulkEdgesRequest } from '../models/BulkEdgesRequest';
import type { BulkNodesRequest } from '../models/BulkNodesRequest';
import type { BulkWriteResponse } from '../models/BulkWriteResponse';
import type { CriticalPathResponse } from '../models/CriticalPathResponse';
import type { RollupResponse } from '../models/RollupResponse';
import type { TopoResponse } from '../models/TopoResponse';
import type { TraverseResponse } from '../models/TraverseResponse';
import type { ValidateResponse } from '../models/ValidateResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class GraphsService {
    /**
     * Bulk upsert nodes
     * @returns BulkWriteResponse Successful Response
     * @throws ApiError
     */
    public static graphBulkNodes({
        graphId,
        requestBody,
    }: {
        graphId: string,
        requestBody: BulkNodesRequest,
    }): CancelablePromise<BulkWriteResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/graphs/{graph_id}/nodes:bulk',
            path: {
                'graph_id': graphId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Bulk upsert edges
     * @returns BulkWriteResponse Successful Response
     * @throws ApiError
     */
    public static graphBulkEdges({
        graphId,
        requestBody,
    }: {
        graphId: string,
        requestBody: BulkEdgesRequest,
    }): CancelablePromise<BulkWriteResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/graphs/{graph_id}/edges:bulk',
            path: {
                'graph_id': graphId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Validate graph invariants
     * @returns ValidateResponse Successful Response
     * @throws ApiError
     */
    public static graphValidateGraph({
        graphId,
    }: {
        graphId: string,
    }): CancelablePromise<ValidateResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/graphs/{graph_id}/validate',
            path: {
                'graph_id': graphId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * BFS traversal over selected edge kinds
     * @returns TraverseResponse Successful Response
     * @throws ApiError
     */
    public static graphTraverseGraph({
        graphId,
        start,
        edgeKinds,
        direction = 'out',
        depth,
    }: {
        graphId: string,
        /**
         * Start nodeId
         */
        start: string,
        /**
         * CSV of edge kinds (dependency,contributes_to,relates_to,validates)
         */
        edgeKinds?: (string | null),
        direction?: string,
        depth?: (number | null),
    }): CancelablePromise<TraverseResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/graphs/{graph_id}/traverse',
            path: {
                'graph_id': graphId,
            },
            query: {
                'start': start,
                'edge_kinds': edgeKinds,
                'direction': direction,
                'depth': depth,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Topological order of dependency DAG
     * @returns TopoResponse Successful Response
     * @throws ApiError
     */
    public static graphTopoOrder({
        graphId,
    }: {
        graphId: string,
    }): CancelablePromise<TopoResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/graphs/{graph_id}/topo',
            path: {
                'graph_id': graphId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Critical path over dependency edges
     * @returns CriticalPathResponse Successful Response
     * @throws ApiError
     */
    public static graphCriticalPath({
        graphId,
    }: {
        graphId: string,
    }): CancelablePromise<CriticalPathResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/graphs/{graph_id}/critical-path',
            path: {
                'graph_id': graphId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Roll up metrics to a goal
     * @returns RollupResponse Successful Response
     * @throws ApiError
     */
    public static graphRollup({
        graphId,
        goal,
    }: {
        graphId: string,
        /**
         * Target goal nodeId
         */
        goal: string,
    }): CancelablePromise<RollupResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/graphs/{graph_id}/rollup',
            path: {
                'graph_id': graphId,
            },
            query: {
                'goal': goal,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
