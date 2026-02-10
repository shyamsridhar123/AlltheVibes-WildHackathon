/**
 * Azure OpenAI Integration
 *
 * Provides a robust client for Azure OpenAI with:
 * - Credential management from environment variables
 * - Retry logic with exponential backoff
 * - Rate limiting
 * - Function calling support
 * - Streaming responses
 * - Comprehensive error handling
 */

import { logger } from '../utils/logger.js';

/**
 * Azure OpenAI Configuration
 */
export interface AzureOpenAIConfig {
  /** Azure OpenAI API endpoint */
  endpoint: string;
  /** Azure OpenAI API key */
  apiKey: string;
  /** Deployment name (model) */
  deploymentName: string;
  /** API version */
  apiVersion?: string;
  /** Maximum retry attempts */
  maxRetries?: number;
  /** Initial retry delay in milliseconds */
  retryDelay?: number;
  /** Maximum retry delay in milliseconds */
  maxRetryDelay?: number;
  /** Request timeout in milliseconds */
  timeout?: number;
  /** Rate limit: maximum requests per minute */
  maxRequestsPerMinute?: number;
}

/**
 * Chat message role
 */
export type ChatRole = 'system' | 'user' | 'assistant' | 'function' | 'tool';

/**
 * Chat message
 */
export interface ChatMessage {
  role: ChatRole;
  content: string;
  name?: string;
  function_call?: FunctionCall;
  tool_calls?: ToolCall[];
}

/**
 * Function call definition
 */
export interface FunctionCall {
  name: string;
  arguments: string;
}

/**
 * Tool call definition
 */
export interface ToolCall {
  id: string;
  type: 'function';
  function: FunctionCall;
}

/**
 * Function definition
 */
export interface FunctionDefinition {
  name: string;
  description?: string;
  parameters?: {
    type: string;
    properties: Record<string, unknown>;
    required?: string[];
  };
}

/**
 * Tool definition
 */
export interface ToolDefinition {
  type: 'function';
  function: FunctionDefinition;
}

/**
 * Chat completion request parameters
 */
export interface ChatCompletionParams {
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  stop?: string | string[];
  functions?: FunctionDefinition[];
  tools?: ToolDefinition[];
  tool_choice?: 'auto' | 'none' | { type: 'function'; function: { name: string } };
  function_call?: 'auto' | 'none' | { name: string };
  stream?: boolean;
}

/**
 * Chat completion response
 */
export interface ChatCompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: ChatMessage;
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

/**
 * Streaming chunk
 */
export interface ChatCompletionChunk {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    delta: Partial<ChatMessage>;
    finish_reason: string | null;
  }>;
}

/**
 * Azure OpenAI Error
 */
export class AzureOpenAIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public code?: string,
    public retryable: boolean = false
  ) {
    super(message);
    this.name = 'AzureOpenAIError';
  }
}

/**
 * Rate limiter using token bucket algorithm
 */
class RateLimiter {
  private tokens: number;
  private lastRefill: number;
  private readonly maxTokens: number;
  private readonly refillRate: number; // tokens per millisecond

  constructor(maxRequestsPerMinute: number) {
    this.maxTokens = maxRequestsPerMinute;
    this.tokens = maxRequestsPerMinute;
    this.lastRefill = Date.now();
    this.refillRate = maxRequestsPerMinute / 60000; // tokens per ms
  }

  /**
   * Refill tokens based on elapsed time
   */
  private refill(): void {
    const now = Date.now();
    const elapsed = now - this.lastRefill;
    const tokensToAdd = elapsed * this.refillRate;

    this.tokens = Math.min(this.maxTokens, this.tokens + tokensToAdd);
    this.lastRefill = now;
  }

  /**
   * Try to acquire a token, wait if necessary
   */
  async acquire(): Promise<void> {
    this.refill();

    if (this.tokens >= 1) {
      this.tokens -= 1;
      return;
    }

    // Calculate wait time for next token
    const waitTime = (1 - this.tokens) / this.refillRate;
    logger.debug(`Rate limit reached, waiting ${Math.round(waitTime)}ms`);

    await new Promise(resolve => setTimeout(resolve, waitTime));
    this.tokens = 0; // consumed the token we waited for
  }
}

/**
 * Azure OpenAI Client
 */
export class AzureOpenAIClient {
  private readonly config: Required<AzureOpenAIConfig>;
  private readonly rateLimiter?: RateLimiter;
  private readonly baseUrl: string;

  constructor(config: AzureOpenAIConfig) {
    // Validate configuration
    if (!config.endpoint) {
      throw new AzureOpenAIError('Azure OpenAI endpoint is required');
    }
    if (!config.apiKey) {
      throw new AzureOpenAIError('Azure OpenAI API key is required');
    }
    if (!config.deploymentName) {
      throw new AzureOpenAIError('Azure OpenAI deployment name is required');
    }

    // Set defaults
    this.config = {
      endpoint: config.endpoint,
      apiKey: config.apiKey,
      deploymentName: config.deploymentName,
      apiVersion: config.apiVersion || '2024-02-15-preview',
      maxRetries: config.maxRetries ?? 3,
      retryDelay: config.retryDelay ?? 1000,
      maxRetryDelay: config.maxRetryDelay ?? 30000,
      timeout: config.timeout ?? 60000,
      maxRequestsPerMinute: config.maxRequestsPerMinute ?? 60,
    };

    // Initialize rate limiter if configured
    if (this.config.maxRequestsPerMinute > 0) {
      this.rateLimiter = new RateLimiter(this.config.maxRequestsPerMinute);
    }

    // Construct base URL
    const endpoint = this.config.endpoint.replace(/\/$/, '');
    this.baseUrl = `${endpoint}/openai/deployments/${this.config.deploymentName}`;

    logger.info(`Azure OpenAI client initialized for deployment: ${this.config.deploymentName}`);
  }

  /**
   * Create a chat completion
   */
  async createChatCompletion(params: ChatCompletionParams): Promise<ChatCompletionResponse> {
    if (params.stream) {
      throw new AzureOpenAIError('Use createChatCompletionStream for streaming responses');
    }

    const response = await this.makeRequest<ChatCompletionResponse>(
      '/chat/completions',
      params
    );

    return response;
  }

  /**
   * Create a streaming chat completion
   */
  async *createChatCompletionStream(
    params: ChatCompletionParams
  ): AsyncGenerator<ChatCompletionChunk, void, unknown> {
    const streamParams = { ...params, stream: true };

    const response = await this.makeStreamingRequest('/chat/completions', streamParams);

    const reader = response.body?.getReader();
    if (!reader) {
      throw new AzureOpenAIError('Response body is not readable');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();

          if (!trimmed || trimmed === 'data: [DONE]') {
            continue;
          }

          if (trimmed.startsWith('data: ')) {
            try {
              const jsonStr = trimmed.slice(6);
              const chunk = JSON.parse(jsonStr) as ChatCompletionChunk;
              yield chunk;
            } catch (error) {
              logger.warn('Failed to parse streaming chunk', { line: trimmed, error });
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * Make an HTTP request with retry logic
   */
  private async makeRequest<T>(
    path: string,
    body: unknown,
    attempt: number = 0
  ): Promise<T> {
    // Apply rate limiting
    if (this.rateLimiter) {
      await this.rateLimiter.acquire();
    }

    const url = `${this.baseUrl}${path}?api-version=${this.config.apiVersion}`;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'api-key': this.config.apiKey,
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Handle non-OK responses
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const error = new AzureOpenAIError(
          errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData.error?.code,
          this.isRetryableError(response.status)
        );

        // Retry if error is retryable and we haven't exceeded max retries
        if (error.retryable && attempt < this.config.maxRetries) {
          const delay = this.calculateRetryDelay(attempt);
          logger.warn(
            `Request failed (attempt ${attempt + 1}/${this.config.maxRetries}), retrying in ${delay}ms`,
            { status: response.status, error: error.message }
          );
          await this.sleep(delay);
          return this.makeRequest<T>(path, body, attempt + 1);
        }

        throw error;
      }

      const data = await response.json();
      return data as T;
    } catch (error) {
      clearTimeout(timeoutId);

      if (error instanceof AzureOpenAIError) {
        throw error;
      }

      // Handle timeout
      if (error instanceof Error && error.name === 'AbortError') {
        const timeoutError = new AzureOpenAIError(
          'Request timeout',
          408,
          'timeout',
          true
        );

        if (attempt < this.config.maxRetries) {
          const delay = this.calculateRetryDelay(attempt);
          logger.warn(
            `Request timeout (attempt ${attempt + 1}/${this.config.maxRetries}), retrying in ${delay}ms`
          );
          await this.sleep(delay);
          return this.makeRequest<T>(path, body, attempt + 1);
        }

        throw timeoutError;
      }

      // Handle network errors
      const networkError = new AzureOpenAIError(
        `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        undefined,
        'network_error',
        true
      );

      if (attempt < this.config.maxRetries) {
        const delay = this.calculateRetryDelay(attempt);
        logger.warn(
          `Network error (attempt ${attempt + 1}/${this.config.maxRetries}), retrying in ${delay}ms`,
          { error: error instanceof Error ? error.message : error }
        );
        await this.sleep(delay);
        return this.makeRequest<T>(path, body, attempt + 1);
      }

      throw networkError;
    }
  }

  /**
   * Make a streaming HTTP request
   */
  private async makeStreamingRequest(
    path: string,
    body: unknown,
    attempt: number = 0
  ): Promise<Response> {
    // Apply rate limiting
    if (this.rateLimiter) {
      await this.rateLimiter.acquire();
    }

    const url = `${this.baseUrl}${path}?api-version=${this.config.apiVersion}`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'api-key': this.config.apiKey,
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const error = new AzureOpenAIError(
          errorData.error?.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData.error?.code,
          this.isRetryableError(response.status)
        );

        if (error.retryable && attempt < this.config.maxRetries) {
          const delay = this.calculateRetryDelay(attempt);
          logger.warn(
            `Streaming request failed (attempt ${attempt + 1}/${this.config.maxRetries}), retrying in ${delay}ms`,
            { status: response.status, error: error.message }
          );
          await this.sleep(delay);
          return this.makeStreamingRequest(path, body, attempt + 1);
        }

        throw error;
      }

      return response;
    } catch (error) {
      if (error instanceof AzureOpenAIError) {
        throw error;
      }

      const networkError = new AzureOpenAIError(
        `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        undefined,
        'network_error',
        true
      );

      if (attempt < this.config.maxRetries) {
        const delay = this.calculateRetryDelay(attempt);
        logger.warn(
          `Streaming network error (attempt ${attempt + 1}/${this.config.maxRetries}), retrying in ${delay}ms`,
          { error: error instanceof Error ? error.message : error }
        );
        await this.sleep(delay);
        return this.makeStreamingRequest(path, body, attempt + 1);
      }

      throw networkError;
    }
  }

  /**
   * Determine if an HTTP status code is retryable
   */
  private isRetryableError(statusCode: number): boolean {
    // Retry on:
    // - 408 Request Timeout
    // - 429 Too Many Requests
    // - 500+ Server errors
    return statusCode === 408 || statusCode === 429 || statusCode >= 500;
  }

  /**
   * Calculate retry delay with exponential backoff
   */
  private calculateRetryDelay(attempt: number): number {
    // Exponential backoff: retryDelay * 2^attempt
    const exponentialDelay = this.config.retryDelay * Math.pow(2, attempt);

    // Add jitter (random value between 0 and 20% of delay)
    const jitter = exponentialDelay * 0.2 * Math.random();

    const delay = exponentialDelay + jitter;

    // Cap at maximum retry delay
    return Math.min(delay, this.config.maxRetryDelay);
  }

  /**
   * Sleep for specified milliseconds
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get configuration
   */
  getConfig(): Readonly<Required<AzureOpenAIConfig>> {
    return { ...this.config };
  }
}

/**
 * Create Azure OpenAI client from environment variables
 */
export function createAzureOpenAIClientFromEnv(): AzureOpenAIClient {
  const endpoint = process.env.AZURE_OPENAI_ENDPOINT;
  const apiKey = process.env.AZURE_OPENAI_API_KEY;
  const deploymentName = process.env.AZURE_OPENAI_DEPLOYMENT_NAME;

  if (!endpoint || !apiKey || !deploymentName) {
    throw new AzureOpenAIError(
      'Missing required environment variables: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME'
    );
  }

  const config: AzureOpenAIConfig = {
    endpoint,
    apiKey,
    deploymentName,
    apiVersion: process.env.AZURE_OPENAI_API_VERSION,
    maxRetries: process.env.AZURE_OPENAI_MAX_RETRIES
      ? parseInt(process.env.AZURE_OPENAI_MAX_RETRIES, 10)
      : undefined,
    retryDelay: process.env.AZURE_OPENAI_RETRY_DELAY
      ? parseInt(process.env.AZURE_OPENAI_RETRY_DELAY, 10)
      : undefined,
    timeout: process.env.AZURE_OPENAI_TIMEOUT
      ? parseInt(process.env.AZURE_OPENAI_TIMEOUT, 10)
      : undefined,
    maxRequestsPerMinute: process.env.AZURE_OPENAI_MAX_REQUESTS_PER_MINUTE
      ? parseInt(process.env.AZURE_OPENAI_MAX_REQUESTS_PER_MINUTE, 10)
      : undefined,
  };

  return new AzureOpenAIClient(config);
}
