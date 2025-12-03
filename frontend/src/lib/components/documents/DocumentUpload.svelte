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

<!-- Upload Card -->
<button
	type="button"
	class="flex flex-col rounded-lg border-2 border-dashed p-4 text-center transition-colors h-full min-h-[180px] focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
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

	<div class="flex flex-col items-center justify-center gap-3 flex-1">
		{#if isUploading}
			<!-- Uploading State -->
			<div class="flex size-14 items-center justify-center rounded-lg bg-muted">
				<div class="size-8 animate-spin rounded-full border-4 border-muted-foreground/30 border-t-primary"></div>
			</div>
			<div>
				<p class="text-sm font-medium">Uploading...</p>
				<p class="text-xs text-muted-foreground">{uploadProgress}%</p>
			</div>
			<!-- Progress Bar -->
			<div class="w-full h-1.5 overflow-hidden rounded-full bg-muted mt-1">
				<div
					class="h-full bg-primary transition-all duration-300"
					style="width: {uploadProgress}%"
				></div>
			</div>
		{:else if error}
			<!-- Error State -->
			<div class="flex size-14 items-center justify-center rounded-lg bg-destructive/10">
				<AlertCircle class="size-7 text-destructive" />
			</div>
			<div>
				<p class="text-sm font-medium text-destructive">Upload Failed</p>
				<p class="text-xs text-muted-foreground mt-1 max-w-[150px] truncate" title={error}>{error}</p>
			</div>
			<Button variant="ghost" size="sm" onclick={(e) => { e.stopPropagation(); clearMessages(); }} class="text-xs">
				Try Again
			</Button>
		{:else if success}
			<!-- Success State -->
			<div class="flex size-14 items-center justify-center rounded-lg bg-green-500/10">
				<CheckCircle class="size-7 text-green-600" />
			</div>
			<div>
				<p class="text-sm font-medium text-green-600">Uploaded!</p>
				<p class="text-xs text-muted-foreground mt-1">Click to upload more</p>
			</div>
		{:else}
			<!-- Default State -->
			<div class="flex size-14 items-center justify-center rounded-lg bg-muted">
				<Upload class="size-7 text-muted-foreground" />
			</div>
			<div>
				<p class="text-sm font-medium">Upload Document</p>
				<p class="text-xs text-muted-foreground mt-1">
					Drop file or click
				</p>
			</div>
			<p class="text-[10px] text-muted-foreground/70 mt-1">
				PDF, DOCX, TXT, MD, CSV
			</p>
		{/if}
	</div>
</button>
