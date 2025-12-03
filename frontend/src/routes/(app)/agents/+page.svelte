<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { Bot } from 'lucide-svelte';
	import { agentStore } from '$lib/stores/agents.svelte';
	import AgentCard from '$lib/components/agents/AgentCard.svelte';

	onMount(() => {
		agentStore.initFromStorage();
		agentStore.fetchAgents();
	});

	function handleAgentClick(slug: string) {
		agentStore.selectAgent(slug);
		goto('/chat');
	}
</script>

<svelte:head>
	<title>Agents | RAG Agent</title>
</svelte:head>

<div class="flex h-full flex-col">
	<!-- Header -->
	<div class="border-b bg-background p-4">
		<div class="flex items-center gap-2">
			<Bot class="size-5" />
			<h1 class="text-lg font-semibold">Agents</h1>
			{#if agentStore.currentAgents.length > 0}
				<span class="text-sm text-muted-foreground">({agentStore.currentAgents.length})</span>
			{/if}
		</div>
		<p class="mt-1 text-sm text-muted-foreground">
			Select an agent to start a specialized conversation
		</p>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-auto p-4">
		<div class="mx-auto max-w-4xl">
			{#if agentStore.loading}
				<div class="flex items-center justify-center py-12">
					<div
						class="size-8 animate-spin rounded-full border-4 border-muted border-t-primary"
					></div>
				</div>
			{:else if agentStore.currentError}
				<div class="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
					<p class="text-destructive">{agentStore.currentError}</p>
				</div>
			{:else if agentStore.currentAgents.length === 0}
				<div class="rounded-lg border border-dashed flex flex-col items-center p-12">
					<Bot class="size-12 text-muted-foreground/50" />
					<h3 class="mt-4 text-lg font-medium">No agents available</h3>
					<p class="mt-1 text-sm text-muted-foreground">
						Agents will appear here once configured.
					</p>
				</div>
			{:else}
				<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
					{#each agentStore.currentAgents as agent (agent.slug)}
						<AgentCard
							{agent}
							selected={agentStore.currentSelectedSlug === agent.slug}
							onclick={() => handleAgentClick(agent.slug)}
						/>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
