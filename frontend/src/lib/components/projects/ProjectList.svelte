<script lang="ts">
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import { ScrollArea } from '$lib/components/ui/scroll-area';
	import { FolderOpen, Plus, FileText } from 'lucide-svelte';
	import type { Project } from '$lib/api';

	let {
		projects = [],
		currentProjectId = null,
		loading = false,
		onSelect,
		onCreate
	} = $props<{
		projects: Project[];
		currentProjectId: string | null;
		loading?: boolean;
		onSelect: (id: string | null) => void;
		onCreate: () => void;
	}>();

	let isAllSelected = $derived(currentProjectId === null);

	function handleProjectClick(project: Project) {
		onSelect(project.id);
		goto(`/projects/${project.id}`);
	}
</script>

<div class="flex flex-col gap-2">
	<!-- Header with title and add button -->
	<div class="flex items-center justify-between px-1">
		<span class="text-sm font-medium text-muted-foreground">Projects</span>
		<button
			type="button"
			class="flex h-6 w-6 cursor-pointer items-center justify-center rounded-md hover:bg-accent hover:text-accent-foreground"
			onclick={onCreate}
			disabled={loading}
		>
			<Plus class="h-4 w-4" />
		</button>
	</div>

	<!-- All Documents option -->
	<Button
		variant={isAllSelected ? 'secondary' : 'ghost'}
		class="w-full justify-start gap-2"
		onclick={() => onSelect(null)}
		disabled={loading}
	>
		<FileText class="h-4 w-4" />
		<span class="truncate">All Documents</span>
	</Button>

	<!-- Project list -->
	{#if projects.length > 0}
		<ScrollArea class="max-h-48">
			<div class="flex flex-col gap-1">
				{#each projects as project (project.id)}
					{@const isSelected = currentProjectId === project.id}
					<button
						type="button"
						class="flex w-full cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground {isSelected ? 'bg-secondary text-secondary-foreground' : ''}"
						onclick={() => handleProjectClick(project)}
						disabled={loading}
					>
						<FolderOpen class="h-4 w-4 shrink-0" />
						<span class="truncate">{project.name}</span>
					</button>
				{/each}
			</div>
		</ScrollArea>
	{:else if !loading}
		<p class="px-2 py-1 text-xs text-muted-foreground">No projects yet</p>
	{/if}

	{#if loading}
		<p class="px-2 py-1 text-xs text-muted-foreground">Loading...</p>
	{/if}
</div>
