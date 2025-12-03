<script lang="ts">
	import { goto } from '$app/navigation';
	import { FileText, FileSpreadsheet, File, Trash2, ExternalLink, Pencil } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import type { Document, DocumentStatus } from '$lib/api/documents';

	interface Props {
		document: Document;
		onDelete: (id: string) => void;
		onEdit: (document: Document) => void;
	}

	let { document, onDelete, onEdit }: Props = $props();

	let showConfirm = $state(false);
	let isClickable = $derived(document.status === 'ready');

	function getStatusVariant(status: DocumentStatus): 'default' | 'secondary' | 'destructive' | 'outline' {
		switch (status) {
			case 'ready':
				return 'default';
			case 'processing':
			case 'pending':
				return 'secondary';
			case 'error':
				return 'destructive';
			default:
				return 'outline';
		}
	}

	function getStatusLabel(status: DocumentStatus): string {
		switch (status) {
			case 'ready':
				return 'Ready';
			case 'processing':
				return 'Processing';
			case 'pending':
				return 'Pending';
			case 'error':
				return 'Error';
			default:
				return status;
		}
	}

	function formatFileSize(bytes: number): string {
		if (bytes < 1024) return `${bytes} B`;
		if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
		return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
	}

	function handleEditClick(e: MouseEvent) {
		e.stopPropagation();
		onEdit(document);
	}

	function handleDeleteClick(e: MouseEvent) {
		e.stopPropagation();
		showConfirm = true;
	}

	function handleConfirmDelete(e: MouseEvent) {
		e.stopPropagation();
		onDelete(document.id);
		showConfirm = false;
	}

	function handleCancelDelete(e: MouseEvent) {
		e.stopPropagation();
		showConfirm = false;
	}

	function handleClick() {
		if (isClickable) {
			goto(`/documents/${document.id}`);
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') {
			handleClick();
		}
	}
</script>

<div
	class="flex flex-col rounded-lg border bg-card p-4 transition-colors h-full min-h-[180px] {isClickable ? 'cursor-pointer hover:bg-muted/50 hover:border-primary/50' : 'hover:bg-muted/30'}"
	onclick={handleClick}
	onkeydown={handleKeydown}
	role={isClickable ? 'button' : undefined}
	tabindex={isClickable ? 0 : undefined}
>
	<!-- File Icon -->
	<div class="flex items-center justify-center mb-3">
		<div class="flex size-14 shrink-0 items-center justify-center rounded-lg bg-muted">
			{#if document.file_type.toLowerCase().includes('pdf')}
				<FileText class="size-7 text-muted-foreground" />
			{:else if document.file_type.toLowerCase().includes('csv') || document.file_type.toLowerCase().includes('spreadsheet')}
				<FileSpreadsheet class="size-7 text-muted-foreground" />
			{:else}
				<File class="size-7 text-muted-foreground" />
			{/if}
		</div>
	</div>

	<!-- File Info -->
	<div class="flex-1 min-w-0 text-center">
		<p class="truncate text-sm font-medium" title={document.filename}>
			{document.filename}
		</p>
		<div class="mt-1 flex items-center justify-center gap-2 text-xs text-muted-foreground">
			<span>{formatFileSize(document.file_size)}</span>
			{#if document.chunk_count > 0}
				<span>&middot;</span>
				<span>{document.chunk_count} chunks</span>
			{/if}
		</div>
	</div>

	<!-- Status Badge -->
	<div class="flex justify-center mt-3">
		<Badge variant={getStatusVariant(document.status)}>
			{getStatusLabel(document.status)}
		</Badge>
	</div>

	<!-- Actions -->
	<div class="flex items-center justify-center gap-2 mt-3 pt-3 border-t">
		{#if showConfirm}
			<Button variant="destructive" size="sm" onclick={handleConfirmDelete}>
				Delete
			</Button>
			<Button variant="outline" size="sm" onclick={handleCancelDelete}>
				Cancel
			</Button>
		{:else}
			{#if isClickable}
				<Button
					variant="ghost"
					size="icon-sm"
					onclick={(e) => { e.stopPropagation(); goto(`/documents/${document.id}`); }}
					title="View document"
					class="text-muted-foreground hover:text-primary"
				>
					<ExternalLink class="size-4" />
				</Button>
			{/if}
			<Button
				variant="ghost"
				size="icon-sm"
				onclick={handleEditClick}
				title="Edit document"
				class="text-muted-foreground hover:text-primary"
			>
				<Pencil class="size-4" />
			</Button>
			<Button
				variant="ghost"
				size="icon-sm"
				onclick={handleDeleteClick}
				title="Delete document"
				class="text-muted-foreground hover:text-destructive"
			>
				<Trash2 class="size-4" />
			</Button>
		{/if}
	</div>
</div>
