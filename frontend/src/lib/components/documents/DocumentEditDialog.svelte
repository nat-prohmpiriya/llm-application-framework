<script lang="ts">
	import { X } from 'lucide-svelte';
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Textarea } from '$lib/components/ui/textarea';
	import { Badge } from '$lib/components/ui/badge';
	import { documentsApi, type Document, type DocumentUpdate } from '$lib/api/documents';

	interface Props {
		document: Document;
		open: boolean;
		onOpenChange: (open: boolean) => void;
		onUpdate: (document: Document) => void;
	}

	let { document, open, onOpenChange, onUpdate }: Props = $props();

	let filename = $state(document.filename);
	let description = $state(document.description || '');
	let tags = $state<string[]>(document.tags || []);
	let tagInput = $state('');
	let saving = $state(false);
	let error = $state<string | null>(null);

	// Reset form when document changes
	$effect(() => {
		filename = document.filename;
		description = document.description || '';
		tags = document.tags || [];
		tagInput = '';
		error = null;
	});

	function addTag() {
		const tag = tagInput.trim().toLowerCase();
		if (tag && !tags.includes(tag) && tags.length < 10) {
			tags = [...tags, tag];
			tagInput = '';
		}
	}

	function removeTag(tagToRemove: string) {
		tags = tags.filter((t) => t !== tagToRemove);
	}

	function handleTagKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') {
			e.preventDefault();
			addTag();
		}
	}

	async function handleSubmit() {
		if (!filename.trim()) {
			error = 'Filename is required';
			return;
		}

		saving = true;
		error = null;

		try {
			const updateData: DocumentUpdate = {};

			// Only include changed fields
			if (filename !== document.filename) {
				updateData.filename = filename;
			}
			if (description !== (document.description || '')) {
				updateData.description = description || null;
			}
			const tagsChanged =
				JSON.stringify(tags.sort()) !== JSON.stringify((document.tags || []).sort());
			if (tagsChanged) {
				updateData.tags = tags.length > 0 ? tags : null;
			}

			// Only call API if there are changes
			if (Object.keys(updateData).length > 0) {
				const updated = await documentsApi.update(document.id, updateData);
				onUpdate(updated);
			}

			onOpenChange(false);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to update document';
		} finally {
			saving = false;
		}
	}
</script>

<Dialog.Root {open} {onOpenChange}>
	<Dialog.Content class="sm:max-w-md">
		<Dialog.Header>
			<Dialog.Title>Edit Document</Dialog.Title>
			<Dialog.Description>
				Update document metadata. Changes won't affect the file content.
			</Dialog.Description>
		</Dialog.Header>

		<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
			<!-- Filename -->
			<div class="space-y-2">
				<Label for="filename">Filename</Label>
				<Input
					id="filename"
					bind:value={filename}
					placeholder="Enter filename"
					disabled={saving}
				/>
			</div>

			<!-- Description -->
			<div class="space-y-2">
				<Label for="description">Description</Label>
				<Textarea
					id="description"
					bind:value={description}
					placeholder="Add a description for this document..."
					rows={3}
					disabled={saving}
				/>
			</div>

			<!-- Tags -->
			<div class="space-y-2">
				<Label for="tags">Tags</Label>
				<div class="flex gap-2">
					<Input
						id="tags"
						bind:value={tagInput}
						placeholder="Add a tag..."
						onkeydown={handleTagKeydown}
						disabled={saving || tags.length >= 10}
					/>
					<Button
						type="button"
						variant="outline"
						onclick={addTag}
						disabled={saving || !tagInput.trim() || tags.length >= 10}
					>
						Add
					</Button>
				</div>
				{#if tags.length > 0}
					<div class="flex flex-wrap gap-1 mt-2">
						{#each tags as tag}
							<Badge variant="secondary" class="gap-1">
								{tag}
								<button
									type="button"
									onclick={() => removeTag(tag)}
									class="hover:text-destructive"
									disabled={saving}
								>
									<X class="size-3" />
								</button>
							</Badge>
						{/each}
					</div>
				{/if}
				<p class="text-xs text-muted-foreground">
					{tags.length}/10 tags
				</p>
			</div>

			<!-- Error Message -->
			{#if error}
				<p class="text-sm text-destructive">{error}</p>
			{/if}

			<!-- Actions -->
			<Dialog.Footer>
				<Button type="button" variant="outline" onclick={() => onOpenChange(false)} disabled={saving}>
					Cancel
				</Button>
				<Button type="submit" disabled={saving}>
					{#if saving}
						Saving...
					{:else}
						Save Changes
					{/if}
				</Button>
			</Dialog.Footer>
		</form>
	</Dialog.Content>
</Dialog.Root>
