/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GoalNode } from '../models/GoalNode';
import type { Graph } from '../models/Graph';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class NodesService {
    /**
     * Get a node
     * @returns GoalNode Successful Response
     * @throws ApiError
     */
    public static nodesGetNode({
        graphId,
        nodeId,
    }: {
        graphId: string,
        nodeId: string,
    }): CancelablePromise<GoalNode> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/graphs/{graph_id}/nodes/{node_id}',
            path: {
                'graph_id': graphId,
                'node_id': nodeId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete a node (and detach edges)
     * @returns Graph Successful Response
     * @throws ApiError
     */
    public static nodesDeleteNode({
        graphId,
        nodeId,
    }: {
        graphId: string,
        nodeId: string,
    }): CancelablePromise<Graph> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/graphs/{graph_id}/nodes/{node_id}',
            path: {
                'graph_id': graphId,
                'node_id': nodeId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Upsert a single node, return full graph
     * @returns Graph Successful Response
     * @throws ApiError
     */
    public static nodesUpsertNode({
        graphId,
        requestBody,
    }: {
        graphId: string,
        requestBody: Record<string, any>,
    }): CancelablePromise<Graph> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/graphs/{graph_id}/nodes',
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
}
