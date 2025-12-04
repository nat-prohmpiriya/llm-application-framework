/**
 * Billing API client
 */

import { fetchApi } from './client';

// Types
export interface BillingPlan {
	id: string;
	name: string;
	display_name: string;
	description: string | null;
	plan_type: 'free' | 'pro' | 'enterprise';
	price_monthly: number;
	price_yearly: number | null;
	currency: string;
	tokens_per_month: number;
	requests_per_minute: number;
	requests_per_day: number;
	max_documents: number;
	max_projects: number;
	max_agents: number;
	allowed_models: string[];
	features: Record<string, unknown> | null;
}

export interface CheckoutRequest {
	plan_id: string;
	billing_interval: 'monthly' | 'yearly';
	success_url?: string;
	cancel_url?: string;
}

export interface CheckoutResponse {
	session_id: string;
	url: string;
}

export interface PortalResponse {
	url: string;
}

// API Functions

/**
 * Get all available billing plans
 */
export async function getPlans(): Promise<BillingPlan[]> {
	return fetchApi<BillingPlan[]>('/api/billing/plans');
}

/**
 * Create a Stripe checkout session for subscribing to a plan
 */
export async function createCheckout(request: CheckoutRequest): Promise<CheckoutResponse> {
	return fetchApi<CheckoutResponse>('/api/billing/checkout', {
		method: 'POST',
		body: JSON.stringify(request)
	});
}

/**
 * Create a Stripe customer portal session for managing subscription
 */
export async function createPortalSession(returnUrl?: string): Promise<PortalResponse> {
	return fetchApi<PortalResponse>('/api/billing/portal', {
		method: 'POST',
		body: JSON.stringify({ return_url: returnUrl })
	});
}
