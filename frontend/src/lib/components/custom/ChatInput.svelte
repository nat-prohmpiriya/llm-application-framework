<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import ImageIcon from '@lucide/svelte/icons/image';
	import SendIcon from '@lucide/svelte/icons/send';

	let { onSend, disabled = false, placeholder = 'Type your message...' } = $props<{
		onSend: (message: string) => void;
		disabled?: boolean;
		placeholder?: string;
	}>();

	let message = $state('');
	let textareaRef = $state<HTMLTextAreaElement | null>(null);

	function handleSubmit(e: Event) {
		e.preventDefault();
		if (message.trim() && !disabled) {
			onSend(message.trim());
			message = '';
			if (textareaRef) {
				textareaRef.style.height = 'auto';
			}
		}
	}

	function handleKeyDown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			handleSubmit(e);
		}
	}

	function handleInput() {
		if (textareaRef) {
			textareaRef.style.height = 'auto';
			textareaRef.style.height = Math.min(textareaRef.scrollHeight, 200) + 'px';
		}
	}
</script>

<form onsubmit={handleSubmit} class="relative">
	<div class="flex items-end gap-2 rounded-2xl border bg-background px-4 py-3 shadow-sm focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2">
		<!-- Image upload button (placeholder for future) -->
		<Button
			type="button"
			variant="ghost"
			size="icon"
			class="h-8 w-8 shrink-0 text-muted-foreground hover:text-foreground"
			disabled={disabled}
		>
			<ImageIcon class="h-5 w-5" />
			<span class="sr-only">Attach image</span>
		</Button>

		<!-- Text input -->
		<textarea
			bind:this={textareaRef}
			bind:value={message}
			onkeydown={handleKeyDown}
			oninput={handleInput}
			{placeholder}
			{disabled}
			rows="1"
			class="flex-1 resize-none bg-transparent text-sm placeholder:text-muted-foreground focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 min-h-[24px] max-h-[200px] py-1"
		></textarea>

		<!-- Send button -->
		<Button
			type="submit"
			variant="ghost"
			size="icon"
			class="h-8 w-8 shrink-0 text-muted-foreground hover:text-foreground disabled:opacity-30"
			disabled={disabled || !message.trim()}
		>
			<SendIcon class="h-5 w-5" />
			<span class="sr-only">Send message</span>
		</Button>
	</div>
</form>
