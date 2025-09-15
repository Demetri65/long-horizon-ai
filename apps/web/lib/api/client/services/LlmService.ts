/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LLMRequest } from '../models/LLMRequest';
import type { LLMResponse } from '../models/LLMResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class LlmService {
    /**
     * Structure
     * @returns LLMResponse Successful Response
     * @throws ApiError
     */
    public static llmStructure({
        requestBody,
    }: {
        requestBody: LLMRequest,
    }): CancelablePromise<LLMResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/llm/structure',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
