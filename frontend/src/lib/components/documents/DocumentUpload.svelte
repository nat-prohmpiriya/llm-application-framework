<script lang="ts">
	import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import { documentsApi, type Document } from '$lib/api/documents';

	interface Props {
		onUpload: (document: Document) => void;
	}

	let { onUpload }: Props = $props();

	const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
	const ALLOWED_TYPES = [
		'application/pdf',
		'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
		'text/plain',
		'text/markdown',
		'text/csv'
	];
	const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt', '.md', '.csv'];

	let isDragging = $state(false);
	let isUploading = $state(false);
	let uploadProgress = $state(0);
	let error = $state<string | null>(null);
	let success = $state<string | null>(null);
	let fileInputRef = $state<HTMLInputElement | null>(null);

	function validateFile(file: File): string | null {
		const extension = '.' + file.name.split('.').pop()?.toLowerCase();
		const isValidType = ALLOWED_TYPES.includes(file.type) || ALLOWED_EXTENSIONS.includes(extension);

		if (!isValidType) {
			return `Invalid file type. Allowed: ${ALLOWED_EXTENSIONS.join(', ')}`;
		}

		if (file.size > MAX_FILE_SIZE) {
			return `File too large. Maximum size: 10MB`;
		}

		return null;
	}

	async function handleUpload(file: File) {
		const validationError = validateFile(file);
		if (validationError) {
			error = validationError;
			success = null;
			return;
		}

		error = null;
		success = null;
		isUploading = true;
		uploadProgress = 0;

		try {
			const document = await documentsApi.upload(file, (percent) => {
				uploadProgress = percent;
			});
			success = `"${file.name}" uploaded successfully`;
			onUpload(document);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Upload failed';
		} finally {
			isUploading = false;
			uploadProgress = 0;
		}
	}

	function handleDragOver(event: DragEvent) {
		event.preventDefault();
		isDragging = true;
	}

	function handleDragLeave(event: DragEvent) {
		event.preventDefault();
		isDragging = false;
	}

	function handleDrop(event: DragEvent) {
		event.preventDefault();
		isDragging = false;

		const files = event.dataTransfer?.files;
		if (files && files.length > 0) {
			handleUpload(files[0]);
		}
	}

	function handleFileChange(event: Event) {
		const input = event.target as HTMLInputElement;
		if (input.files && input.files.length > 0) {
			handleUpload(input.files[0]);
			input.value = '';
		}
	}

	function handleClick() {
		fileInputRef?.click();
	}

	function clearMessages() {
		error = null;
		success = null;
	}
</script>

<div class="space-y-3">
	<!-- Drop Zone -->
	<button
		type="button"
		class="w-full rounded-lg border-2 border-dashed p-6 text-center transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
			{isDragging
			? 'border-primary bg-primary/5'
			: 'border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/30'}
			{isUploading ? 'pointer-events-none opacity-50' : 'cursor-pointer'}"
		ondragover={handleDragOver}
		ondragleave={handleDragLeave}
		ondrop={handleDrop}
		onclick={handleClick}
		disabled={isUploading}
	>
		<input
			bind:this={fileInputRef}
			type="file"
			accept={ALLOWED_EXTENSIONS.join(',')}
			class="hidden"
			onchange={handleFileChange}
			disabled={isUploading}
		/>

		<div class="flex flex-col items-center gap-2">
			{#if isUploading}
				<div class="size-10 animate-spin rounded-full border-4 border-muted border-t-primary"></div>
				<p class="text-sm font-medium">{uploadProgress}%</p>
			{:else}
				<Upload class="size-10 text-muted-foreground" />
				<div>
					<p class="text-sm font-medium">Drop file here or click to upload</p>
					<p class="mt-1 text-xs text-muted-foreground">
						PDF, DOCX, TXT, MD, CSV (max 10MB)
					</p>
				</div>
			{/if}
		</div>
	</button>

	<!-- Progress Bar -->
	{#if isUploading}
		<div class="h-2 overflow-hidden rounded-full bg-muted">
			<div
				class="h-full bg-primary transition-all duration-300"
				style="width: {uploadProgress}%"
			></div>
		</div>
	{/if}

	<!-- Error Message -->
	{#if error}
		<div class="flex items-center gap-2 rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
			<AlertCircle class="size-4 shrink-0" />
			<span class="flex-1">{error}</span>
			<Button variant="ghost" size="sm" onclick={clearMessages} class="h-auto p-1">
				&times;
			</Button>
		</div>
	{/if}

	<!-- Success Message -->
	{#if success}
		<div class="flex items-center gap-2 rounded-lg bg-green-500/10 p-3 text-sm text-green-600">
			<CheckCircle class="size-4 shrink-0" />
			<span class="flex-1">{success}</span>
			<Button variant="ghost" size="sm" onclick={clearMessages} class="h-auto p-1">
				&times;
			</Button>
		</div>
	{/if}
</div>
