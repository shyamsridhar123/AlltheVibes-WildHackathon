/**
 * Message Bus Unit Tests
 *
 * Tests the Redis-based pub/sub message bus with mocking.
 * No real Redis connection needed for these tests.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { EventEmitter } from 'events';
import { MessageBus } from './messageBus.js';
import type { BusMessage, MessageHandler } from '../types/messageBus.js';

// Mock Redis client
class MockRedisClient extends EventEmitter {
  private channels: Map<string, (message: string) => void> = new Map();
  private static publishedMessages: Map<string, string[]> = new Map();

  async connect() {
    return Promise.resolve();
  }

  async quit() {
    return Promise.resolve();
  }

  async publish(channel: string, message: string) {
    // Store published message
    if (!MockRedisClient.publishedMessages.has(channel)) {
      MockRedisClient.publishedMessages.set(channel, []);
    }
    MockRedisClient.publishedMessages.get(channel)!.push(message);

    // Simulate pub/sub - deliver to subscribers
    const handler = this.channels.get(channel);
    if (handler) {
      // Simulate async delivery
      setImmediate(() => handler(message));
    }

    return Promise.resolve(1);
  }

  async subscribe(channel: string, handler: (message: string) => void) {
    this.channels.set(channel, handler);
    return Promise.resolve();
  }

  async unsubscribe(channel: string) {
    this.channels.delete(channel);
    return Promise.resolve();
  }

  async rPush(key: string, value: string) {
    return Promise.resolve(1);
  }

  async expire(key: string, seconds: number) {
    return Promise.resolve(true);
  }

  static getPublishedMessages(channel: string): string[] {
    return MockRedisClient.publishedMessages.get(channel) || [];
  }

  static clearPublishedMessages() {
    MockRedisClient.publishedMessages.clear();
  }
}

// Mock the redis module
vi.mock('redis', () => ({
  createClient: vi.fn(() => new MockRedisClient())
}));

describe('MessageBus', () => {
  let messageBus: MessageBus;

  beforeEach(() => {
    MockRedisClient.clearPublishedMessages();
    messageBus = new MessageBus({
      host: 'localhost',
      port: 6379,
      db: 0
    });
  });

  afterEach(async () => {
    if (messageBus.isConnected()) {
      await messageBus.disconnect();
    }
  });

  describe('Connection Management', () => {
    it('should connect to Redis', async () => {
      expect(messageBus.isConnected()).toBe(false);
      await messageBus.connect();
      expect(messageBus.isConnected()).toBe(true);
    });

    it('should disconnect from Redis', async () => {
      await messageBus.connect();
      expect(messageBus.isConnected()).toBe(true);
      await messageBus.disconnect();
      expect(messageBus.isConnected()).toBe(false);
    });

    it('should emit connected event on connect', async () => {
      const connectedSpy = vi.fn();
      messageBus.on('connected', connectedSpy);

      await messageBus.connect();

      expect(connectedSpy).toHaveBeenCalledTimes(1);
    });

    it('should emit disconnected event on disconnect', async () => {
      const disconnectedSpy = vi.fn();
      messageBus.on('disconnected', disconnectedSpy);

      await messageBus.connect();
      await messageBus.disconnect();

      expect(disconnectedSpy).toHaveBeenCalledTimes(1);
    });

    it('should not connect twice', async () => {
      await messageBus.connect();
      await messageBus.connect(); // Should log warning but not fail
      expect(messageBus.isConnected()).toBe(true);
    });

    it('should handle disconnect when not connected', async () => {
      expect(messageBus.isConnected()).toBe(false);
      await messageBus.disconnect(); // Should log warning but not fail
      expect(messageBus.isConnected()).toBe(false);
    });
  });

  describe('Publishing Messages', () => {
    beforeEach(async () => {
      await messageBus.connect();
    });

    it('should publish a message to a topic', async () => {
      const topic = 'test-topic';
      const payload = { data: 'test' };
      const from = 'agent-1';

      await messageBus.publish(topic, payload, from);

      const messages = MockRedisClient.getPublishedMessages(topic);
      expect(messages).toHaveLength(1);

      const message: BusMessage = JSON.parse(messages[0]);
      expect(message.topic).toBe(topic);
      expect(message.payload).toEqual(payload);
      expect(message.from).toBe(from);
      expect(message.id).toBeDefined();
      expect(message.timestamp).toBeDefined();
    });

    it('should publish message with metadata', async () => {
      const topic = 'test-topic';
      const payload = { data: 'test' };
      const from = 'agent-1';
      const metadata = { priority: 'high', category: 'urgent' };

      await messageBus.publish(topic, payload, from, metadata);

      const messages = MockRedisClient.getPublishedMessages(topic);
      const message: BusMessage = JSON.parse(messages[0]);

      expect(message.metadata).toEqual(metadata);
    });

    it('should emit message-published event', async () => {
      const publishedSpy = vi.fn();
      messageBus.on('message-published', publishedSpy);

      await messageBus.publish('test-topic', { data: 'test' }, 'agent-1');

      expect(publishedSpy).toHaveBeenCalledTimes(1);
      expect(publishedSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          topic: 'test-topic',
          from: 'agent-1'
        })
      );
    });

    it('should throw error when not connected', async () => {
      await messageBus.disconnect();

      await expect(
        messageBus.publish('test-topic', { data: 'test' }, 'agent-1')
      ).rejects.toThrow('MessageBus not connected');
    });
  });

  describe('Subscribing to Topics', () => {
    beforeEach(async () => {
      await messageBus.connect();
    });

    it('should subscribe to a topic', async () => {
      const topic = 'test-topic';
      const handler: MessageHandler = vi.fn();
      const subscriberId = 'agent-1';

      const subscriptionId = await messageBus.subscribe(topic, handler, subscriberId);

      expect(subscriptionId).toBeDefined();
      expect(typeof subscriptionId).toBe('string');
    });

    it('should receive published messages', async () => {
      const topic = 'test-topic';
      const handler: MessageHandler = vi.fn();
      const subscriberId = 'agent-1';

      await messageBus.subscribe(topic, handler, subscriberId);

      const payload = { data: 'test' };
      await messageBus.publish(topic, payload, 'agent-2');

      // Wait for async message delivery
      await new Promise(resolve => setImmediate(resolve));

      expect(handler).toHaveBeenCalledTimes(1);
      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({
          topic,
          payload,
          from: 'agent-2'
        })
      );
    });

    it('should handle multiple subscribers to same topic', async () => {
      const topic = 'test-topic';
      const handler1: MessageHandler = vi.fn();
      const handler2: MessageHandler = vi.fn();

      await messageBus.subscribe(topic, handler1, 'agent-1');
      await messageBus.subscribe(topic, handler2, 'agent-2');

      await messageBus.publish(topic, { data: 'test' }, 'agent-3');

      // Wait for async message delivery
      await new Promise(resolve => setImmediate(resolve));

      expect(handler1).toHaveBeenCalledTimes(1);
      expect(handler2).toHaveBeenCalledTimes(1);
    });

    it('should handle multiple topics', async () => {
      const handler1: MessageHandler = vi.fn();
      const handler2: MessageHandler = vi.fn();

      await messageBus.subscribe('topic-1', handler1, 'agent-1');
      await messageBus.subscribe('topic-2', handler2, 'agent-1');

      await messageBus.publish('topic-1', { data: 'test1' }, 'agent-2');
      await messageBus.publish('topic-2', { data: 'test2' }, 'agent-2');

      // Wait for async message delivery
      await new Promise(resolve => setImmediate(resolve));

      expect(handler1).toHaveBeenCalledTimes(1);
      expect(handler2).toHaveBeenCalledTimes(1);
    });

    it('should emit subscribed event', async () => {
      const subscribedSpy = vi.fn();
      messageBus.on('subscribed', subscribedSpy);

      await messageBus.subscribe('test-topic', vi.fn(), 'agent-1');

      expect(subscribedSpy).toHaveBeenCalledTimes(1);
      expect(subscribedSpy).toHaveBeenCalledWith(
        expect.objectContaining({
          topic: 'test-topic',
          subscriberId: 'agent-1'
        })
      );
    });

    it('should throw error when not connected', async () => {
      await messageBus.disconnect();

      await expect(
        messageBus.subscribe('test-topic', vi.fn(), 'agent-1')
      ).rejects.toThrow('MessageBus not connected');
    });
  });

  describe('Unsubscribing from Topics', () => {
    beforeEach(async () => {
      await messageBus.connect();
    });

    it('should unsubscribe from a topic', async () => {
      const handler: MessageHandler = vi.fn();
      const subscriptionId = await messageBus.subscribe('test-topic', handler, 'agent-1');

      const result = await messageBus.unsubscribe(subscriptionId);

      expect(result).toBe(true);
    });

    it('should not receive messages after unsubscribing', async () => {
      const handler: MessageHandler = vi.fn();
      const topic = 'test-topic';

      const subscriptionId = await messageBus.subscribe(topic, handler, 'agent-1');
      await messageBus.unsubscribe(subscriptionId);

      await messageBus.publish(topic, { data: 'test' }, 'agent-2');

      // Wait for async message delivery
      await new Promise(resolve => setImmediate(resolve));

      expect(handler).not.toHaveBeenCalled();
    });

    it('should return false for non-existent subscription', async () => {
      const result = await messageBus.unsubscribe('non-existent-id');
      expect(result).toBe(false);
    });

    it('should emit unsubscribed event', async () => {
      const unsubscribedSpy = vi.fn();
      messageBus.on('unsubscribed', unsubscribedSpy);

      const subscriptionId = await messageBus.subscribe('test-topic', vi.fn(), 'agent-1');
      await messageBus.unsubscribe(subscriptionId);

      expect(unsubscribedSpy).toHaveBeenCalledTimes(1);
    });

    it('should unsubscribe all subscriptions for a subscriber', async () => {
      const subscriberId = 'agent-1';

      await messageBus.subscribe('topic-1', vi.fn(), subscriberId);
      await messageBus.subscribe('topic-2', vi.fn(), subscriberId);
      await messageBus.subscribe('topic-3', vi.fn(), subscriberId);

      const count = await messageBus.unsubscribeAll(subscriberId);

      expect(count).toBe(3);
      expect(messageBus.getSubscriptions()).toHaveLength(0);
    });

    it('should only unsubscribe specified subscriber', async () => {
      await messageBus.subscribe('topic-1', vi.fn(), 'agent-1');
      await messageBus.subscribe('topic-1', vi.fn(), 'agent-2');

      const count = await messageBus.unsubscribeAll('agent-1');

      expect(count).toBe(1);
      expect(messageBus.getSubscriptions()).toHaveLength(1);
      expect(messageBus.getSubscriptions()[0].subscriberId).toBe('agent-2');
    });
  });

  describe('Query Subscriptions', () => {
    beforeEach(async () => {
      await messageBus.connect();
    });

    it('should get all subscriptions', async () => {
      await messageBus.subscribe('topic-1', vi.fn(), 'agent-1');
      await messageBus.subscribe('topic-2', vi.fn(), 'agent-2');

      const subscriptions = messageBus.getSubscriptions();

      expect(subscriptions).toHaveLength(2);
    });

    it('should get subscriptions for a topic', async () => {
      const topic = 'test-topic';

      await messageBus.subscribe(topic, vi.fn(), 'agent-1');
      await messageBus.subscribe(topic, vi.fn(), 'agent-2');
      await messageBus.subscribe('other-topic', vi.fn(), 'agent-3');

      const topicSubs = messageBus.getTopicSubscriptions(topic);

      expect(topicSubs).toHaveLength(2);
      expect(topicSubs.every(sub => sub.topic === topic)).toBe(true);
    });

    it('should return empty array for topic with no subscriptions', async () => {
      const topicSubs = messageBus.getTopicSubscriptions('non-existent-topic');

      expect(topicSubs).toEqual([]);
    });
  });

  describe('Error Handling', () => {
    beforeEach(async () => {
      await messageBus.connect();
    });

    it('should handle async handler errors', async () => {
      const errorSpy = vi.fn();
      messageBus.on('handler-error', errorSpy);

      const handler: MessageHandler = async () => {
        throw new Error('Handler error');
      };

      await messageBus.subscribe('test-topic', handler, 'agent-1');
      await messageBus.publish('test-topic', { data: 'test' }, 'agent-2');

      // Wait for async message delivery and error handling
      await new Promise(resolve => setTimeout(resolve, 50));

      expect(errorSpy).toHaveBeenCalled();
    });

    it('should handle sync handler errors', async () => {
      const errorSpy = vi.fn();
      messageBus.on('handler-error', errorSpy);

      const handler: MessageHandler = () => {
        throw new Error('Handler error');
      };

      await messageBus.subscribe('test-topic', handler, 'agent-1');
      await messageBus.publish('test-topic', { data: 'test' }, 'agent-2');

      // Wait for async message delivery
      await new Promise(resolve => setImmediate(resolve));

      expect(errorSpy).toHaveBeenCalled();
    });

    it('should continue processing other handlers after error', async () => {
      const errorHandler: MessageHandler = () => {
        throw new Error('Handler error');
      };
      const successHandler: MessageHandler = vi.fn();

      await messageBus.subscribe('test-topic', errorHandler, 'agent-1');
      await messageBus.subscribe('test-topic', successHandler, 'agent-2');

      await messageBus.publish('test-topic', { data: 'test' }, 'agent-3');

      // Wait for async message delivery
      await new Promise(resolve => setImmediate(resolve));

      expect(successHandler).toHaveBeenCalledTimes(1);
    });
  });

  describe('Message Structure', () => {
    beforeEach(async () => {
      await messageBus.connect();
    });

    it('should generate unique message IDs', async () => {
      const topic = 'test-topic';

      await messageBus.publish(topic, { data: 'test1' }, 'agent-1');
      await messageBus.publish(topic, { data: 'test2' }, 'agent-1');

      const messages = MockRedisClient.getPublishedMessages(topic);
      const message1: BusMessage = JSON.parse(messages[0]);
      const message2: BusMessage = JSON.parse(messages[1]);

      expect(message1.id).not.toBe(message2.id);
    });

    it('should include timestamp in messages', async () => {
      const topic = 'test-topic';
      const before = new Date();

      await messageBus.publish(topic, { data: 'test' }, 'agent-1');

      const after = new Date();
      const messages = MockRedisClient.getPublishedMessages(topic);
      const message: BusMessage = JSON.parse(messages[0]);
      const timestamp = new Date(message.timestamp);

      expect(timestamp.getTime()).toBeGreaterThanOrEqual(before.getTime());
      expect(timestamp.getTime()).toBeLessThanOrEqual(after.getTime());
    });

    it('should preserve message payload types', async () => {
      const handler: MessageHandler = vi.fn();
      const topic = 'test-topic';

      await messageBus.subscribe(topic, handler, 'agent-1');

      // Test different payload types
      await messageBus.publish(topic, 'string payload', 'agent-2');
      await messageBus.publish(topic, 123, 'agent-2');
      await messageBus.publish(topic, { complex: 'object' }, 'agent-2');
      await messageBus.publish(topic, [1, 2, 3], 'agent-2');

      // Wait for async message delivery
      await new Promise(resolve => setImmediate(resolve));

      expect(handler).toHaveBeenCalledTimes(4);
      expect(handler.mock.calls[0][0].payload).toBe('string payload');
      expect(handler.mock.calls[1][0].payload).toBe(123);
      expect(handler.mock.calls[2][0].payload).toEqual({ complex: 'object' });
      expect(handler.mock.calls[3][0].payload).toEqual([1, 2, 3]);
    });
  });
});
