<script lang="ts">
	import * as Card from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import type { AgentInfo } from '$lib/api';

	interface Props {
		agent: AgentInfo;
		selected?: boolean;
		onclick?: () => void;
	}

	let { agent, selected = false, onclick }: Props = $props();

	function getAgentIcon(icon?: string): string {
		if (!icon) return '🤖';
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

<button type="button" class="w-full text-left" onclick={onclick}>
	<Card.Root
		class="transition-all hover:shadow-md {selected
			? 'ring-2 ring-primary border-primary'
			: 'hover:border-muted-foreground/50'}"
	>
		<Card.Header class="pb-3">
			<div class="flex items-center gap-3">
				<span class="text-2xl">{getAgentIcon(agent.icon)}</span>
				<Card.Title class="text-base">{agent.name}</Card.Title>
			</div>
		</Card.Header>
		<Card.Content class="pt-0">
			{#if agent.description}
				<p class="text-sm text-muted-foreground mb-3 line-clamp-2">
					{agent.description}
				</p>
			{/if}
			{#if agent.tools && agent.tools.length > 0}
				<div class="flex flex-wrap gap-1.5">
					{#each agent.tools as tool}
						<Badge variant="secondary" class="text-xs">
							{tool}
						</Badge>
					{/each}
				</div>
			{/if}
		</Card.Content>
	</Card.Root>
</button>
