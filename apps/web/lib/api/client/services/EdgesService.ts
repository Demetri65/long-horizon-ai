/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Graph } from '../models/Graph';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class EdgesService {
    /**
     * Upsert a single edge, return full graph
     * @returns Graph Successful Response
     * @throws ApiError
     */
    public static edgesUpsertEdge({
        graphId,
        requestBody,
    }: {
        graphId: string,
        requestBody: Record<string, any>,
    }): CancelablePromise<Graph> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/graphs/{graph_id}/edges',
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
     * Delete an edge by id, return full graph
     * @returns Graph Successful Response
     * @throws ApiError
     */
    public static edgesDeleteEdge({
        graphId,
        edgeId,
    }: {
        graphId: string,
        edgeId: string,
    }): CancelablePromise<Graph> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/graphs/{graph_id}/edges/{edge_id}',
            path: {
                'graph_id': graphId,
                'edge_id': edgeId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
