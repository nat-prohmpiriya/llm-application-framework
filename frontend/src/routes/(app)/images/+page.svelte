<script lang="ts">
	import { Image } from 'lucide-svelte';

	let images = $state<any[]>([]);
	let loading = $state(false);
</script>

<svelte:head>
	<title>Images | RAG Agent</title>
</svelte:head>

<div class="flex h-full flex-col">
	<!-- Content -->
	<div class="flex-1 overflow-auto p-8">
		<div class="mx-auto max-w-6xl">
			<!-- Header -->
			<div class="flex items-center justify-between mb-6">
				<div class="flex items-center gap-3">
					<Image class="size-8 text-foreground" />
					<h1 class="text-3xl font-semibold text-foreground">Images</h1>
				</div>
				{#if images.length > 0}
					<span class="text-sm text-muted-foreground">{images.length} images</span>
				{/if}
			</div>

			{#if loading}
				<div class="flex items-center justify-center py-12">
					<div
						class="size-8 animate-spin rounded-full border-4 border-muted border-t-primary"
					></div>
				</div>
			{:else if images.length === 0}
				<div class="rounded-lg bg-white border border-border flex flex-col items-center p-12">
					<Image class="size-12 text-muted-foreground/50" />
					<h3 class="mt-4 text-lg font-medium">No images yet</h3>
					<p class="mt-1 text-sm text-muted-foreground text-center">
						Image generation and management coming soon.
					</p>
				</div>
			{:else}
				<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
					{#each images as image (image.id)}
						<div class="aspect-square rounded-lg border overflow-hidden">
							<img
								src={image.url}
								alt={image.title}
								class="w-full h-full object-cover"
							/>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>
