/**
 * Redis connection for message bus and task queue
 * Provides connection pooling, health checks, and utility methods
 */

import { createClient, RedisClientType } from 'redis';
import { config } from '../config/index.js';
import { logger } from '../utils/logger.js';

let client: RedisClientType | null = null;
let isHealthy = false;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;
const RECONNECT_DELAY = 1000; // ms

/**
 * Redis connection options with pooling configuration
 */
const redisOptions = {
  socket: {
    host: config.redis.host,
    port: config.redis.port,
    reconnectStrategy: (retries: number) => {
      reconnectAttempts = retries;
      if (retries > MAX_RECONNECT_ATTEMPTS) {
        logger.error('Redis max reconnection attempts reached');
        return new Error('Max reconnection attempts exceeded');
      }
      const delay = Math.min(RECONNECT_DELAY * retries, 5000);
      logger.warn(`Redis reconnecting in ${delay}ms (attempt ${retries})`);
      return delay;
    },
  },
  password: config.redis.password || undefined,
};

/**
 * Connects to Redis with connection pooling and error handling
 */
export async function connectRedis(): Promise<RedisClientType> {
  if (client && isHealthy) {
    return client;
  }

  try {
    client = createClient(redisOptions);

    // Event handlers
    client.on('error', (err) => {
      logger.error('Redis Client Error:', err);
      isHealthy = false;
    });

    client.on('connect', () => {
      logger.info('✅ Connected to Redis');
      isHealthy = true;
      reconnectAttempts = 0;
    });

    client.on('ready', () => {
      logger.info('Redis client ready');
      isHealthy = true;
    });

    client.on('reconnecting', () => {
      logger.warn('Redis reconnecting...');
      isHealthy = false;
    });

    client.on('end', () => {
      logger.info('Redis connection closed');
      isHealthy = false;
    });

    await client.connect();

    // Verify connection with ping
    await client.ping();

    return client;
  } catch (error) {
    logger.error('Failed to connect to Redis:', error);
    isHealthy = false;
    throw error;
  }
}

/**
 * Disconnects from Redis gracefully
 */
export async function disconnectRedis(): Promise<void> {
  if (client) {
    try {
      await client.quit();
      client = null;
      isHealthy = false;
      logger.info('Disconnected from Redis');
    } catch (error) {
      logger.error('Error disconnecting from Redis:', error);
      // Force disconnect if graceful quit fails
      await client?.disconnect();
      client = null;
      isHealthy = false;
    }
  }
}

/**
 * Gets the Redis client instance
 * Throws error if client is not initialized
 */
export function getRedisClient(): RedisClientType {
  if (!client) {
    throw new Error('Redis client not initialized. Call connectRedis() first.');
  }
  return client;
}

/**
 * Health check for Redis connection
 */
export async function healthCheck(): Promise<boolean> {
  try {
    if (!client) {
      return false;
    }
    await client.ping();
    isHealthy = true;
    return true;
  } catch (error) {
    logger.error('Redis health check failed:', error);
    isHealthy = false;
    return false;
  }
}

/**
 * Get current health status without performing check
 */
export function isRedisHealthy(): boolean {
  return isHealthy;
}

/**
 * Redis utility methods for common operations
 */
export const RedisUtils = {
  /**
   * Get a value from Redis
   */
  async get(key: string): Promise<string | null> {
    const client = getRedisClient();
    return await client.get(key);
  },

  /**
   * Get and parse JSON value from Redis
   */
  async getJSON<T>(key: string): Promise<T | null> {
    const value = await this.get(key);
    if (!value) return null;
    try {
      return JSON.parse(value) as T;
    } catch (error) {
      logger.error(`Failed to parse JSON for key ${key}:`, error);
      return null;
    }
  },

  /**
   * Set a value in Redis
   */
  async set(key: string, value: string, expirySeconds?: number): Promise<void> {
    const client = getRedisClient();
    if (expirySeconds) {
      await client.setEx(key, expirySeconds, value);
    } else {
      await client.set(key, value);
    }
  },

  /**
   * Set a JSON value in Redis
   */
  async setJSON(key: string, value: unknown, expirySeconds?: number): Promise<void> {
    const jsonString = JSON.stringify(value);
    await this.set(key, jsonString, expirySeconds);
  },

  /**
   * Delete a key from Redis
   */
  async del(key: string): Promise<number> {
    const client = getRedisClient();
    return await client.del(key);
  },

  /**
   * Delete multiple keys from Redis
   */
  async delMultiple(keys: string[]): Promise<number> {
    if (keys.length === 0) return 0;
    const client = getRedisClient();
    return await client.del(keys);
  },

  /**
   * Set expiry time on a key
   */
  async expire(key: string, seconds: number): Promise<boolean> {
    const client = getRedisClient();
    return await client.expire(key, seconds);
  },

  /**
   * Check if a key exists
   */
  async exists(key: string): Promise<boolean> {
    const client = getRedisClient();
    const result = await client.exists(key);
    return result === 1;
  },

  /**
   * Get time-to-live for a key in seconds
   */
  async ttl(key: string): Promise<number> {
    const client = getRedisClient();
    return await client.ttl(key);
  },

  /**
   * Increment a counter
   */
  async incr(key: string): Promise<number> {
    const client = getRedisClient();
    return await client.incr(key);
  },

  /**
   * Decrement a counter
   */
  async decr(key: string): Promise<number> {
    const client = getRedisClient();
    return await client.decr(key);
  },

  /**
   * Get all keys matching a pattern
   */
  async keys(pattern: string): Promise<string[]> {
    const client = getRedisClient();
    return await client.keys(pattern);
  },

  /**
   * Flush all data (use with caution!)
   */
  async flushAll(): Promise<void> {
    const client = getRedisClient();
    await client.flushAll();
    logger.warn('Redis: All data flushed');
  },
};
