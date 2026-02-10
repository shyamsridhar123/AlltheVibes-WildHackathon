import { z } from 'zod';

/**
 * Message Bus Type Definitions
 *
 * Core type definitions for the pub/sub message bus used for agent communication.
 * The message bus enables asynchronous, topic-based communication between agents.
 */

/**
 * Message handler callback function
 */
export type MessageHandler<T = unknown> = (message: BusMessage<T>) => void | Promise<void>;

/**
 * Subscription ID for tracking subscriptions
 */
export type SubscriptionId = string;

/**
 * Topic name for routing messages
 */
export type Topic = string;

/**
 * Message sent through the bus
 */
export interface BusMessage<T = unknown> {
  /** Unique message identifier */
  id: string;
  /** Topic the message was published to */
  topic: Topic;
  /** Message payload */
  payload: T;
  /** Sender agent ID */
  from: string;
  /** Timestamp when message was created */
  timestamp: Date;
  /** Correlation ID for tracking related messages */
  correlationId?: string;
  /** Message metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Subscription configuration
 */
export interface Subscription {
  /** Unique subscription identifier */
  id: SubscriptionId;
  /** Topic to subscribe to */
  topic: Topic;
  /** Message handler callback */
  handler: MessageHandler;
  /** Subscriber agent ID */
  subscriberId: string;
  /** When subscription was created */
  createdAt: Date;
}

/**
 * Message bus configuration options
 */
export interface MessageBusConfig {
  /** Redis connection URL */
  redisUrl?: string;
  /** Redis host */
  host?: string;
  /** Redis port */
  port?: number;
  /** Redis database number */
  db?: number;
  /** Connection pool size */
  poolSize?: number;
  /** Connection timeout in milliseconds */
  connectionTimeout?: number;
  /** Enable message persistence */
  persistent?: boolean;
  /** Message TTL in seconds (for persistent messages) */
  messageTTL?: number;
}

/**
 * Message bus interface
 */
export interface IMessageBus {
  /**
   * Connect to the message bus
   */
  connect(): Promise<void>;

  /**
   * Disconnect from the message bus
   */
  disconnect(): Promise<void>;

  /**
   * Publish a message to a topic
   */
  publish<T = unknown>(topic: Topic, payload: T, from: string, metadata?: Record<string, unknown>): Promise<void>;

  /**
   * Subscribe to a topic
   */
  subscribe<T = unknown>(topic: Topic, handler: MessageHandler<T>, subscriberId: string): Promise<SubscriptionId>;

  /**
   * Unsubscribe from a topic
   */
  unsubscribe(subscriptionId: SubscriptionId): Promise<boolean>;

  /**
   * Unsubscribe all subscriptions for a subscriber
   */
  unsubscribeAll(subscriberId: string): Promise<number>;

  /**
   * Get all active subscriptions
   */
  getSubscriptions(): Subscription[];

  /**
   * Get subscriptions for a specific topic
   */
  getTopicSubscriptions(topic: Topic): Subscription[];

  /**
   * Check if connected to message bus
   */
  isConnected(): boolean;
}

/**
 * Zod Schemas for Message Bus Validation
 */

// BusMessage schema
export const BusMessageSchema = z.object({
  id: z.string(),
  topic: z.string(),
  payload: z.unknown(),
  from: z.string(),
  timestamp: z.date(),
  correlationId: z.string().optional(),
  metadata: z.record(z.unknown()).optional()
});

// MessageBusConfig schema
export const MessageBusConfigSchema = z.object({
  redisUrl: z.string().optional(),
  host: z.string().optional(),
  port: z.number().int().min(1).max(65535).optional(),
  db: z.number().int().min(0).max(15).optional(),
  poolSize: z.number().int().min(1).optional(),
  connectionTimeout: z.number().min(0).optional(),
  persistent: z.boolean().optional(),
  messageTTL: z.number().min(0).optional()
});

/**
 * Type guard to check if a value is a valid BusMessage
 */
export function isBusMessage(value: unknown): value is BusMessage {
  try {
    BusMessageSchema.parse(value);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate and parse a bus message object
 */
export function parseBusMessage(value: unknown): BusMessage {
  return BusMessageSchema.parse(value);
}
