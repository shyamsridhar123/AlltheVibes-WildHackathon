/**
 * BaseAgent - Core agent class with lifecycle management
 */

import { EventEmitter } from 'events';
import { randomUUID } from 'crypto';
import {
  AgentId,
  AgentRole,
  AgentStatus,
  AgentCapability,
  AgentMetadata,
  AgentMessage,
} from '../types/agent.js';
import { Task } from '../types/task.js';
import { logger } from '../utils/logger.js';

export interface AgentConfig {
  role: AgentRole;
  capabilities?: AgentCapability[];
  parentId?: AgentId;
}

export interface AgentState {
  [key: string]: unknown;
}

/**
 * Base Agent class providing core functionality for all agents
 */
export abstract class BaseAgent extends EventEmitter {
  protected readonly id: AgentId;
  protected readonly role: AgentRole;
  protected status: AgentStatus;
  protected capabilities: Map<string, AgentCapability>;
  protected state: AgentState;
  protected parentId?: AgentId;
  protected children: Map<AgentId, BaseAgent>;
  protected metadata: AgentMetadata;

  constructor(config: AgentConfig) {
    super();
    this.id = randomUUID();
    this.role = config.role;
    this.status = AgentStatus.IDLE;
    this.capabilities = new Map();
    this.state = {};
    this.parentId = config.parentId;
    this.children = new Map();

    // Register initial capabilities
    if (config.capabilities) {
      config.capabilities.forEach((cap) => {
        this.capabilities.set(cap.name, cap);
      });
    }

    this.metadata = {
      id: this.id,
      role: this.role,
      status: this.status,
      capabilities: Array.from(this.capabilities.values()),
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    logger.debug(`Agent ${this.id} created with role ${this.role}`);
  }

  /**
   * Initialize the agent - override in subclasses
   */
  async initialize(): Promise<void> {
    logger.info(`Initializing agent ${this.id} (${this.role})`);
    this.status = AgentStatus.IDLE;
    this.updateMetadata();
    this.emit('initialized', this.metadata);
  }

  /**
   * Execute a task - must be implemented by subclasses
   */
  abstract execute(task: Task): Promise<unknown>;

  /**
   * Terminate the agent and cleanup resources
   */
  async terminate(): Promise<void> {
    logger.info(`Terminating agent ${this.id}`);

    // Terminate all child agents first
    const terminationPromises = Array.from(this.children.values()).map((child) =>
      child.terminate()
    );
    await Promise.all(terminationPromises);

    this.status = AgentStatus.STOPPED;
    this.updateMetadata();
    this.emit('terminated', this.metadata);
    this.removeAllListeners();
  }

  /**
   * Spawn a child agent
   */
  async spawn<T extends BaseAgent>(
    AgentClass: new (config: AgentConfig) => T,
    config: Omit<AgentConfig, 'parentId'>
  ): Promise<T> {
    logger.info(`Agent ${this.id} spawning child agent`);

    const childConfig: AgentConfig = {
      ...config,
      parentId: this.id,
    };

    const child = new AgentClass(childConfig);
    await child.initialize();

    this.children.set(child.getId(), child);
    this.emit('child-spawned', child.getMetadata());

    return child;
  }

  /**
   * Send a message to another agent
   */
  async sendMessage(to: AgentId, type: string, payload: unknown): Promise<void> {
    const message: AgentMessage = {
      from: this.id,
      to,
      type,
      payload,
      timestamp: new Date(),
    };

    logger.debug(`Agent ${this.id} sending message to ${to}: ${type}`);
    this.emit('message-sent', message);
  }

  /**
   * Handle incoming message - override in subclasses
   */
  async handleMessage(message: AgentMessage): Promise<void> {
    logger.debug(`Agent ${this.id} received message: ${message.type}`);
    this.emit('message-received', message);
  }

  /**
   * Register a capability
   */
  registerCapability(capability: AgentCapability): void {
    this.capabilities.set(capability.name, capability);
    this.updateMetadata();
    logger.debug(`Agent ${this.id} registered capability: ${capability.name}`);
  }

  /**
   * Unregister a capability
   */
  unregisterCapability(name: string): boolean {
    const result = this.capabilities.delete(name);
    if (result) {
      this.updateMetadata();
      logger.debug(`Agent ${this.id} unregistered capability: ${name}`);
    }
    return result;
  }

  /**
   * Check if agent has a specific capability
   */
  hasCapability(name: string): boolean {
    return this.capabilities.has(name);
  }

  /**
   * Get agent's capabilities
   */
  getCapabilities(): AgentCapability[] {
    return Array.from(this.capabilities.values());
  }

  /**
   * Update agent state
   */
  protected setState(key: string, value: unknown): void {
    this.state[key] = value;
    this.emit('state-updated', { key, value });
  }

  /**
   * Get agent state value
   */
  protected getState<T = unknown>(key: string): T | undefined {
    return this.state[key] as T | undefined;
  }

  /**
   * Get full agent state
   */
  getFullState(): Readonly<AgentState> {
    return { ...this.state };
  }

  /**
   * Update metadata timestamp
   */
  protected updateMetadata(): void {
    this.metadata = {
      ...this.metadata,
      status: this.status,
      capabilities: Array.from(this.capabilities.values()),
      updatedAt: new Date(),
    };
  }

  /**
   * Get agent ID
   */
  getId(): AgentId {
    return this.id;
  }

  /**
   * Get agent role
   */
  getRole(): AgentRole {
    return this.role;
  }

  /**
   * Get agent status
   */
  getStatus(): AgentStatus {
    return this.status;
  }

  /**
   * Get agent metadata
   */
  getMetadata(): Readonly<AgentMetadata> {
    return { ...this.metadata };
  }

  /**
   * Get parent agent ID
   */
  getParentId(): AgentId | undefined {
    return this.parentId;
  }

  /**
   * Get child agents
   */
  getChildren(): ReadonlyMap<AgentId, BaseAgent> {
    return new Map(this.children);
  }

  /**
   * Set agent status
   */
  protected setStatus(status: AgentStatus): void {
    this.status = status;
    this.updateMetadata();
    this.emit('status-changed', status);
  }
}
