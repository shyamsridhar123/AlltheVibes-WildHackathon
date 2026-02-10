import { z } from 'zod';

/**
 * Task Type Definitions
 *
 * Core type definitions for tasks in the Agent Swarm Platform.
 * Tasks represent units of work that agents can claim and execute.
 */

/**
 * Task status enum
 */
export enum TaskStatus {
  /** Task is waiting to be claimed */
  PENDING = 'pending',
  /** Task has been claimed by an agent */
  CLAIMED = 'claimed',
  /** Task is currently being executed */
  IN_PROGRESS = 'in_progress',
  /** Task completed successfully */
  COMPLETED = 'completed',
  /** Task execution failed */
  FAILED = 'failed',
  /** Task was cancelled */
  CANCELLED = 'cancelled',
  /** Task is waiting for retry */
  RETRY = 'retry'
}

/**
 * Task priority levels
 */
export enum TaskPriority {
  /** Critical priority - execute immediately */
  CRITICAL = 5,
  /** High priority */
  HIGH = 4,
  /** Normal priority */
  NORMAL = 3,
  /** Low priority */
  LOW = 2,
  /** Deferred priority - execute when system is idle */
  DEFERRED = 1
}

/**
 * Task metadata for tracking and auditing
 */
export interface TaskMetadata {
  /** Task creation timestamp */
  createdAt: Date;
  /** Last update timestamp */
  updatedAt: Date;
  /** Task completion timestamp */
  completedAt?: Date;
  /** Task failure timestamp */
  failedAt?: Date;
  /** Agent ID that claimed the task */
  claimedBy?: string;
  /** Timestamp when task was claimed */
  claimedAt?: Date;
  /** Number of retry attempts */
  retryCount: number;
  /** Maximum number of retry attempts allowed */
  maxRetries: number;
  /** Parent task ID for subtasks */
  parentTaskId?: string;
  /** Correlation ID for tracking related tasks */
  correlationId?: string;
  /** Custom metadata */
  custom?: Record<string, unknown>;
}

/**
 * Task result information
 */
export interface TaskResult {
  /** Whether task execution was successful */
  success: boolean;
  /** Result data from task execution */
  data?: unknown;
  /** Error information if task failed */
  error?: {
    message: string;
    code?: string;
    stack?: string;
  };
  /** Execution duration in milliseconds */
  duration: number;
  /** Agent ID that executed the task */
  executedBy: string;
  /** Timestamp when execution completed */
  timestamp: Date;
}

/**
 * Task requirements and constraints
 */
export interface TaskRequirements {
  /** Required agent capabilities */
  requiredCapabilities?: string[];
  /** Required agent type */
  requiredAgentType?: string;
  /** Estimated execution time in milliseconds */
  estimatedDuration?: number;
  /** Task deadline */
  deadline?: Date;
  /** Task dependencies (must be completed first) */
  dependencies?: string[];
  /** Resource requirements */
  resources?: {
    memory?: number;
    cpu?: number;
    apiCalls?: number;
  };
}

/**
 * Complete task definition
 */
export interface Task {
  /** Unique task identifier */
  id: string;
  /** Task type/category */
  type: string;
  /** Task title/description */
  title: string;
  /** Detailed task description */
  description?: string;
  /** Task priority level */
  priority: TaskPriority;
  /** Current task status */
  status: TaskStatus;
  /** Task input data/payload */
  payload: unknown;
  /** Task result (populated after completion) */
  result?: TaskResult;
  /** Task requirements and constraints */
  requirements?: TaskRequirements;
  /** Task metadata */
  metadata: TaskMetadata;
}

/**
 * Zod Schemas for Task Validation
 */

// TaskStatus schema
export const TaskStatusSchema = z.nativeEnum(TaskStatus);

// TaskPriority schema
export const TaskPrioritySchema = z.nativeEnum(TaskPriority);

// TaskMetadata schema
export const TaskMetadataSchema = z.object({
  createdAt: z.date(),
  updatedAt: z.date(),
  completedAt: z.date().optional(),
  failedAt: z.date().optional(),
  claimedBy: z.string().optional(),
  claimedAt: z.date().optional(),
  retryCount: z.number().int().min(0),
  maxRetries: z.number().int().min(0),
  parentTaskId: z.string().optional(),
  correlationId: z.string().optional(),
  custom: z.record(z.unknown()).optional()
});

// TaskResult schema
export const TaskResultSchema = z.object({
  success: z.boolean(),
  data: z.unknown().optional(),
  error: z.object({
    message: z.string(),
    code: z.string().optional(),
    stack: z.string().optional()
  }).optional(),
  duration: z.number().min(0),
  executedBy: z.string(),
  timestamp: z.date()
});

// TaskRequirements schema
export const TaskRequirementsSchema = z.object({
  requiredCapabilities: z.array(z.string()).optional(),
  requiredAgentType: z.string().optional(),
  estimatedDuration: z.number().min(0).optional(),
  deadline: z.date().optional(),
  dependencies: z.array(z.string()).optional(),
  resources: z.object({
    memory: z.number().optional(),
    cpu: z.number().optional(),
    apiCalls: z.number().optional()
  }).optional()
});

// Complete Task schema
export const TaskSchema = z.object({
  id: z.string(),
  type: z.string(),
  title: z.string(),
  description: z.string().optional(),
  priority: TaskPrioritySchema,
  status: TaskStatusSchema,
  payload: z.unknown(),
  result: TaskResultSchema.optional(),
  requirements: TaskRequirementsSchema.optional(),
  metadata: TaskMetadataSchema
});

/**
 * Type guard to check if a value is a valid Task
 */
export function isTask(value: unknown): value is Task {
  try {
    TaskSchema.parse(value);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate and parse a task object
 */
export function parseTask(value: unknown): Task {
  return TaskSchema.parse(value);
}

/**
 * Create a new task with default values
 */
export function createTask(params: {
  type: string;
  title: string;
  description?: string;
  priority?: TaskPriority;
  payload: unknown;
  requirements?: TaskRequirements;
}): Task {
  const now = new Date();
  return {
    id: crypto.randomUUID(),
    type: params.type,
    title: params.title,
    description: params.description,
    priority: params.priority ?? TaskPriority.NORMAL,
    status: TaskStatus.PENDING,
    payload: params.payload,
    requirements: params.requirements,
    metadata: {
      createdAt: now,
      updatedAt: now,
      retryCount: 0,
      maxRetries: 3
    }
  };
}
