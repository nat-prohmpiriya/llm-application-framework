<script lang="ts">
	import { FileText, ChevronDown, ChevronUp, ExternalLink } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import type { SourceInfo } from '$lib/api/chat';

	interface Props {
		sources: SourceInfo[];
	}

	let { sources }: Props = $props();

	let expandedIds = $state<Set<string>>(new Set());

	function toggleExpand(index: number) {
		const key = `${index}`;
		const newSet = new Set(expandedIds);
		if (newSet.has(key)) {
			newSet.delete(key);
		} else {
			newSet.add(key);
		}
		expandedIds = newSet;
	}

	function formatScore(score: number): string {
		return (score * 100).toFixed(0) + '%';
	}

	function getDocumentUrl(documentId: string): string {
		return `/documents?doc=${documentId}`;
	}
</script>

{#if sources.length > 0}
	<div class="mt-3 space-y-2">
		<p class="text-xs font-medium text-muted-foreground">Sources ({sources.length})</p>
		<div class="space-y-1">
			{#each sources as source, index}
				{@const isExpanded = expandedIds.has(`${index}`)}
				<div class="rounded-lg border bg-muted/30 text-xs">
					<button
						type="button"
						class="flex w-full items-center gap-2 p-2 text-left hover:bg-muted/50"
						onclick={() => toggleExpand(index)}
					>
						<FileText class="size-3.5 shrink-0 text-muted-foreground" />
						<span class="flex-1 truncate font-medium">{source.filename}</span>
						<span class="shrink-0 text-muted-foreground">
							{formatScore(source.score)}
						</span>
						{#if isExpanded}
							<ChevronUp class="size-3.5 shrink-0 text-muted-foreground" />
						{:else}
							<ChevronDown class="size-3.5 shrink-0 text-muted-foreground" />
						{/if}
					</button>
					{#if isExpanded}
						<div class="border-t bg-background p-2">
							<p class="whitespace-pre-wrap text-muted-foreground">{source.content}</p>
							<div class="mt-2 flex items-center justify-between">
								<p class="text-[10px] text-muted-foreground/70">
									Chunk #{source.chunk_index}
								</p>
								<a
									href={getDocumentUrl(source.document_id)}
									class="inline-flex items-center gap-1 text-[10px] text-primary hover:underline"
									onclick={(e) => e.stopPropagation()}
								>
									<ExternalLink class="size-3" />
									View document
								</a>
							</div>
						</div>
					{/if}
				</div>
			{/each}
		</div>
	</div>
{/if}
