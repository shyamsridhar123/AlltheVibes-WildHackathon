# Services

External service integrations for the Agent Swarm Platform.

## Azure OpenAI Integration

The Azure OpenAI service provides GPT-4 powered intelligence for agents.

### Features

- **Credential Management**: Environment-based configuration for secure credential storage
- **Retry Logic**: Exponential backoff with configurable retry attempts
- **Rate Limiting**: Token bucket algorithm to prevent API quota exhaustion
- **Function Calling**: Native support for GPT-4 function calling
- **Streaming**: Efficient streaming responses for real-time interactions
- **Error Handling**: Comprehensive error handling with detailed error types

### Quick Start

```typescript
import { createAzureOpenAIClientFromEnv } from './services/openai.js';

// Create client from environment variables
const client = createAzureOpenAIClientFromEnv();

// Basic chat completion
const response = await client.createChatCompletion({
  messages: [
    { role: 'system', content: 'You are a helpful assistant.' },
    { role: 'user', content: 'Hello!' }
  ],
  temperature: 0.7,
  max_tokens: 100
});

console.log(response.choices[0].message.content);
```

### Streaming Responses

```typescript
// Stream responses for real-time output
for await (const chunk of client.createChatCompletionStream({
  messages: [{ role: 'user', content: 'Tell me a story' }],
  temperature: 0.8
})) {
  const content = chunk.choices[0]?.delta?.content;
  if (content) {
    process.stdout.write(content);
  }
}
```

### Function Calling

```typescript
const response = await client.createChatCompletion({
  messages: [
    { role: 'user', content: 'What is the weather in San Francisco?' }
  ],
  functions: [
    {
      name: 'get_weather',
      description: 'Get the current weather for a location',
      parameters: {
        type: 'object',
        properties: {
          location: { type: 'string' },
          unit: { type: 'string', enum: ['celsius', 'fahrenheit'] }
        },
        required: ['location']
      }
    }
  ]
});

if (response.choices[0].message.function_call) {
  const { name, arguments: args } = response.choices[0].message.function_call;
  console.log(`Function: ${name}`);
  console.log(`Arguments: ${args}`);
}
```

### Tool Calling (Newer API)

```typescript
const response = await client.createChatCompletion({
  messages: [
    { role: 'user', content: 'Search for recent AI papers' }
  ],
  tools: [
    {
      type: 'function',
      function: {
        name: 'search_papers',
        description: 'Search academic papers',
        parameters: {
          type: 'object',
          properties: {
            query: { type: 'string' },
            year: { type: 'number' }
          },
          required: ['query']
        }
      }
    }
  ],
  tool_choice: 'auto'
});
```

### Configuration

Set the following environment variables in your `.env` file:

#### Required
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Your model deployment name (e.g., `gpt-4`)

#### Optional
- `AZURE_OPENAI_API_VERSION`: API version (default: `2024-02-15-preview`)
- `AZURE_OPENAI_MAX_RETRIES`: Maximum retry attempts (default: `3`)
- `AZURE_OPENAI_RETRY_DELAY`: Initial retry delay in ms (default: `1000`)
- `AZURE_OPENAI_TIMEOUT`: Request timeout in ms (default: `60000`)
- `AZURE_OPENAI_MAX_REQUESTS_PER_MINUTE`: Rate limit (default: `60`)

### Error Handling

```typescript
import { AzureOpenAIError } from './services/openai.js';

try {
  const response = await client.createChatCompletion({
    messages: [{ role: 'user', content: 'Hello!' }]
  });
} catch (error) {
  if (error instanceof AzureOpenAIError) {
    console.error(`OpenAI Error: ${error.message}`);
    console.error(`Status: ${error.statusCode}`);
    console.error(`Code: ${error.code}`);
    console.error(`Retryable: ${error.retryable}`);
  }
}
```

### Advanced Configuration

```typescript
import { AzureOpenAIClient } from './services/openai.js';

const client = new AzureOpenAIClient({
  endpoint: 'https://your-resource.openai.azure.com',
  apiKey: 'your-api-key',
  deploymentName: 'gpt-4',
  apiVersion: '2024-02-15-preview',
  maxRetries: 5,
  retryDelay: 2000,
  maxRetryDelay: 60000,
  timeout: 120000,
  maxRequestsPerMinute: 30
});
```

### Testing

Run the test suite:

```bash
npm test src/services/openai.test.ts
```

### Best Practices

1. **Always use environment variables** for credentials
2. **Enable rate limiting** to prevent quota exhaustion
3. **Set appropriate timeouts** based on your use case
4. **Handle errors gracefully** and provide fallback mechanisms
5. **Use streaming** for long-form content generation
6. **Monitor token usage** to control costs
7. **Implement retry logic** for production reliability

### Integration with Agents

```typescript
import { BaseAgent } from '../agents/BaseAgent.js';
import { createAzureOpenAIClientFromEnv } from '../services/openai.js';

class IntelligentAgent extends BaseAgent {
  private openai = createAzureOpenAIClientFromEnv();

  async execute(task: Task): Promise<unknown> {
    const response = await this.openai.createChatCompletion({
      messages: [
        { role: 'system', content: 'You are an intelligent agent.' },
        { role: 'user', content: task.payload as string }
      ],
      temperature: 0.7
    });

    return response.choices[0].message.content;
  }
}
```
