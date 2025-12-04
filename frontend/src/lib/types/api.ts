// API Response Types

/**
 * Base response wrapper from backend
 * All API responses are wrapped in this format
 */
export interface BaseResponse<T> {
	trace_id: string;
	data: T;
}

export interface ErrorResponse {
	trace_id: string;
	error: string;
	detail?: string;
}

export class ApiException extends Error {
	status: number;
	traceId?: string;
	detail?: string;

	constructor(status: number, message: string, traceId?: string, detail?: string) {
		super(message);
		this.name = 'ApiException';
		this.status = status;
		this.traceId = traceId;
		this.detail = detail;
	}
}

// Auth Types
export interface LoginRequest {
	email: string;
	password: string;
}

export interface RegisterRequest {
	email: string;
	username: string;
	password: string;
	first_name?: string;
	last_name?: string;
}

export interface TokenResponse {
	access_token: string;
	refresh_token: string;
	token_type: string;
}

export interface RefreshTokenRequest {
	refresh_token: string;
}

// User Types
export interface User {
	id: number;
	email: string;
	username: string;
	first_name: string | null;
	last_name: string | null;
	is_active: boolean;
	is_superuser: boolean;
	tier: 'free' | 'pro' | 'enterprise';
}

// Helper to get display name
export function getUserDisplayName(user: User): string {
	if (user.first_name && user.last_name) {
		return `${user.first_name} ${user.last_name}`;
	}
	if (user.first_name) {
		return user.first_name;
	}
	return user.username;
}

// Project Types
export interface Project {
	id: number;
	name: string;
	description?: string;
	privacy_level: 'strict' | 'moderate' | 'off';
	created_at: string;
	updated_at: string;
}

// Chat Types
export interface Message {
	id: string;
	role: 'user' | 'assistant' | 'system';
	content: string;
	sources?: Source[];
	created_at: string;
}

export interface Source {
	document_id: string;
	document_name: string;
	chunk_id: string;
	page?: number;
	score: number;
	content: string;
}

export interface ChatRequest {
	message: string;
	project_id?: number;
	conversation_id?: string;
	stream?: boolean;
}

export interface Conversation {
	id: string;
	project_id: number;
	title: string;
	messages: Message[];
	created_at: string;
	updated_at: string;
}

// Document Types
export interface Document {
	id: number;
	project_id: number;
	name: string;
	type: 'pdf' | 'docx' | 'txt' | 'md' | 'csv';
	size: number;
	status: 'pending' | 'processing' | 'ready' | 'error';
	chunk_count?: number;
	error_message?: string;
	created_at: string;
	updated_at: string;
}

// Fine-tuning Types
export interface FinetuneJob {
	id: number;
	name: string;
	status: 'pending' | 'running' | 'completed' | 'failed';
	progress?: number;
	base_model: string;
	dataset_id: string;
	hyperparameters: Record<string, unknown>;
	metrics?: Record<string, number>;
	error_message?: string;
	created_at: string;
	updated_at: string;
	completed_at?: string;
}

// Message Response (generic)
export interface MessageResponse {
	message: string;
}
