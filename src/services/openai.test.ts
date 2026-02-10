/**
 * Azure OpenAI Integration Tests
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  AzureOpenAIClient,
  AzureOpenAIConfig,
  AzureOpenAIError,
  createAzureOpenAIClientFromEnv,
  ChatCompletionParams,
  ChatCompletionResponse,
  ChatCompletionChunk,
} from './openai.js';

// Mock fetch globally
global.fetch = vi.fn();

describe('AzureOpenAIClient', () => {
  let config: AzureOpenAIConfig;
  let client: AzureOpenAIClient;

  beforeEach(() => {
    config = {
      endpoint: 'https://test.openai.azure.com',
      apiKey: 'test-api-key',
      deploymentName: 'gpt-4',
      apiVersion: '2024-02-15-preview',
      maxRetries: 2,
      retryDelay: 100,
      maxRetryDelay: 1000,
      timeout: 5000,
      maxRequestsPerMinute: 60,
    };
    client = new AzureOpenAIClient(config);
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('constructor', () => {
    it('should create client with valid config', () => {
      expect(client).toBeInstanceOf(AzureOpenAIClient);
      expect(client.getConfig().endpoint).toBe(config.endpoint);
      expect(client.getConfig().deploymentName).toBe(config.deploymentName);
    });

    it('should throw error if endpoint is missing', () => {
      expect(() => {
        new AzureOpenAIClient({ ...config, endpoint: '' });
      }).toThrow('Azure OpenAI endpoint is required');
    });

    it('should throw error if apiKey is missing', () => {
      expect(() => {
        new AzureOpenAIClient({ ...config, apiKey: '' });
      }).toThrow('Azure OpenAI API key is required');
    });

    it('should throw error if deploymentName is missing', () => {
      expect(() => {
        new AzureOpenAIClient({ ...config, deploymentName: '' });
      }).toThrow('Azure OpenAI deployment name is required');
    });

    it('should use default values for optional config', () => {
      const minimalConfig: AzureOpenAIConfig = {
        endpoint: 'https://test.openai.azure.com',
        apiKey: 'test-key',
        deploymentName: 'gpt-4',
      };
      const minimalClient = new AzureOpenAIClient(minimalConfig);
      const fullConfig = minimalClient.getConfig();

      expect(fullConfig.apiVersion).toBe('2024-02-15-preview');
      expect(fullConfig.maxRetries).toBe(3);
      expect(fullConfig.retryDelay).toBe(1000);
      expect(fullConfig.timeout).toBe(60000);
    });
  });

  describe('createChatCompletion', () => {
    const mockResponse: ChatCompletionResponse = {
      id: 'test-id',
      object: 'chat.completion',
      created: Date.now(),
      model: 'gpt-4',
      choices: [
        {
          index: 0,
          message: {
            role: 'assistant',
            content: 'Hello! How can I help you?',
          },
          finish_reason: 'stop',
        },
      ],
      usage: {
        prompt_tokens: 10,
        completion_tokens: 20,
        total_tokens: 30,
      },
    };

    it('should make successful chat completion request', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const params: ChatCompletionParams = {
        messages: [
          { role: 'system', content: 'You are a helpful assistant.' },
          { role: 'user', content: 'Hello!' },
        ],
        temperature: 0.7,
        max_tokens: 100,
      };

      const response = await client.createChatCompletion(params);

      expect(response).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledTimes(1);

      const [url, options] = (global.fetch as any).mock.calls[0];
      expect(url).toContain('/chat/completions');
      expect(url).toContain('api-version=2024-02-15-preview');
      expect(options.method).toBe('POST');
      expect(options.headers['api-key']).toBe('test-api-key');
    });

    it('should throw error when streaming is requested', async () => {
      const params: ChatCompletionParams = {
        messages: [{ role: 'user', content: 'Hello!' }],
        stream: true,
      };

      await expect(client.createChatCompletion(params)).rejects.toThrow(
        'Use createChatCompletionStream for streaming responses'
      );
    });

    it('should retry on retryable errors', async () => {
      // First call fails with 500, second succeeds
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: false,
          status: 500,
          statusText: 'Internal Server Error',
          json: async () => ({ error: { message: 'Server error' } }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        });

      const params: ChatCompletionParams = {
        messages: [{ role: 'user', content: 'Hello!' }],
      };

      const response = await client.createChatCompletion(params);

      expect(response).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    it('should not retry on non-retryable errors', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({ error: { message: 'Invalid request' } }),
      });

      const params: ChatCompletionParams = {
        messages: [{ role: 'user', content: 'Hello!' }],
      };

      await expect(client.createChatCompletion(params)).rejects.toThrow(
        AzureOpenAIError
      );
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should throw error after max retries', async () => {
      (global.fetch as any).mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: { message: 'Server error' } }),
      });

      const params: ChatCompletionParams = {
        messages: [{ role: 'user', content: 'Hello!' }],
      };

      await expect(client.createChatCompletion(params)).rejects.toThrow(
        AzureOpenAIError
      );
      // Initial attempt + 2 retries = 3 calls
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });

    it('should handle function calling', async () => {
      const functionResponse: ChatCompletionResponse = {
        ...mockResponse,
        choices: [
          {
            index: 0,
            message: {
              role: 'assistant',
              content: '',
              function_call: {
                name: 'get_weather',
                arguments: '{"location": "San Francisco"}',
              },
            },
            finish_reason: 'function_call',
          },
        ],
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => functionResponse,
      });

      const params: ChatCompletionParams = {
        messages: [{ role: 'user', content: 'What is the weather in SF?' }],
        functions: [
          {
            name: 'get_weather',
            description: 'Get the current weather',
            parameters: {
              type: 'object',
              properties: {
                location: { type: 'string' },
              },
              required: ['location'],
            },
          },
        ],
      };

      const response = await client.createChatCompletion(params);

      expect(response.choices[0].message.function_call).toBeDefined();
      expect(response.choices[0].message.function_call?.name).toBe('get_weather');
    });

    it('should handle tool calling', async () => {
      const toolResponse: ChatCompletionResponse = {
        ...mockResponse,
        choices: [
          {
            index: 0,
            message: {
              role: 'assistant',
              content: '',
              tool_calls: [
                {
                  id: 'call_123',
                  type: 'function',
                  function: {
                    name: 'search_database',
                    arguments: '{"query": "test"}',
                  },
                },
              ],
            },
            finish_reason: 'tool_calls',
          },
        ],
      };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => toolResponse,
      });

      const params: ChatCompletionParams = {
        messages: [{ role: 'user', content: 'Search for test' }],
        tools: [
          {
            type: 'function',
            function: {
              name: 'search_database',
              description: 'Search the database',
              parameters: {
                type: 'object',
                properties: {
                  query: { type: 'string' },
                },
                required: ['query'],
              },
            },
          },
        ],
      };

      const response = await client.createChatCompletion(params);

      expect(response.choices[0].message.tool_calls).toBeDefined();
      expect(response.choices[0].message.tool_calls?.[0].function.name).toBe(
        'search_database'
      );
    });
  });

  describe('createChatCompletionStream', () => {
    it('should handle streaming responses', async () => {
      const mockChunks = [
        'data: {"id":"1","object":"chat.completion.chunk","created":1234,"model":"gpt-4","choices":[{"index":0,"delta":{"role":"assistant","content":"Hello"},"finish_reason":null}]}\n',
        'data: {"id":"1","object":"chat.completion.chunk","created":1234,"model":"gpt-4","choices":[{"index":0,"delta":{"content":" there"},"finish_reason":null}]}\n',
        'data: {"id":"1","object":"chat.completion.chunk","created":1234,"model":"gpt-4","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}\n',
        'data: [DONE]\n',
      ];

      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        async start(controller) {
          for (const chunk of mockChunks) {
            controller.enqueue(encoder.encode(chunk));
          }
          controller.close();
        },
      });

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        body: stream,
      });

      const params: ChatCompletionParams = {
        messages: [{ role: 'user', content: 'Hello!' }],
      };

      const chunks: ChatCompletionChunk[] = [];
      for await (const chunk of client.createChatCompletionStream(params)) {
        chunks.push(chunk);
      }

      expect(chunks).toHaveLength(3);
      expect(chunks[0].choices[0].delta.content).toBe('Hello');
      expect(chunks[1].choices[0].delta.content).toBe(' there');
      expect(chunks[2].choices[0].finish_reason).toBe('stop');
    });

    it('should handle malformed streaming chunks gracefully', async () => {
      const mockChunks = [
        'data: {"id":"1","object":"chat.completion.chunk","created":1234,"model":"gpt-4","choices":[{"index":0,"delta":{"content":"Good"},"finish_reason":null}]}\n',
        'data: invalid json\n',
        'data: {"id":"1","object":"chat.completion.chunk","created":1234,"model":"gpt-4","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":"stop"}]}\n',
        'data: [DONE]\n',
      ];

      const encoder = new TextEncoder();
      const stream = new ReadableStream({
        async start(controller) {
          for (const chunk of mockChunks) {
            controller.enqueue(encoder.encode(chunk));
          }
          controller.close();
        },
      });

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        body: stream,
      });

      const params: ChatCompletionParams = {
        messages: [{ role: 'user', content: 'Hello!' }],
      };

      const chunks: ChatCompletionChunk[] = [];
      for await (const chunk of client.createChatCompletionStream(params)) {
        chunks.push(chunk);
      }

      // Should skip the malformed chunk
      expect(chunks).toHaveLength(2);
      expect(chunks[0].choices[0].delta.content).toBe('Good');
      expect(chunks[1].choices[0].delta.content).toBe('!');
    });
  });

  describe('rate limiting', () => {
    it('should apply rate limiting', async () => {
      const fastClient = new AzureOpenAIClient({
        ...config,
        maxRequestsPerMinute: 2, // Very low rate limit for testing
      });

      const mockResponse: ChatCompletionResponse = {
        id: 'test-id',
        object: 'chat.completion',
        created: Date.now(),
        model: 'gpt-4',
        choices: [
          {
            index: 0,
            message: { role: 'assistant', content: 'Response' },
            finish_reason: 'stop',
          },
        ],
        usage: {
          prompt_tokens: 10,
          completion_tokens: 10,
          total_tokens: 20,
        },
      };

      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockResponse,
      });

      const params: ChatCompletionParams = {
        messages: [{ role: 'user', content: 'Hello!' }],
      };

      // Make 3 rapid requests
      const startTime = Date.now();
      await fastClient.createChatCompletion(params);
      await fastClient.createChatCompletion(params);
      await fastClient.createChatCompletion(params);
      const duration = Date.now() - startTime;

      // Third request should have been rate limited
      // With 2 requests per minute, we need ~30 seconds per request
      // The third request should be delayed
      expect(duration).toBeGreaterThan(100); // Some delay occurred
    });
  });

  describe('error handling', () => {
    it('should create AzureOpenAIError with correct properties', () => {
      const error = new AzureOpenAIError('Test error', 500, 'server_error', true);

      expect(error.message).toBe('Test error');
      expect(error.statusCode).toBe(500);
      expect(error.code).toBe('server_error');
      expect(error.retryable).toBe(true);
      expect(error.name).toBe('AzureOpenAIError');
    });

    it('should handle network errors', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network failure'));

      const params: ChatCompletionParams = {
        messages: [{ role: 'user', content: 'Hello!' }],
      };

      await expect(client.createChatCompletion(params)).rejects.toThrow(
        'Network error'
      );
    });
  });
});

describe('createAzureOpenAIClientFromEnv', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it('should create client from environment variables', () => {
    process.env.AZURE_OPENAI_ENDPOINT = 'https://test.openai.azure.com';
    process.env.AZURE_OPENAI_API_KEY = 'test-key';
    process.env.AZURE_OPENAI_DEPLOYMENT_NAME = 'gpt-4';

    const client = createAzureOpenAIClientFromEnv();

    expect(client).toBeInstanceOf(AzureOpenAIClient);
    expect(client.getConfig().endpoint).toBe('https://test.openai.azure.com');
    expect(client.getConfig().deploymentName).toBe('gpt-4');
  });

  it('should use optional environment variables', () => {
    process.env.AZURE_OPENAI_ENDPOINT = 'https://test.openai.azure.com';
    process.env.AZURE_OPENAI_API_KEY = 'test-key';
    process.env.AZURE_OPENAI_DEPLOYMENT_NAME = 'gpt-4';
    process.env.AZURE_OPENAI_API_VERSION = '2023-12-01-preview';
    process.env.AZURE_OPENAI_MAX_RETRIES = '5';
    process.env.AZURE_OPENAI_TIMEOUT = '30000';

    const client = createAzureOpenAIClientFromEnv();

    expect(client.getConfig().apiVersion).toBe('2023-12-01-preview');
    expect(client.getConfig().maxRetries).toBe(5);
    expect(client.getConfig().timeout).toBe(30000);
  });

  it('should throw error if required env vars are missing', () => {
    delete process.env.AZURE_OPENAI_ENDPOINT;
    delete process.env.AZURE_OPENAI_API_KEY;
    delete process.env.AZURE_OPENAI_DEPLOYMENT_NAME;

    expect(() => createAzureOpenAIClientFromEnv()).toThrow(
      'Missing required environment variables'
    );
  });
});
