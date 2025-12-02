<script lang="ts">
	import ChatMessage from './ChatMessage.svelte';
	import ChatInput from './ChatInput.svelte';

	interface Message {
		id: string;
		role: 'user' | 'assistant';
		content: string;
	}

	let { messages = [], isStreaming = false, streamingContent = '', onSend } = $props<{
		messages?: Message[];
		isStreaming?: boolean;
		streamingContent?: string;
		onSend: (message: string) => void;
	}>();

	let scrollAreaRef = $state<HTMLDivElement | null>(null);

	// Auto-scroll to bottom when new messages arrive
	$effect(() => {
		if (scrollAreaRef && (messages.length > 0 || streamingContent)) {
			setTimeout(() => {
				scrollAreaRef?.scrollTo({
					top: scrollAreaRef.scrollHeight,
					behavior: 'smooth',
				});
			}, 50);
		}
	});
</script>

<div class="flex flex-col h-full">
	<!-- Messages area -->
	<div class="flex-1 overflow-hidden">
		<div bind:this={scrollAreaRef} class="h-full overflow-y-auto">
			{#if messages.length === 0 && !isStreaming}
				<!-- Empty state - clean and minimal -->
				<div class="flex items-center justify-center h-full">
					<!-- Empty - no card, just blank space -->
				</div>
			{:else}
				<div
					class="max-w-3xl mx-auto px-4 py-6 space-y-6 border border-gray-200 rounded-xl"
				>
					{#each messages as msg (msg.id)}
						<ChatMessage message={msg.content} isUser={msg.role === 'user'} />
					{/each}

					{#if isStreaming}
						<ChatMessage message={streamingContent} isUser={false} isStreaming={true} />
					{/if}
				</div>
			{/if}
		</div>
	</div>

	<!-- Input area - centered at bottom -->
	<div class="border-t bg-background">
		<div class="max-w-3xl mx-auto px-4 py-4">
			<ChatInput
				{onSend}
				disabled={isStreaming}
				placeholder={isStreaming ? 'Waiting for response...' : 'Type your message...'}
			/>
		</div>
	</div>
</div>
