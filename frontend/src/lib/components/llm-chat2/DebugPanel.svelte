<script lang="ts">
	import { ChevronDown, ChevronRight, FileText, Clock, Coins, Zap } from 'lucide-svelte';
	import type { SourceInfo, UsageInfo, LatencyInfo } from '$lib/api/chat';

	interface ModelPrice {
		input: number; // per million tokens
		output: number; // per million tokens
	}

	interface Props {
		sources?: SourceInfo[];
		usage?: UsageInfo;
		latency?: LatencyInfo;
		modelPrice?: ModelPrice;
	}

	let { sources = [], usage, latency, modelPrice }: Props = $props();

	// Collapsible section states
	let showSources = $state(false);
	let expandedChunks = $state<Set<number>>(new Set());

	// Calculate cost estimation
	let estimatedCost = $derived(() => {
		if (!usage || !modelPrice) return null;
		const inputCost = (usage.prompt_tokens * modelPrice.input) / 1_000_000;
		const outputCost = (usage.completion_tokens * modelPrice.output) / 1_000_000;
		return inputCost + outputCost;
	});

	function toggleChunk(index: number) {
		const newSet = new Set(expandedChunks);
		if (newSet.has(index)) {
			newSet.delete(index);
		} else {
			newSet.add(index);
		}
		expandedChunks = newSet;
	}

	function formatScore(score: number): string {
		return `${(score * 100).toFixed(1)}%`;
	}

	function formatCost(cost: number): string {
		if (cost < 0.0001) return '<$0.0001';
		return `~$${cost.toFixed(4)}`;
	}

	function formatMs(ms: number): string {
		if (ms >= 1000) {
			return `${(ms / 1000).toFixed(2)}s`;
		}
		return `${ms}ms`;
	}
</script>

<div class="mt-3 rounded-lg border bg-muted/30 text-xs">
	<!-- Stats Grid -->
	<div class="grid grid-cols-2 gap-3 p-3 sm:grid-cols-4">
		<!-- Token Usage -->
		{#if usage}
			<div class="flex items-start gap-2">
				<div class="rounded bg-blue-500/10 p-1.5">
					<Coins class="size-3.5 text-blue-500" />
				</div>
				<div>
					<p class="text-muted-foreground">Tokens</p>
					<p class="font-mono font-medium">{usage.total_tokens.toLocaleString()}</p>
					<p class="text-muted-foreground">
						{usage.prompt_tokens.toLocaleString()} in / {usage.completion_tokens.toLocaleString()} out
					</p>
				</div>
			</div>
		{/if}

		<!-- Cost Estimation -->
		{#if estimatedCost() !== null}
			<div class="flex items-start gap-2">
				<div class="rounded bg-green-500/10 p-1.5">
					<Coins class="size-3.5 text-green-500" />
				</div>
				<div>
					<p class="text-muted-foreground">Cost</p>
					<p class="font-mono font-medium">{formatCost(estimatedCost()!)}</p>
				</div>
			</div>
		{/if}

		<!-- Latency -->
		{#if latency}
			<div class="flex items-start gap-2">
				<div class="rounded bg-amber-500/10 p-1.5">
					<Clock class="size-3.5 text-amber-500" />
				</div>
				<div>
					<p class="text-muted-foreground">Latency</p>
					{#if latency.llm_ms}
						<p class="font-mono font-medium">{formatMs(latency.llm_ms)}</p>
					{/if}
					{#if latency.retrieval_ms}
						<p class="text-muted-foreground">
							RAG: {formatMs(latency.retrieval_ms)}
						</p>
					{/if}
				</div>
			</div>
		{/if}

		<!-- RAG Sources Count -->
		{#if sources.length > 0}
			<div class="flex items-start gap-2">
				<div class="rounded bg-purple-500/10 p-1.5">
					<FileText class="size-3.5 text-purple-500" />
				</div>
				<div>
					<p class="text-muted-foreground">Sources</p>
					<p class="font-mono font-medium">{sources.length} chunks</p>
				</div>
			</div>
		{/if}
	</div>

	<!-- RAG Sources List (Collapsible) -->
	{#if sources.length > 0}
		<div class="border-t">
			<button
				class="flex w-full items-center gap-2 px-3 py-2 text-left hover:bg-muted/50 transition-colors"
				onclick={() => (showSources = !showSources)}
			>
				{#if showSources}
					<ChevronDown class="size-3.5" />
				{:else}
					<ChevronRight class="size-3.5" />
				{/if}
				<span class="font-medium">Retrieved Sources</span>
			</button>

			{#if showSources}
				<div class="space-y-2 px-3 pb-3">
					{#each sources as source, index}
						<div class="rounded border bg-background/50">
							<button
								class="flex w-full items-center gap-2 px-3 py-2 text-left hover:bg-muted/30 transition-colors"
								onclick={() => toggleChunk(index)}
							>
								{#if expandedChunks.has(index)}
									<ChevronDown class="size-3 shrink-0" />
								{:else}
									<ChevronRight class="size-3 shrink-0" />
								{/if}
								<span class="flex-1 truncate font-medium">{source.filename}</span>
								<span class="shrink-0 rounded bg-primary/10 px-1.5 py-0.5 font-mono text-primary">
									{formatScore(source.score)}
								</span>
							</button>

							{#if expandedChunks.has(index)}
								<div class="border-t px-3 py-2">
									<p class="mb-1 text-muted-foreground">
										Chunk #{source.chunk_index}
									</p>
									<p class="whitespace-pre-wrap font-mono text-xs leading-relaxed">
										{source.content.slice(0, 500)}{source.content.length > 500 ? '...' : ''}
									</p>
								</div>
							{/if}
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>
