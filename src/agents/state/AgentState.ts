/**
 * Agent state types and enums
 * Defines the core state model for agent lifecycle management
 */

import type { AgentId } from '../../types/agent.js';

/**
 * Agent state enum - defines all possible states an agent can be in
 */
export enum AgentState {
  IDLE = 'idle',
  ACTIVE = 'active',
  BUSY = 'busy',
  ERROR = 'error',
  TERMINATED = 'terminated',
}

/**
 * State metadata - additional information about the current state
 */
export interface StateMetadata {
  /** Timestamp when the state was entered */
  enteredAt: Date;
  /** Previous state before this one */
  previousState?: AgentState;
  /** Reason for state change (optional) */
  reason?: string;
  /** Error details if state is ERROR */
  error?: {
    message: string;
    code?: string;
    stack?: string;
  };
  /** Task ID if agent is ACTIVE or BUSY */
  currentTaskId?: string;
  /** Number of tasks in queue if agent is BUSY */
  queuedTasks?: number;
}

/**
 * Agent state record - full state information for an agent
 */
export interface AgentStateRecord {
  agentId: AgentId;
  state: AgentState;
  metadata: StateMetadata;
  updatedAt: Date;
}

/**
 * State transition - represents a change from one state to another
 */
export interface StateTransition {
  from: AgentState;
  to: AgentState;
  timestamp: Date;
  reason?: string;
}

/**
 * State change event - emitted when an agent's state changes
 */
export interface StateChangeEvent {
  agentId: AgentId;
  transition: StateTransition;
  metadata: StateMetadata;
}

/**
 * State change callback - function that is called when state changes
 */
export type StateChangeCallback = (event: StateChangeEvent) => void | Promise<void>;

/**
 * Valid state transitions map
 * Defines which state transitions are allowed
 */
export const VALID_STATE_TRANSITIONS: Record<AgentState, AgentState[]> = {
  [AgentState.IDLE]: [AgentState.ACTIVE, AgentState.TERMINATED],
  [AgentState.ACTIVE]: [AgentState.IDLE, AgentState.BUSY, AgentState.ERROR, AgentState.TERMINATED],
  [AgentState.BUSY]: [AgentState.ACTIVE, AgentState.ERROR, AgentState.TERMINATED],
  [AgentState.ERROR]: [AgentState.IDLE, AgentState.TERMINATED],
  [AgentState.TERMINATED]: [], // Terminal state - no transitions allowed
};

/**
 * Validates if a state transition is allowed
 */
export function isValidTransition(from: AgentState, to: AgentState): boolean {
  const allowedTransitions = VALID_STATE_TRANSITIONS[from];
  return allowedTransitions.includes(to);
}

/**
 * State transition error
 */
export class StateTransitionError extends Error {
  constructor(
    public from: AgentState,
    public to: AgentState,
    message?: string
  ) {
    super(
      message ||
        `Invalid state transition: ${from} -> ${to}. Allowed transitions from ${from}: ${VALID_STATE_TRANSITIONS[from].join(', ')}`
    );
    this.name = 'StateTransitionError';
  }
}

/**
 * Agent not found error
 */
export class AgentNotFoundError extends Error {
  constructor(public agentId: AgentId) {
    super(`Agent not found: ${agentId}`);
    this.name = 'AgentNotFoundError';
  }
}
