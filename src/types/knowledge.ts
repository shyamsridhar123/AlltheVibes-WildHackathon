import { z } from 'zod';

/**
 * Knowledge Type Definitions
 *
 * Core type definitions for the shared knowledge graph in the Agent Swarm Platform.
 * Knowledge entries represent insights, learnings, and information shared between agents.
 */

/**
 * Knowledge entry type classification
 */
export enum KnowledgeType {
  /** Factual information */
  FACT = 'fact',
  /** Procedural knowledge (how to do something) */
  PROCEDURE = 'procedure',
  /** Insight or observation */
  INSIGHT = 'insight',
  /** Lesson learned from execution */
  LESSON = 'lesson',
  /** Reference to external resource */
  REFERENCE = 'reference',
  /** Relationship between entities */
  RELATIONSHIP = 'relationship',
  /** Agent capability or skill */
  CAPABILITY = 'capability',
  /** Context or background information */
  CONTEXT = 'context'
}

/**
 * Knowledge confidence level
 */
export enum KnowledgeConfidence {
  /** Highly confident (verified through multiple sources) */
  HIGH = 'high',
  /** Moderately confident (single source or limited verification) */
  MEDIUM = 'medium',
  /** Low confidence (speculative or unverified) */
  LOW = 'low',
  /** Unknown confidence level */
  UNKNOWN = 'unknown'
}

/**
 * Knowledge source information
 */
export interface KnowledgeSource {
  /** Agent ID that created this knowledge */
  agentId: string;
  /** Agent type that created this knowledge */
  agentType: string;
  /** Task ID associated with this knowledge */
  taskId?: string;
  /** Timestamp when knowledge was created */
  timestamp: Date;
  /** Source reliability score (0-1) */
  reliability?: number;
}

/**
 * Knowledge metadata for tracking and versioning
 */
export interface KnowledgeMetadata {
  /** Knowledge entry creation timestamp */
  createdAt: Date;
  /** Last update timestamp */
  updatedAt: Date;
  /** Knowledge version number */
  version: number;
  /** Number of times this knowledge has been accessed */
  accessCount: number;
  /** Number of times this knowledge has been validated */
  validationCount: number;
  /** Tags for categorization */
  tags: string[];
  /** Related knowledge entry IDs */
  relatedEntries?: string[];
  /** Custom metadata */
  custom?: Record<string, unknown>;
}

/**
 * Knowledge validation record
 */
export interface KnowledgeValidation {
  /** Agent ID that validated this knowledge */
  validatorAgentId: string;
  /** Whether validation was successful */
  isValid: boolean;
  /** Validation timestamp */
  timestamp: Date;
  /** Validation notes or comments */
  notes?: string;
}

/**
 * Knowledge entry - represents a single piece of shared knowledge
 */
export interface KnowledgeEntry {
  /** Unique knowledge entry identifier */
  id: string;
  /** Knowledge type classification */
  type: KnowledgeType;
  /** Knowledge title or summary */
  title: string;
  /** Detailed knowledge content */
  content: string;
  /** Confidence level in this knowledge */
  confidence: KnowledgeConfidence;
  /** Source information */
  source: KnowledgeSource;
  /** Knowledge metadata */
  metadata: KnowledgeMetadata;
  /** Validation records */
  validations?: KnowledgeValidation[];
  /** Vector embedding for semantic search (stored as array of numbers) */
  embedding?: number[];
  /** Whether this knowledge is active/visible */
  isActive: boolean;
}

/**
 * Knowledge query parameters
 */
export interface KnowledgeQuery {
  /** Search query text */
  query?: string;
  /** Filter by knowledge type */
  type?: KnowledgeType[];
  /** Filter by tags */
  tags?: string[];
  /** Filter by minimum confidence level */
  minConfidence?: KnowledgeConfidence;
  /** Filter by agent ID */
  agentId?: string;
  /** Filter by task ID */
  taskId?: string;
  /** Maximum number of results */
  limit?: number;
  /** Offset for pagination */
  offset?: number;
  /** Whether to include inactive knowledge */
  includeInactive?: boolean;
}

/**
 * Knowledge graph relationship
 */
export interface KnowledgeRelationship {
  /** Unique relationship identifier */
  id: string;
  /** Source knowledge entry ID */
  fromId: string;
  /** Target knowledge entry ID */
  toId: string;
  /** Relationship type */
  type: string;
  /** Relationship strength (0-1) */
  strength?: number;
  /** Relationship properties */
  properties?: Record<string, unknown>;
  /** Timestamp when relationship was created */
  createdAt: Date;
}

/**
 * Zod Schemas for Knowledge Validation
 */

// KnowledgeType schema
export const KnowledgeTypeSchema = z.nativeEnum(KnowledgeType);

// KnowledgeConfidence schema
export const KnowledgeConfidenceSchema = z.nativeEnum(KnowledgeConfidence);

// KnowledgeSource schema
export const KnowledgeSourceSchema = z.object({
  agentId: z.string(),
  agentType: z.string(),
  taskId: z.string().optional(),
  timestamp: z.date(),
  reliability: z.number().min(0).max(1).optional()
});

// KnowledgeMetadata schema
export const KnowledgeMetadataSchema = z.object({
  createdAt: z.date(),
  updatedAt: z.date(),
  version: z.number().int().min(1),
  accessCount: z.number().int().min(0),
  validationCount: z.number().int().min(0),
  tags: z.array(z.string()),
  relatedEntries: z.array(z.string()).optional(),
  custom: z.record(z.unknown()).optional()
});

// KnowledgeValidation schema
export const KnowledgeValidationSchema = z.object({
  validatorAgentId: z.string(),
  isValid: z.boolean(),
  timestamp: z.date(),
  notes: z.string().optional()
});

// KnowledgeEntry schema
export const KnowledgeEntrySchema = z.object({
  id: z.string(),
  type: KnowledgeTypeSchema,
  title: z.string(),
  content: z.string(),
  confidence: KnowledgeConfidenceSchema,
  source: KnowledgeSourceSchema,
  metadata: KnowledgeMetadataSchema,
  validations: z.array(KnowledgeValidationSchema).optional(),
  embedding: z.array(z.number()).optional(),
  isActive: z.boolean()
});

// KnowledgeQuery schema
export const KnowledgeQuerySchema = z.object({
  query: z.string().optional(),
  type: z.array(KnowledgeTypeSchema).optional(),
  tags: z.array(z.string()).optional(),
  minConfidence: KnowledgeConfidenceSchema.optional(),
  agentId: z.string().optional(),
  taskId: z.string().optional(),
  limit: z.number().int().min(1).max(1000).optional(),
  offset: z.number().int().min(0).optional(),
  includeInactive: z.boolean().optional()
});

// KnowledgeRelationship schema
export const KnowledgeRelationshipSchema = z.object({
  id: z.string(),
  fromId: z.string(),
  toId: z.string(),
  type: z.string(),
  strength: z.number().min(0).max(1).optional(),
  properties: z.record(z.unknown()).optional(),
  createdAt: z.date()
});

/**
 * Type guard to check if a value is a valid KnowledgeEntry
 */
export function isKnowledgeEntry(value: unknown): value is KnowledgeEntry {
  try {
    KnowledgeEntrySchema.parse(value);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate and parse a knowledge entry object
 */
export function parseKnowledgeEntry(value: unknown): KnowledgeEntry {
  return KnowledgeEntrySchema.parse(value);
}

/**
 * Type guard to check if a value is a valid KnowledgeQuery
 */
export function isKnowledgeQuery(value: unknown): value is KnowledgeQuery {
  try {
    KnowledgeQuerySchema.parse(value);
    return true;
  } catch {
    return false;
  }
}

/**
 * Validate and parse a knowledge query object
 */
export function parseKnowledgeQuery(value: unknown): KnowledgeQuery {
  return KnowledgeQuerySchema.parse(value);
}

/**
 * Create a new knowledge entry with default values
 */
export function createKnowledgeEntry(params: {
  type: KnowledgeType;
  title: string;
  content: string;
  source: KnowledgeSource;
  confidence?: KnowledgeConfidence;
  tags?: string[];
  embedding?: number[];
}): KnowledgeEntry {
  const now = new Date();
  return {
    id: crypto.randomUUID(),
    type: params.type,
    title: params.title,
    content: params.content,
    confidence: params.confidence ?? KnowledgeConfidence.MEDIUM,
    source: params.source,
    metadata: {
      createdAt: now,
      updatedAt: now,
      version: 1,
      accessCount: 0,
      validationCount: 0,
      tags: params.tags ?? []
    },
    embedding: params.embedding,
    isActive: true
  };
}
