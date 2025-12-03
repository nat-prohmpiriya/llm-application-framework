import { agentsApi, type AgentInfo, type AgentCreate, type AgentUpdate } from '$lib/api';

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

	async createAgent(data: AgentCreate): Promise<AgentInfo> {
		this.isLoading = true;
		this.error = null;

		try {
			const agent = await agentsApi.create(data);
			// Refresh agents list
			await this.fetchAgents();
			return agent;
		} catch (e) {
			this.error = e instanceof Error ? e.message : 'Failed to create agent';
			throw e;
		} finally {
			this.isLoading = false;
		}
	}

	async updateAgent(agentId: string, data: AgentUpdate): Promise<AgentInfo> {
		this.isLoading = true;
		this.error = null;

		try {
			const agent = await agentsApi.update(agentId, data);
			// Refresh agents list
			await this.fetchAgents();
			return agent;
		} catch (e) {
			this.error = e instanceof Error ? e.message : 'Failed to update agent';
			throw e;
		} finally {
			this.isLoading = false;
		}
	}

	async deleteAgent(agentId: string): Promise<void> {
		this.isLoading = true;
		this.error = null;

		try {
			await agentsApi.delete(agentId);
			// Clear selection if deleted agent was selected
			const deletedAgent = this.agents.find(a => a.id === agentId);
			if (deletedAgent && this.selectedAgentSlug === deletedAgent.slug) {
				this.selectAgent(null);
			}
			// Refresh agents list
			await this.fetchAgents();
		} catch (e) {
			this.error = e instanceof Error ? e.message : 'Failed to delete agent';
			throw e;
		} finally {
			this.isLoading = false;
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
