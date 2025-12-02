<script lang="ts">
	import { User, Bot } from 'lucide-svelte';
	import { cn } from '$lib/utils';

	interface Props {
		role: 'user' | 'assistant';
		content: string;
		isStreaming?: boolean;
	}

	let { role, content, isStreaming = false }: Props = $props();

	let isUser = $derived(role === 'user');
</script>

<div class={cn('flex gap-3 p-4', isUser ? 'justify-end' : 'justify-start')}>
	{#if !isUser}
		<div
			class="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground"
		>
			<Bot class="size-5" />
		</div>
	{/if}

	<div
		class={cn(
			'max-w-[80%] rounded-2xl px-4 py-2 text-sm',
			isUser ? 'bg-primary text-primary-foreground rounded-br-md' : 'bg-muted rounded-bl-md'
		)}
	>
		<p class="whitespace-pre-wrap">{content}</p>
		{#if isStreaming && !isUser}
			<span class="inline-block size-2 animate-pulse rounded-full bg-current ml-1"></span>
		{/if}
	</div>

	{#if isUser}
		<div
			class="flex size-8 shrink-0 items-center justify-center rounded-full bg-secondary text-secondary-foreground"
		>
			<User class="size-5" />
		</div>
	{/if}
</div>
