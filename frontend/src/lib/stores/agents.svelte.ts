import { agentsApi, type AgentInfo } from '$lib/api';

const STORAGE_KEY = 'selected_agent_slug';

class AgentStore {
	agents = $state<AgentInfo[]>([]);
	selectedAgentSlug = $state<string | null>(null);
	isLoading = $state(false);
	error = $state<string | null>(null);

	selectedAgent = $derived(
		this.selectedAgentSlug ? this.agents.find((a) => a.slug === this.selectedAgentSlug) : null
	);

	async fetchAgents() {
		this.isLoading = true;
		this.error = null;

		try {
			const response = await agentsApi.list();
			this.agents = response.agents;
		} catch (e) {
			this.error = e instanceof Error ? e.message : 'Failed to fetch agents';
		} finally {
			this.isLoading = false;
		}
	}

	selectAgent(slug: string | null) {
		this.selectedAgentSlug = slug;
		if (typeof window !== 'undefined') {
			if (slug) {
				localStorage.setItem(STORAGE_KEY, slug);
			} else {
				localStorage.removeItem(STORAGE_KEY);
			}
		}
	}

	initFromStorage() {
		if (typeof window === 'undefined') return;

		const stored = localStorage.getItem(STORAGE_KEY);
		if (stored) {
			this.selectedAgentSlug = stored;
		}
	}

	get currentAgents() {
		return this.agents;
	}

	get currentSelectedSlug() {
		return this.selectedAgentSlug;
	}

	get currentSelectedAgent() {
		return this.selectedAgent;
	}

	get loading() {
		return this.isLoading;
	}

	get currentError() {
		return this.error;
	}
}

export const agentStore = new AgentStore();
