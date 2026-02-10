/**
 * Tests for Redis client and utilities
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import type { RedisClientType } from 'redis';

// Mock the redis module
vi.mock('redis', () => ({
  createClient: vi.fn(),
}));

// Mock config
vi.mock('../config/index.js', () => ({
  config: {
    redis: {
      host: 'localhost',
      port: 6379,
      password: '',
    },
  },
}));

// Mock logger
vi.mock('../utils/logger.js', () => ({
  logger: {
    info: vi.fn(),
    error: vi.fn(),
    warn: vi.fn(),
  },
}));

describe('Redis Client', () => {
  let mockClient: Partial<RedisClientType>;
  let connectRedis: any;
  let disconnectRedis: any;
  let getRedisClient: any;
  let healthCheck: any;
  let isRedisHealthy: any;
  let RedisUtils: any;

  beforeEach(async () => {
    vi.resetModules();
    mockClient = {
      connect: vi.fn().mockResolvedValue(undefined),
      quit: vi.fn().mockResolvedValue(undefined),
      disconnect: vi.fn().mockResolvedValue(undefined),
      ping: vi.fn().mockResolvedValue('PONG'),
      on: vi.fn(),
      get: vi.fn(),
      set: vi.fn(),
      setEx: vi.fn(),
      del: vi.fn(),
      expire: vi.fn(),
      exists: vi.fn(),
      ttl: vi.fn(),
      incr: vi.fn(),
      decr: vi.fn(),
      keys: vi.fn(),
      flushAll: vi.fn(),
    };
    const { createClient } = await import('redis');
    vi.mocked(createClient).mockReturnValue(mockClient as RedisClientType);
    const redisModule = await import('./redis.js');
    connectRedis = redisModule.connectRedis;
    disconnectRedis = redisModule.disconnectRedis;
    getRedisClient = redisModule.getRedisClient;
    healthCheck = redisModule.healthCheck;
    isRedisHealthy = redisModule.isRedisHealthy;
    RedisUtils = redisModule.RedisUtils;
  });

  afterEach(async () => {
    vi.clearAllMocks();
    await disconnectRedis();
  });

  describe('connectRedis', () => {
    it('should connect to Redis successfully', async () => {
      const client = await connectRedis();
      expect(client).toBeDefined();
      expect(mockClient.connect).toHaveBeenCalled();
      expect(mockClient.ping).toHaveBeenCalled();
    });

    it('should return existing client on subsequent calls', async () => {
      const client1 = await connectRedis();
      const client2 = await connectRedis();
      expect(client1).toBe(client2);
    });

    it('should handle connection errors', async () => {
      mockClient.connect = vi.fn().mockRejectedValue(new Error('Connection failed'));
      await expect(connectRedis()).rejects.toThrow('Connection failed');
    });

    it('should register event handlers', async () => {
      await connectRedis();
      expect(mockClient.on).toHaveBeenCalledWith('error', expect.any(Function));
      expect(mockClient.on).toHaveBeenCalledWith('connect', expect.any(Function));
      expect(mockClient.on).toHaveBeenCalledWith('ready', expect.any(Function));
      expect(mockClient.on).toHaveBeenCalledWith('reconnecting', expect.any(Function));
      expect(mockClient.on).toHaveBeenCalledWith('end', expect.any(Function));
    });
  });

  describe('disconnectRedis', () => {
    it('should disconnect gracefully', async () => {
      await connectRedis();
      await disconnectRedis();
      expect(mockClient.quit).toHaveBeenCalled();
    });

    it('should handle disconnect errors', async () => {
      await connectRedis();
      mockClient.quit = vi.fn().mockRejectedValue(new Error('Quit failed'));
      await disconnectRedis();
      expect(mockClient.disconnect).toHaveBeenCalled();
    });

    it('should not error if client is not initialized', async () => {
      await expect(disconnectRedis()).resolves.not.toThrow();
    });
  });

  describe('getRedisClient', () => {
    it('should return client when initialized', async () => {
      await connectRedis();
      const client = getRedisClient();
      expect(client).toBe(mockClient);
    });

    it('should throw error when not initialized', () => {
      expect(() => getRedisClient()).toThrow('Redis client not initialized');
    });
  });

  describe('healthCheck', () => {
    it('should return true when Redis is healthy', async () => {
      await connectRedis();
      const healthy = await healthCheck();
      expect(healthy).toBe(true);
      expect(mockClient.ping).toHaveBeenCalled();
    });

    it('should return false when Redis is unhealthy', async () => {
      await connectRedis();
      mockClient.ping = vi.fn().mockRejectedValue(new Error('Ping failed'));
      const healthy = await healthCheck();
      expect(healthy).toBe(false);
    });

    it('should return false when client is not initialized', async () => {
      const healthy = await healthCheck();
      expect(healthy).toBe(false);
    });
  });

  describe('isRedisHealthy', () => {
    it('should return health status', async () => {
      await connectRedis();
      const healthy = isRedisHealthy();
      expect(typeof healthy).toBe('boolean');
    });
  });

  describe('RedisUtils', () => {
    beforeEach(async () => {
      await connectRedis();
    });

    describe('get/set operations', () => {
      it('should get a value', async () => {
        mockClient.get = vi.fn().mockResolvedValue('test-value');
        const value = await RedisUtils.get('test-key');
        expect(value).toBe('test-value');
      });

      it('should set a value without expiry', async () => {
        mockClient.set = vi.fn().mockResolvedValue('OK');
        await RedisUtils.set('test-key', 'test-value');
        expect(mockClient.set).toHaveBeenCalledWith('test-key', 'test-value');
      });

      it('should set a value with expiry', async () => {
        mockClient.setEx = vi.fn().mockResolvedValue('OK');
        await RedisUtils.set('test-key', 'test-value', 60);
        expect(mockClient.setEx).toHaveBeenCalledWith('test-key', 60, 'test-value');
      });
    });

    describe('JSON operations', () => {
      it('should get and parse JSON value', async () => {
        const testData = { foo: 'bar', num: 42 };
        mockClient.get = vi.fn().mockResolvedValue(JSON.stringify(testData));
        const value = await RedisUtils.getJSON('test-key');
        expect(value).toEqual(testData);
      });

      it('should set JSON value', async () => {
        const testData = { foo: 'bar' };
        mockClient.set = vi.fn().mockResolvedValue('OK');
        await RedisUtils.setJSON('test-key', testData);
        expect(mockClient.set).toHaveBeenCalledWith('test-key', JSON.stringify(testData));
      });
    });

    describe('delete operations', () => {
      it('should delete a key', async () => {
        mockClient.del = vi.fn().mockResolvedValue(1);
        const result = await RedisUtils.del('test-key');
        expect(result).toBe(1);
      });

      it('should delete multiple keys', async () => {
        mockClient.del = vi.fn().mockResolvedValue(3);
        const result = await RedisUtils.delMultiple(['key1', 'key2', 'key3']);
        expect(result).toBe(3);
      });
    });

    describe('utility operations', () => {
      it('should set expiry on a key', async () => {
        mockClient.expire = vi.fn().mockResolvedValue(true);
        const result = await RedisUtils.expire('test-key', 60);
        expect(result).toBe(true);
      });

      it('should check if key exists', async () => {
        mockClient.exists = vi.fn().mockResolvedValue(1);
        const result = await RedisUtils.exists('test-key');
        expect(result).toBe(true);
      });

      it('should increment a counter', async () => {
        mockClient.incr = vi.fn().mockResolvedValue(5);
        const result = await RedisUtils.incr('counter');
        expect(result).toBe(5);
      });

      it('should decrement a counter', async () => {
        mockClient.decr = vi.fn().mockResolvedValue(3);
        const result = await RedisUtils.decr('counter');
        expect(result).toBe(3);
      });

      it('should get TTL for a key', async () => {
        mockClient.ttl = vi.fn().mockResolvedValue(60);
        const result = await RedisUtils.ttl('test-key');
        expect(result).toBe(60);
      });

      it('should get keys matching pattern', async () => {
        const keys = ['key1', 'key2', 'key3'];
        mockClient.keys = vi.fn().mockResolvedValue(keys);
        const result = await RedisUtils.keys('key*');
        expect(result).toEqual(keys);
      });
    });
  });
});
