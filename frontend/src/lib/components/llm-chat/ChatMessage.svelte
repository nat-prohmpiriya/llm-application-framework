<script lang="ts">
	import { User, Bot, Copy, Check, RefreshCw } from 'lucide-svelte';
	import { cn } from '$lib/utils';
	import { Marked } from 'marked';
	import { markedHighlight } from 'marked-highlight';
	import hljs from 'highlight.js';
	import 'highlight.js/styles/github-dark.css';
	import type { SourceInfo } from '$lib/api/chat';
	import SourceCitation from './SourceCitation.svelte';

	// Configure marked with highlight.js
	const markedInstance = new Marked(
		markedHighlight({
			emptyLangClass: 'hljs',
			langPrefix: 'hljs language-',
			highlight(code, lang) {
				const language = hljs.getLanguage(lang) ? lang : 'plaintext';
				return hljs.highlight(code, { language }).value;
			}
		})
	);

	markedInstance.setOptions({
		breaks: true,
		gfm: true
	});

	interface Props {
		role: 'user' | 'assistant';
		content: string;
		isStreaming?: boolean;
		sources?: SourceInfo[];
		createdAt?: Date;
		isLastAssistant?: boolean;
		onRegenerate?: () => void;
	}

	let { role, content, isStreaming = false, sources = [], createdAt, isLastAssistant = false, onRegenerate }: Props = $props();

	// Format time as HH:MM (24-hour format)
	let formattedTime = $derived(
		createdAt ? createdAt.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit', hour12: false }) : null
	);

	let isUser = $derived(role === 'user');

	// Render markdown to HTML (skip during streaming for performance)
	let renderedContent = $derived(
		isUser ? content : (isStreaming ? content : markedInstance.parse(content, { async: false }) as string)
	);

	// Copy button state
	let copied = $state(false);

	async function handleCopy() {
		await navigator.clipboard.writeText(content);
		copied = true;
		setTimeout(() => {
			copied = false;
		}, 2000);
	}
</script>

<div class={cn('flex gap-3 p-4 min-w-0', isUser ? 'justify-end' : 'justify-start')}>
	{#if !isUser}
		<div
			class="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground"
		>
			<Bot class="size-5" />
		</div>
	{/if}

	<div
		class={cn(
			'group relative max-w-[80%] rounded-2xl px-4 py-2 text-sm overflow-hidden min-w-0',
			isUser ? 'bg-primary text-primary-foreground rounded-br-md' : 'bg-muted rounded-bl-md'
		)}
	>
		<!-- Action buttons -->
		<div class={cn(
			'absolute top-1 right-1 flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity',
		)}>
			<!-- Regenerate button (only for last assistant message) -->
			{#if isLastAssistant && !isStreaming && onRegenerate}
				<button
					onclick={onRegenerate}
					class="p-1 rounded hover:bg-background/50 text-muted-foreground"
					title="Regenerate response"
				>
					<RefreshCw class="size-3.5" />
				</button>
			{/if}
			<!-- Copy button -->
			<button
				onclick={handleCopy}
				class={cn(
					'p-1 rounded',
					isUser
						? 'hover:bg-primary-foreground/20 text-primary-foreground'
						: 'hover:bg-background/50 text-muted-foreground'
				)}
				title="Copy message"
			>
				{#if copied}
					<Check class="size-3.5" />
				{:else}
					<Copy class="size-3.5" />
				{/if}
			</button>
		</div>
		{#if isUser}
			<p class="whitespace-pre-wrap break-words overflow-wrap-anywhere">{content}</p>
		{:else if isStreaming}
			<!-- During streaming: show raw text for performance -->
			<p class="whitespace-pre-wrap break-words overflow-wrap-anywhere">{content}</p>
		{:else}
			<!-- After streaming: render markdown -->
			<div class="prose prose-sm dark:prose-invert max-w-none overflow-wrap-anywhere [word-break:break-word]">
				{@html renderedContent}
			</div>
		{/if}
		{#if isStreaming && !isUser}
			<span class="inline-block size-2 animate-pulse rounded-full bg-current ml-1"></span>
		{/if}

		<!-- Sources -->
		{#if !isUser && !isStreaming && sources.length > 0}
			<SourceCitation {sources} />
		{/if}

		<!-- Timestamp -->
		{#if formattedTime && !isStreaming}
			<div class="mt-1 text-right text-xs text-muted-foreground/70">
				{formattedTime}
			</div>
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

<style>
	/* Markdown content styles */
	.prose :global(p) {
		margin-bottom: 0.5rem;
	}
	.prose :global(p:last-child) {
		margin-bottom: 0;
	}
	.prose :global(ul),
	.prose :global(ol) {
		margin: 0.5rem 0;
		padding-left: 1.5rem;
	}
	.prose :global(li) {
		margin: 0.25rem 0;
	}
	.prose :global(code) {
		background-color: hsl(var(--muted));
		padding: 0.125rem 0.25rem;
		border-radius: 0.25rem;
		font-size: 0.875em;
	}
	.prose :global(pre) {
		background-color: hsl(var(--muted));
		padding: 0.75rem;
		border-radius: 0.5rem;
		overflow-x: auto;
		margin: 0.5rem 0;
	}
	.prose :global(pre code) {
		background: none;
		padding: 0;
	}
	.prose :global(strong) {
		font-weight: 600;
	}
	.prose :global(h1),
	.prose :global(h2),
	.prose :global(h3),
	.prose :global(h4) {
		font-weight: 600;
		margin: 0.75rem 0 0.5rem 0;
	}
	.prose :global(blockquote) {
		border-left: 3px solid hsl(var(--border));
		padding-left: 0.75rem;
		margin: 0.5rem 0;
		color: hsl(var(--muted-foreground));
	}
</style>
