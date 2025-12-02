<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { FileText, Filter } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Select from '$lib/components/ui/select';
	import { documentsApi, type Document, type DocumentStatus } from '$lib/api/documents';
	import DocumentUpload from '$lib/components/documents/DocumentUpload.svelte';
	import DocumentItem from '$lib/components/documents/DocumentItem.svelte';

	type StatusFilter = 'all' | DocumentStatus;

	let documents = $state<Document[]>([]);
	let loading = $state(true);
	let statusFilter = $state<StatusFilter>('all');
	let pollInterval = $state<ReturnType<typeof setInterval> | null>(null);

	const filterOptions: { value: StatusFilter; label: string }[] = [
		{ value: 'all', label: 'All' },
		{ value: 'ready', label: 'Ready' },
		{ value: 'processing', label: 'Processing' },
		{ value: 'pending', label: 'Pending' },
		{ value: 'error', label: 'Error' }
	];

	let filteredDocuments = $derived(
		statusFilter === 'all'
			? documents
			: documents.filter((doc) => doc.status === statusFilter)
	);

	let hasProcessingDocuments = $derived(
		documents.some((doc) => doc.status === 'processing' || doc.status === 'pending')
	);

	onMount(async () => {
		await loadDocuments();
	});

	onDestroy(() => {
		stopPolling();
	});

	$effect(() => {
		if (hasProcessingDocuments) {
			startPolling();
		} else {
			stopPolling();
		}
	});

	function startPolling() {
		if (pollInterval) return;
		pollInterval = setInterval(async () => {
			await loadDocuments();
		}, 5000);
	}

	function stopPolling() {
		if (pollInterval) {
			clearInterval(pollInterval);
			pollInterval = null;
		}
	}

	async function loadDocuments() {
		try {
			const response = await documentsApi.list(1, 100);
			documents = response.items;
		} catch (e) {
			console.error('Failed to load documents:', e);
		} finally {
			loading = false;
		}
	}

	function handleUpload(document: Document) {
		documents = [document, ...documents];
	}

	async function handleDelete(id: string) {
		try {
			await documentsApi.delete(id);
			documents = documents.filter((doc) => doc.id !== id);
		} catch (e) {
			console.error('Failed to delete document:', e);
		}
	}

	function handleFilterChange(value: string | undefined) {
		if (value) {
			statusFilter = value as StatusFilter;
		}
	}
</script>

<svelte:head>
	<title>Documents | RAG Agent</title>
</svelte:head>

<div class="flex h-full flex-col">
	<!-- Header -->
	<div class="border-b bg-background p-4">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-2">
				<FileText class="size-5" />
				<h1 class="text-lg font-semibold">Documents</h1>
				{#if documents.length > 0}
					<span class="text-sm text-muted-foreground">({documents.length})</span>
				{/if}
			</div>

			<!-- Status Filter -->
			<Select.Root type="single" onValueChange={handleFilterChange}>
				<Select.Trigger class="w-40">
					<Filter class="mr-2 size-4" />
					<span
						>{filterOptions.find((o) => o.value === statusFilter)?.label || 'All'}</span
					>
				</Select.Trigger>
				<Select.Content>
					{#each filterOptions as option}
						<Select.Item value={option.value}>{option.label}</Select.Item>
					{/each}
				</Select.Content>
			</Select.Root>
		</div>
	</div>

	<!-- Content -->
	<div class="flex-1 overflow-auto p-4">
		<div class="mx-auto max-w-3xl space-y-6">
			<!-- Upload Zone -->
			<DocumentUpload onUpload={handleUpload} />

			<!-- Document List -->
			{#if loading}
				<div class="flex items-center justify-center py-12">
					<div
						class="size-8 animate-spin rounded-full border-4 border-muted border-t-primary"
					></div>
				</div>
			{:else if filteredDocuments.length === 0}
				<div class="rounded-lg border border-dashed flex flex-col items-center p-12">
					<FileText class="size-12 text-muted-foreground/50" />
					<h3 class="mt-4 text-lg font-medium">No documents</h3>
					<p class="mt-1 text-sm text-muted-foreground">
						{#if statusFilter !== 'all'}
							No documents with status "{statusFilter}". Try changing the filter.
						{:else}
							Upload your first document to get started with RAG.
						{/if}
					</p>
				</div>
			{:else}
				<div class="space-y-2">
					{#each filteredDocuments as document (document.id)}
						<DocumentItem {document} onDelete={handleDelete} />
					{/each}
				</div>
			{/if}

			<!-- Processing indicator -->
			{#if hasProcessingDocuments}
				<p class="text-center text-xs text-muted-foreground">
					Auto-refreshing while documents are processing...
				</p>
			{/if}
		</div>
	</div>
</div>
