<script lang="ts">
	import { onMount } from 'svelte';
	import { ChevronDown, MessageSquare, Bot } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { agentStore } from '$lib/stores/agents.svelte';

	interface Props {
		onSelect?: (slug: string | null) => void;
		disabled?: boolean;
	}

	let { onSelect, disabled = false }: Props = $props();

	onMount(() => {
		agentStore.initFromStorage();
		agentStore.fetchAgents();
	});

	function handleSelect(slug: string | null) {
		agentStore.selectAgent(slug);
		onSelect?.(slug);
	}

	function getAgentIcon(icon?: string): string {
		if (!icon) return '';
		const iconMap: Record<string, string> = {
			search: '🔍',
			calculator: '🔢',
			code: '💻',
			write: '✍️',
			chart: '📊',
			brain: '🧠',
			robot: '🤖',
			sparkles: '✨',
		};
		return iconMap[icon] || '🤖';
	}
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger>
		{#snippet child({ props })}
			<Button
				variant="outline"
				class="min-w-[180px] justify-between gap-2"
				{disabled}
				{...props}
			>
				{#if agentStore.currentSelectedAgent}
					<span class="flex items-center gap-2">
						<span>{getAgentIcon(agentStore.currentSelectedAgent.icon)}</span>
						<span class="font-medium">{agentStore.currentSelectedAgent.name}</span>
					</span>
				{:else}
					<span class="flex items-center gap-2">
						<MessageSquare class="size-4" />
						<span class="text-muted-foreground">Direct Chat</span>
					</span>
				{/if}
				<ChevronDown class="size-4 opacity-50" />
			</Button>
		{/snippet}
	</DropdownMenu.Trigger>
	<DropdownMenu.Content class="w-[240px]">
		<DropdownMenu.Item
			class="flex cursor-pointer items-center gap-2"
			onclick={() => handleSelect(null)}
		>
			<MessageSquare class="size-4" />
			<div class="flex flex-col gap-0.5">
				<span class="font-medium">Direct Chat</span>
				<span class="text-xs text-muted-foreground">Chat without agent</span>
			</div>
		</DropdownMenu.Item>

		{#if agentStore.currentAgents.length > 0}
			<DropdownMenu.Separator />
			<DropdownMenu.Label
				class="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground"
			>
				<Bot class="size-3" />
				<span>Agents</span>
			</DropdownMenu.Label>

			{#each agentStore.currentAgents as agent}
				<DropdownMenu.Item
					class="flex cursor-pointer items-center gap-2"
					onclick={() => handleSelect(agent.slug)}
				>
					<span class="text-base">{getAgentIcon(agent.icon)}</span>
					<div class="flex flex-col gap-0.5">
						<span class="font-medium">{agent.name}</span>
						{#if agent.description}
							<span class="text-xs text-muted-foreground line-clamp-1">
								{agent.description}
							</span>
						{/if}
					</div>
				</DropdownMenu.Item>
			{/each}
		{/if}

		{#if agentStore.loading}
			<DropdownMenu.Item disabled class="text-muted-foreground">
				Loading agents...
			</DropdownMenu.Item>
		{/if}

		{#if agentStore.currentError}
			<DropdownMenu.Item disabled class="text-destructive">
				{agentStore.currentError}
			</DropdownMenu.Item>
		{/if}
	</DropdownMenu.Content>
</DropdownMenu.Root>
