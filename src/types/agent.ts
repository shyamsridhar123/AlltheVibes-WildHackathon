import { z } from 'zod';

/**
 * Core agent types for Codesmash Agent Swarm Platform
 */

export type AgentId = string;
export type TaskId = string;

/**
 * Agent lifecycle status
 */
export enum AgentStatus {
  IDLE = 'idle',
  BUSY = 'busy',
  FAILED = 'failed',
  STOPPED = 'stopped',
}

/**
 * Agent type classification (role)
 */
export enum AgentRole {
  WORKER = 'worker',
  COORDINATOR = 'coordinator',
  SPECIALIST = 'specialist',
}

/**
 * Agent capability definition
 */
export interface AgentCapability {
  /** Unique capability identifier */
  name: string;
  /** Human-readable description */
  description: string;
  /** Version of the capability */
  version: string;
  /** Whether this capability is currently enabled */
  enabled: boolean;
}

/**
 * Agent execution statistics
 */
export interface AgentStats {
  /** Total number of tasks executed */
  tasksExecuted: number;
  /** Number of successful task executions */
  tasksSucceeded: number;
  /** Number of failed task executions */
  tasksFailed: number;
  /** Timestamp when agent was created */
  createdAt: Date;
  /** Timestamp of last activity */
  lastActiveAt: Date;
  /** Total execution time in milliseconds */
  totalExecutionTime: number;
}

/**
 * Agent metadata
 */
export interface AgentMetadata {
  /** Unique agent identifier */
  id: AgentId;
  /** Agent role/type */
  role: AgentRole;
  /** Current agent status */
  status: AgentStatus;
  /** List of agent capabilities */
  capabilities: AgentCapability[];
  /** Timestamp when agent was created */
  createdAt: Date;
  /** Timestamp when agent was last updated */
  updatedAt: Date;
}

/**
 * Agent message for inter-agent communication
 */
export interface AgentMessage {
  /** Sender agent ID */
  from: AgentId;
  /** Recipient agent ID */
  to: AgentId;
  /** Message type */
  type: string;
  /** Message payload */
  payload: unknown;
  /** When message was sent */
  timestamp: Date;
  /** Unique message identifier (optional, can be assigned by message bus) */
  id?: string;
  /** Correlation ID for tracking related messages */
  correlationId?: string;
}

/**
 * Agent configuration options
 */
export interface AgentConfig {
  /** Agent name */
  name: string;
  /** Agent type/role */
  type: AgentRole;
  /** Agent version */
  version?: string;
  /** List of capabilities */
  capabilities?: AgentCapability[];
  /** Custom configuration */
  custom?: Record<string, unknown>;
}

/**
 * Zod Schemas for Agent Validation
 */

// AgentStatus schema
export const AgentStatusSchema = z.nativeEnum(AgentStatus);

// AgentRole schema
export const AgentRoleSchema = z.nativeEnum(AgentRole);

// AgentCapability schema
export const AgentCapabilitySchema = z.object({
  name: z.string(),
  description: z.string(),
  version: z.string(),
  enabled: z.boolean()
});

// AgentStats schema
export const AgentStatsSchema = z.object({
  tasksExecuted: z.number().int().min(0),
  tasksSucceeded: z.number().int().min(0),
  tasksFailed: z.number().int().min(0),
  createdAt: z.date(),
  lastActiveAt: z.date(),
  totalExecutionTime: z.number().min(0)
});

// AgentMetadata schema
export const AgentMetadataSchema = z.object({
  id: z.string(),
  role: AgentRoleSchema,
  status: AgentStatusSchema,
  capabilities: z.array(AgentCapabilitySchema),
  createdAt: z.date(),
  updatedAt: z.date()
});

// AgentMessage schema
export const AgentMessageSchema = z.object({
  from: z.string(),
  to: z.string(),
  type: z.string(),
  payload: z.unknown(),
  timestamp: z.date(),
  id: z.string().optional(),
  correlationId: z.string().optional()
});

// AgentConfig schema
export const AgentConfigSchema = z.object({
  name: z.string(),
  type: AgentRoleSchema,
  version: z.string().optional(),
  capabilities: z.array(AgentCapabilitySchema).optional(),
  custom: z.record(z.unknown()).optional()
});

/**
 * Type guard to check if a value is a valid AgentMetadata
 */
export function isAgentMetadata(value: unknown): value is AgentMetadata {
  try {
    AgentMetadataSchema.parse(value);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate and parse an agent metadata object
 */
export function parseAgentMetadata(value: unknown): AgentMetadata {
  return AgentMetadataSchema.parse(value);
}

/**
 * Type guard to check if a value is a valid AgentConfig
 */
export function isAgentConfig(value: unknown): value is AgentConfig {
  try {
    AgentConfigSchema.parse(value);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate and parse an agent config object
 */
export function parseAgentConfig(value: unknown): AgentConfig {
  return AgentConfigSchema.parse(value);
}

/**
 * Type guard to check if a value is a valid AgentMessage
 */
export function isAgentMessage(value: unknown): value is AgentMessage {
  try {
    AgentMessageSchema.parse(value);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate and parse an agent message object
 */
export function parseAgentMessage(value: unknown): AgentMessage {
  return AgentMessageSchema.parse(value);
}
