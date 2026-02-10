/**
 * Tests for BaseAgent class
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { BaseAgent, AgentConfig } from './BaseAgent.js';
import { AgentRole, AgentStatus, Task, AgentMessage } from '../types/agent.js';

// Test implementation of BaseAgent
class TestAgent extends BaseAgent {
  async execute(task: Task): Promise<unknown> {
    this.setStatus(AgentStatus.BUSY);
    // Simulate task execution
    const result = { taskId: task.id, result: 'completed' };
    this.setStatus(AgentStatus.IDLE);
    return result;
  }
}

describe('BaseAgent', () => {
  let agent: TestAgent;
  const config: AgentConfig = {
    role: AgentRole.WORKER,
    capabilities: [
      {
        name: 'test-capability',
        description: 'A test capability',
        version: '1.0.0',
      },
    ],
  };

  beforeEach(() => {
    agent = new TestAgent(config);
  });

  describe('Initialization', () => {
    it('should create agent with unique ID', () => {
      const agent1 = new TestAgent(config);
      const agent2 = new TestAgent(config);
      expect(agent1.getId()).not.toBe(agent2.getId());
    });

    it('should initialize with correct role', () => {
      expect(agent.getRole()).toBe(AgentRole.WORKER);
    });

    it('should initialize with IDLE status', async () => {
      await agent.initialize();
      expect(agent.getStatus()).toBe(AgentStatus.IDLE);
    });

    it('should emit initialized event', async () => {
      const spy = vi.fn();
      agent.on('initialized', spy);
      await agent.initialize();
      expect(spy).toHaveBeenCalledWith(agent.getMetadata());
    });
  });

  describe('Capabilities', () => {
    beforeEach(async () => {
      await agent.initialize();
    });

    it('should register initial capabilities', () => {
      expect(agent.hasCapability('test-capability')).toBe(true);
    });

    it('should register new capability', () => {
      agent.registerCapability({
        name: 'new-capability',
        description: 'A new capability',
        version: '1.0.0',
      });
      expect(agent.hasCapability('new-capability')).toBe(true);
    });

    it('should unregister capability', () => {
      agent.unregisterCapability('test-capability');
      expect(agent.hasCapability('test-capability')).toBe(false);
    });

    it('should get all capabilities', () => {
      const capabilities = agent.getCapabilities();
      expect(capabilities).toHaveLength(1);
      expect(capabilities[0].name).toBe('test-capability');
    });
  });

  describe('State Management', () => {
    beforeEach(async () => {
      await agent.initialize();
    });

    it('should set and get state', () => {
      (agent as any).setState('testKey', 'testValue');
      expect((agent as any).getState('testKey')).toBe('testValue');
    });

    it('should emit state-updated event', () => {
      const spy = vi.fn();
      agent.on('state-updated', spy);
      (agent as any).setState('key', 'value');
      expect(spy).toHaveBeenCalledWith({ key: 'key', value: 'value' });
    });

    it('should get full state', () => {
      (agent as any).setState('key1', 'value1');
      (agent as any).setState('key2', 'value2');
      const state = agent.getFullState();
      expect(state).toEqual({ key1: 'value1', key2: 'value2' });
    });
  });

  describe('Task Execution', () => {
    beforeEach(async () => {
      await agent.initialize();
    });

    it('should execute task and return result', async () => {
      const task: Task = {
        id: 'task-1',
        type: 'test-task',
        priority: 1,
        payload: {},
        status: 'pending',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const result = await agent.execute(task);
      expect(result).toEqual({ taskId: 'task-1', result: 'completed' });
    });

    it('should change status during execution', async () => {
      const task: Task = {
        id: 'task-1',
        type: 'test-task',
        priority: 1,
        payload: {},
        status: 'pending',
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      const statusSpy = vi.fn();
      agent.on('status-changed', statusSpy);

      await agent.execute(task);

      expect(statusSpy).toHaveBeenCalledWith(AgentStatus.BUSY);
      expect(statusSpy).toHaveBeenCalledWith(AgentStatus.IDLE);
      expect(agent.getStatus()).toBe(AgentStatus.IDLE);
    });
  });

  describe('Message Passing', () => {
    beforeEach(async () => {
      await agent.initialize();
    });

    it('should send message and emit event', async () => {
      const spy = vi.fn();
      agent.on('message-sent', spy);

      await agent.sendMessage('target-agent-id', 'test-message', { data: 'test' });

      expect(spy).toHaveBeenCalledWith(
        expect.objectContaining({
          from: agent.getId(),
          to: 'target-agent-id',
          type: 'test-message',
          payload: { data: 'test' },
        })
      );
    });

    it('should handle incoming message', async () => {
      const spy = vi.fn();
      agent.on('message-received', spy);

      const message: AgentMessage = {
        from: 'sender-id',
        to: agent.getId(),
        type: 'test-message',
        payload: { data: 'test' },
        timestamp: new Date(),
      };

      await agent.handleMessage(message);
      expect(spy).toHaveBeenCalledWith(message);
    });
  });

  describe('Agent Spawning', () => {
    beforeEach(async () => {
      await agent.initialize();
    });

    it('should spawn child agent', async () => {
      const spy = vi.fn();
      agent.on('child-spawned', spy);

      const child = await agent.spawn(TestAgent, {
        role: AgentRole.WORKER,
      });

      expect(child.getParentId()).toBe(agent.getId());
      expect(spy).toHaveBeenCalledWith(child.getMetadata());
      expect(agent.getChildren().size).toBe(1);
    });

    it('should initialize spawned child', async () => {
      const child = await agent.spawn(TestAgent, {
        role: AgentRole.WORKER,
      });

      expect(child.getStatus()).toBe(AgentStatus.IDLE);
    });
  });

  describe('Termination', () => {
    it('should terminate agent and emit event', async () => {
      await agent.initialize();
      const spy = vi.fn();
      agent.on('terminated', spy);

      await agent.terminate();

      expect(agent.getStatus()).toBe(AgentStatus.STOPPED);
      expect(spy).toHaveBeenCalledWith(agent.getMetadata());
    });

    it('should terminate all child agents', async () => {
      await agent.initialize();

      const child1 = await agent.spawn(TestAgent, { role: AgentRole.WORKER });
      const child2 = await agent.spawn(TestAgent, { role: AgentRole.WORKER });

      await agent.terminate();

      expect(child1.getStatus()).toBe(AgentStatus.STOPPED);
      expect(child2.getStatus()).toBe(AgentStatus.STOPPED);
    });
  });

  describe('Metadata', () => {
    it('should return agent metadata', async () => {
      await agent.initialize();
      const metadata = agent.getMetadata();

      expect(metadata.id).toBe(agent.getId());
      expect(metadata.role).toBe(AgentRole.WORKER);
      expect(metadata.status).toBe(AgentStatus.IDLE);
      expect(metadata.capabilities).toHaveLength(1);
      expect(metadata.createdAt).toBeInstanceOf(Date);
      expect(metadata.updatedAt).toBeInstanceOf(Date);
    });

    it('should update metadata timestamp on changes', async () => {
      await agent.initialize();
      const originalMetadata = agent.getMetadata();

      // Wait a bit to ensure timestamp difference
      await new Promise((resolve) => setTimeout(resolve, 10));

      agent.registerCapability({
        name: 'new-cap',
        description: 'test',
        version: '1.0.0',
      });

      const newMetadata = agent.getMetadata();
      expect(newMetadata.updatedAt.getTime()).toBeGreaterThan(
        originalMetadata.updatedAt.getTime()
      );
    });
  });
});
