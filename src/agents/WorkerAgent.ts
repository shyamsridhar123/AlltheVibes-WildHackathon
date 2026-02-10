/**
 * WorkerAgent - Example worker agent implementation
 */

import { BaseAgent, AgentConfig } from './BaseAgent.js';
import { AgentRole, AgentStatus, Task } from '../types/agent.js';
import { logger } from '../utils/logger.js';

export interface WorkerAgentConfig extends Omit<AgentConfig, 'role'> {
  // Worker-specific config can be added here
}

/**
 * Worker agent that processes tasks
 */
export class WorkerAgent extends BaseAgent {
  constructor(config: WorkerAgentConfig) {
    super({
      ...config,
      role: AgentRole.WORKER,
    });
  }

  /**
   * Execute a task
   */
  async execute(task: Task): Promise<unknown> {
    logger.info(`Worker ${this.id} executing task ${task.id} (${task.type})`);

    this.setStatus(AgentStatus.BUSY);

    try {
      // Simulate task processing
      const result = await this.processTask(task);

      this.setStatus(AgentStatus.IDLE);
      logger.info(`Worker ${this.id} completed task ${task.id}`);

      return result;
    } catch (error) {
      this.setStatus(AgentStatus.FAILED);
      logger.error(`Worker ${this.id} failed to execute task ${task.id}:`, error);
      throw error;
    }
  }

  /**
   * Process the task - can be overridden by subclasses
   */
  protected async processTask(task: Task): Promise<unknown> {
    // Default implementation - just return the task payload
    return {
      taskId: task.id,
      status: 'completed',
      result: task.payload,
    };
  }
}
