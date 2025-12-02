import { authApi } from '$lib/api';
import type { User, LoginRequest, RegisterRequest } from '$lib/types';

// Auth state using Svelte 5 runes
let user = $state<User | null>(null);
let isLoading = $state(true);
let isAuthenticated = $derived(user !== null);

// Initialize auth state from stored token
async function initialize(): Promise<void> {
	if (typeof window === 'undefined') {
		isLoading = false;
		return;
	}

	const token = localStorage.getItem('access_token');
	if (!token) {
		isLoading = false;
		return;
	}

	try {
		user = await authApi.me();
	} catch {
		// Token invalid, clear it
		localStorage.removeItem('access_token');
		localStorage.removeItem('refresh_token');
		user = null;
	} finally {
		isLoading = false;
	}
}

// Login
async function login(input: LoginRequest): Promise<void> {
	await authApi.login(input);
	user = await authApi.me();
}

// Register and auto-login
async function register(input: RegisterRequest): Promise<void> {
	// First register the user
	await authApi.register(input);
	// Then login to get tokens
	await authApi.login({ email: input.email, password: input.password });
	// Finally get user info
	user = await authApi.me();
}

// Logout
async function logout(): Promise<void> {
	await authApi.logout();
	user = null;
}

// Export auth store
export function useAuth() {
	return {
		get user() {
			return user;
		},
		get isLoading() {
			return isLoading;
		},
		get isAuthenticated() {
			return isAuthenticated;
		},
		initialize,
		login,
		register,
		logout,
	};
}

// Create singleton instance
export const auth = useAuth();
