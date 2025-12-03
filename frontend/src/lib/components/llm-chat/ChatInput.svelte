<script lang="ts">
	import { Image, Send, Square } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';

	interface Props {
		value?: string;
		placeholder?: string;
		disabled?: boolean;
		loading?: boolean;
		onSend: (message: string) => void;
		onStop?: () => void;
		onImageUpload?: (files: FileList) => void;
	}

	let {
		value = $bindable(''),
		placeholder = 'Type your message...',
		disabled = false,
		loading = false,
		onSend,
		onStop,
		onImageUpload
	}: Props = $props();

	let textareaRef = $state<HTMLTextAreaElement | null>(null);
	let fileInputRef = $state<HTMLInputElement | null>(null);

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSend();
		}
	}

	function handleSend() {
		const trimmed = value.trim();
		if (trimmed && !disabled && !loading) {
			onSend(trimmed);
			value = '';
			// Reset textarea height
			if (textareaRef) {
				textareaRef.style.height = 'auto';
			}
		}
	}

	function handleInput() {
		// Auto-resize textarea
		if (textareaRef) {
			textareaRef.style.height = 'auto';
			textareaRef.style.height = `${Math.min(textareaRef.scrollHeight, 200)}px`;
		}
	}

	function handleImageClick() {
		fileInputRef?.click();
	}

	function handleFileChange(event: Event) {
		const input = event.target as HTMLInputElement;
		if (input.files && input.files.length > 0 && onImageUpload) {
			onImageUpload(input.files);
			input.value = '';
		}
	}

	let canSend = $derived(value.trim().length > 0 && !disabled && !loading);
</script>

<div class="border-t p-4 rounded-b-xl bg-gray-50">
	<div class="flex items-end gap-2 rounded-lg border bg-muted/30 p-2">
		<!-- Image Upload Button -->
		{#if onImageUpload}
			<Button
				variant="ghost"
				size="icon-sm"
				onclick={handleImageClick}
				disabled={disabled || loading}
				title="Upload image"
				class="shrink-0"
			>
				<Image class="size-5 text-muted-foreground" />
			</Button>
			<input
				bind:this={fileInputRef}
				type="file"
				accept="image/*"
				multiple
				class="hidden"
				onchange={handleFileChange}
			/>
		{/if}

		<!-- Text Input -->
		<textarea
			bind:this={textareaRef}
			bind:value
			{placeholder}
			disabled={disabled || loading}
			rows={1}
			class="flex-1 resize-none bg-transparent text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
			onkeydown={handleKeydown}
			oninput={handleInput}
		></textarea>

		<!-- Send/Stop Button -->
		{#if loading && onStop}
			<Button
				variant="ghost"
				size="icon-sm"
				onclick={onStop}
				title="Stop generating"
				class="shrink-0"
			>
				<Square class="size-4 fill-destructive text-destructive" />
			</Button>
		{:else}
			<Button
				variant="ghost"
				size="icon-sm"
				onclick={handleSend}
				disabled={!canSend}
				title="Send message"
				class="shrink-0"
			>
				<Send class="size-5 {canSend ? 'text-primary' : 'text-muted-foreground'}" />
			</Button>
		{/if}
	</div>
</div>
