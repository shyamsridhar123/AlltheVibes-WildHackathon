/**
 * Redis-based Pub/Sub Message Bus
 *
 * Provides topic-based asynchronous communication for agent swarms.
 * Uses Redis pub/sub for reliable, fast message delivery.
 */

import { EventEmitter } from 'events';
import { randomUUID } from 'crypto';
import { createClient, RedisClientType } from 'redis';
import {
  IMessageBus,
  MessageBusConfig,
  BusMessage,
  MessageHandler,
  Subscription,
  SubscriptionId,
  Topic
} from '../types/messageBus.js';
import { logger } from '../utils/logger.js';

/**
 * Redis-based message bus implementation
 */
export class MessageBus extends EventEmitter implements IMessageBus {
  private publishClient?: RedisClientType;
  private subscribeClient?: RedisClientType;
  private subscriptions: Map<SubscriptionId, Subscription>;
  private topicSubscriptions: Map<Topic, Set<SubscriptionId>>;
  private config: Required<MessageBusConfig>;
  private connected: boolean;

  constructor(config: MessageBusConfig = {}) {
    super();

    // Set default configuration
    this.config = {
      redisUrl: config.redisUrl || process.env.REDIS_URL || 'redis://localhost:6379',
      host: config.host || process.env.REDIS_HOST || 'localhost',
      port: config.port || parseInt(process.env.REDIS_PORT || '6379'),
      db: config.db || parseInt(process.env.REDIS_DB || '0'),
      poolSize: config.poolSize || 10,
      connectionTimeout: config.connectionTimeout || 5000,
      persistent: config.persistent || false,
      messageTTL: config.messageTTL || 3600
    };

    this.subscriptions = new Map();
    this.topicSubscriptions = new Map();
    this.connected = false;

    logger.debug('MessageBus initialized with config:', this.config);
  }

  /**
   * Connect to Redis
   */
  async connect(): Promise<void> {
    if (this.connected) {
      logger.warn('MessageBus already connected');
      return;
    }

    try {
      logger.info('Connecting to Redis message bus...');

      // Create publish client
      this.publishClient = createClient({
        url: this.config.redisUrl,
        database: this.config.db,
        socket: {
          connectTimeout: this.config.connectionTimeout
        }
      }) as RedisClientType;

      this.publishClient.on('error', (err) => {
        logger.error('Redis publish client error:', err);
        this.emit('error', err);
      });

      // Create subscribe client (separate connection required for pub/sub)
      this.subscribeClient = createClient({
        url: this.config.redisUrl,
        database: this.config.db,
        socket: {
          connectTimeout: this.config.connectionTimeout
        }
      }) as RedisClientType;

      this.subscribeClient.on('error', (err) => {
        logger.error('Redis subscribe client error:', err);
        this.emit('error', err);
      });

      // Connect both clients
      await Promise.all([
        this.publishClient.connect(),
        this.subscribeClient.connect()
      ]);

      this.connected = true;
      logger.info('Connected to Redis message bus');
      this.emit('connected');
    } catch (error) {
      logger.error('Failed to connect to Redis:', error);
      this.connected = false;
      throw new Error(`Failed to connect to message bus: ${error}`);
    }
  }

  /**
   * Disconnect from Redis
   */
  async disconnect(): Promise<void> {
    if (!this.connected) {
      logger.warn('MessageBus not connected');
      return;
    }

    try {
      logger.info('Disconnecting from Redis message bus...');

      // Unsubscribe from all topics
      for (const [subscriptionId] of this.subscriptions) {
        await this.unsubscribe(subscriptionId);
      }

      // Disconnect clients
      await Promise.all([
        this.publishClient?.quit(),
        this.subscribeClient?.quit()
      ]);

      this.connected = false;
      logger.info('Disconnected from Redis message bus');
      this.emit('disconnected');
    } catch (error) {
      logger.error('Error disconnecting from Redis:', error);
      throw new Error(`Failed to disconnect from message bus: ${error}`);
    }
  }

  /**
   * Publish a message to a topic
   */
  async publish<T = unknown>(
    topic: Topic,
    payload: T,
    from: string,
    metadata?: Record<string, unknown>
  ): Promise<void> {
    if (!this.connected || !this.publishClient) {
      throw new Error('MessageBus not connected');
    }

    const message: BusMessage<T> = {
      id: randomUUID(),
      topic,
      payload,
      from,
      timestamp: new Date(),
      metadata
    };

    try {
      // Publish to Redis channel
      const messageJson = JSON.stringify(message);
      await this.publishClient.publish(topic, messageJson);

      // If persistent, also store in a Redis list with TTL
      if (this.config.persistent) {
        const key = `message:${topic}`;
        await this.publishClient.rPush(key, messageJson);
        await this.publishClient.expire(key, this.config.messageTTL);
      }

      logger.debug(`Published message to topic '${topic}':`, message.id);
      this.emit('message-published', message);
    } catch (error) {
      logger.error(`Failed to publish message to topic '${topic}':`, error);
      throw new Error(`Failed to publish message: ${error}`);
    }
  }

  /**
   * Subscribe to a topic
   */
  async subscribe<T = unknown>(
    topic: Topic,
    handler: MessageHandler<T>,
    subscriberId: string
  ): Promise<SubscriptionId> {
    if (!this.connected || !this.subscribeClient) {
      throw new Error('MessageBus not connected');
    }

    const subscriptionId = randomUUID();
    const subscription: Subscription = {
      id: subscriptionId,
      topic,
      handler: handler as MessageHandler,
      subscriberId,
      createdAt: new Date()
    };

    try {
      // Check if this is the first subscription to this topic
      const isFirstTopicSubscription = !this.topicSubscriptions.has(topic);

      // Store subscription
      this.subscriptions.set(subscriptionId, subscription);

      // Track topic subscription
      if (!this.topicSubscriptions.has(topic)) {
        this.topicSubscriptions.set(topic, new Set());
      }
      this.topicSubscriptions.get(topic)!.add(subscriptionId);

      // Only subscribe to Redis channel if this is the first subscription to this topic
      if (isFirstTopicSubscription) {
        await this.subscribeClient.subscribe(topic, (messageJson: string) => {
          this.handleIncomingMessage(topic, messageJson);
        });
        logger.debug(`Subscribed to Redis channel '${topic}'`);
      }

      logger.info(`Agent ${subscriberId} subscribed to topic '${topic}' (${subscriptionId})`);
      this.emit('subscribed', subscription);

      return subscriptionId;
    } catch (error) {
      // Cleanup on error
      this.subscriptions.delete(subscriptionId);
      this.topicSubscriptions.get(topic)?.delete(subscriptionId);

      logger.error(`Failed to subscribe to topic '${topic}':`, error);
      throw new Error(`Failed to subscribe to topic: ${error}`);
    }
  }

  /**
   * Unsubscribe from a topic
   */
  async unsubscribe(subscriptionId: SubscriptionId): Promise<boolean> {
    const subscription = this.subscriptions.get(subscriptionId);
    if (!subscription) {
      logger.warn(`Subscription not found: ${subscriptionId}`);
      return false;
    }

    try {
      const { topic, subscriberId } = subscription;

      // Remove subscription
      this.subscriptions.delete(subscriptionId);
      this.topicSubscriptions.get(topic)?.delete(subscriptionId);

      // If no more subscriptions to this topic, unsubscribe from Redis
      const topicSubs = this.topicSubscriptions.get(topic);
      if (!topicSubs || topicSubs.size === 0) {
        if (this.subscribeClient) {
          await this.subscribeClient.unsubscribe(topic);
          logger.debug(`Unsubscribed from Redis channel '${topic}'`);
        }
        this.topicSubscriptions.delete(topic);
      }

      logger.info(`Agent ${subscriberId} unsubscribed from topic '${topic}' (${subscriptionId})`);
      this.emit('unsubscribed', subscription);

      return true;
    } catch (error) {
      logger.error(`Failed to unsubscribe: ${subscriptionId}`, error);
      throw new Error(`Failed to unsubscribe: ${error}`);
    }
  }

  /**
   * Unsubscribe all subscriptions for a subscriber
   */
  async unsubscribeAll(subscriberId: string): Promise<number> {
    const subscriptionsToRemove = Array.from(this.subscriptions.values())
      .filter(sub => sub.subscriberId === subscriberId);

    let count = 0;
    for (const subscription of subscriptionsToRemove) {
      const success = await this.unsubscribe(subscription.id);
      if (success) count++;
    }

    logger.info(`Unsubscribed ${count} subscriptions for agent ${subscriberId}`);
    return count;
  }

  /**
   * Get all active subscriptions
   */
  getSubscriptions(): Subscription[] {
    return Array.from(this.subscriptions.values());
  }

  /**
   * Get subscriptions for a specific topic
   */
  getTopicSubscriptions(topic: Topic): Subscription[] {
    const subscriptionIds = this.topicSubscriptions.get(topic);
    if (!subscriptionIds) {
      return [];
    }

    return Array.from(subscriptionIds)
      .map(id => this.subscriptions.get(id))
      .filter((sub): sub is Subscription => sub !== undefined);
  }

  /**
   * Check if connected to message bus
   */
  isConnected(): boolean {
    return this.connected;
  }

  /**
   * Handle incoming message from Redis
   */
  private handleIncomingMessage(topic: Topic, messageJson: string): void {
    try {
      const message: BusMessage = JSON.parse(messageJson);

      // Convert timestamp string back to Date object
      message.timestamp = new Date(message.timestamp);

      logger.debug(`Received message on topic '${topic}':`, message.id);

      // Get all subscriptions for this topic
      const subscriptions = this.getTopicSubscriptions(topic);

      // Invoke all handlers
      for (const subscription of subscriptions) {
        try {
          const result = subscription.handler(message);

          // Handle async handlers
          if (result instanceof Promise) {
            result.catch(error => {
              logger.error(
                `Error in message handler for subscription ${subscription.id}:`,
                error
              );
              this.emit('handler-error', { subscription, error, message });
            });
          }
        } catch (error) {
          logger.error(
            `Error in message handler for subscription ${subscription.id}:`,
            error
          );
          this.emit('handler-error', { subscription, error, message });
        }
      }

      this.emit('message-received', message);
    } catch (error) {
      logger.error(`Failed to process message on topic '${topic}':`, error);
      this.emit('error', error);
    }
  }
}

/**
 * Create a new message bus instance
 */
export function createMessageBus(config?: MessageBusConfig): MessageBus {
  return new MessageBus(config);
}
