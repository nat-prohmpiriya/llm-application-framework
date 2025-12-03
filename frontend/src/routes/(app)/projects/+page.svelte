<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { Plus, Search, ChevronDown, FolderKanban } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { projectsApi, type ProjectDetail, type ProjectCreate, type ProjectUpdate } from '$lib/api';
	import ProjectDialog from '$lib/components/projects/ProjectDialog.svelte';

	let projects = $state<ProjectDetail[]>([]);
	let loading = $state(true);
	let searchQuery = $state('');
	let showCreateDialog = $state(false);
	let sortBy = $state<'activity' | 'name' | 'created'>('activity');

	let filteredProjects = $derived.by(() => {
		let result = searchQuery
			? projects.filter(
					(p) =>
						p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
						(p.description?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false)
				)
			: projects;

		// Sort based on selected option
		return result.toSorted((a, b) => {
			switch (sortBy) {
				case 'name':
					return a.name.localeCompare(b.name);
				case 'created':
					return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
				case 'activity':
				default:
					return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
			}
		});
	});

	onMount(async () => {
		await loadProjects();
	});

	async function loadProjects() {
		try {
			const response = await projectsApi.list(1, 100);
			// Get detail for each project to get counts
			const projectDetails = await Promise.all(
				response.items.map((p) => projectsApi.get(p.id))
			);
			projects = projectDetails;
		} catch (e) {
			console.error('Failed to load projects:', e);
		} finally {
			loading = false;
		}
	}

	async function handleCreate(data: ProjectCreate | ProjectUpdate) {
		try {
			const newProject = await projectsApi.create(data as ProjectCreate);
			// Get project detail with counts
			const projectDetail = await projectsApi.get(newProject.id);
			projects = [projectDetail, ...projects];
			showCreateDialog = false;
		} catch (e) {
			console.error('Failed to create project:', e);
		}
	}

	async function handleDelete(id: string, event: MouseEvent) {
		event.stopPropagation();
		try {
			await projectsApi.delete(id);
			projects = projects.filter((p) => p.id !== id);
		} catch (e) {
			console.error('Failed to delete project:', e);
		}
	}

	function handleClick(id: string) {
		goto(`/projects/${id}`);
	}

	function formatDate(dateString: string): string {
		const date = new Date(dateString);
		const now = new Date();
		const diff = now.getTime() - date.getTime();
		const days = Math.floor(diff / (1000 * 60 * 60 * 24));
		const months = Math.floor(days / 30);

		if (days === 0) return 'Updated today';
		if (days === 1) return 'Updated yesterday';
		if (days < 7) return `Updated ${days} days ago`;
		if (months === 1) return 'Updated 1 month ago';
		if (months < 12) return `Updated ${months} months ago`;
		return `Updated ${date.toLocaleDateString()}`;
	}

	const sortLabels = {
		activity: 'Activity',
		name: 'Name',
		created: 'Created'
	};
</script>

<svelte:head>
	<title>Projects | RAG Agent</title>
</svelte:head>

<div class="flex h-full flex-col">
	<!-- Content -->
	<div class="flex-1 overflow-auto p-8">
		<div class="mx-auto max-w-6xl">
			<!-- Header -->
			<div class="flex items-center justify-between mb-6">
				<div class="flex items-center gap-3">
					<FolderKanban class="size-8 text-foreground" />
					<h1 class="text-3xl font-semibold text-foreground">Projects</h1>
				</div>
				<Button onclick={() => (showCreateDialog = true)}>
					<Plus class="mr-2 size-4" />
					New project
				</Button>
			</div>

			<!-- Search -->
			<div class="relative mb-6">
				<Search
					class="absolute left-4 top-1/2 size-5 -translate-y-1/2 text-muted-foreground"
				/>
				<Input
					type="search"
					placeholder="Search projects..."
					class="pl-12 h-12 bg-white border-border rounded-lg text-base"
					bind:value={searchQuery}
				/>
			</div>

			<!-- Sort -->
			<div class="flex justify-end mb-4">
				<div class="flex items-center gap-2 text-sm text-muted-foreground">
					<span>Sort by</span>
					<DropdownMenu.Root>
						<DropdownMenu.Trigger>
							{#snippet child({ props })}
								<Button {...props} variant="ghost" size="sm" class="gap-1 px-2">
									{sortLabels[sortBy]}
									<ChevronDown class="size-4" />
								</Button>
							{/snippet}
						</DropdownMenu.Trigger>
						<DropdownMenu.Content align="end">
							<DropdownMenu.Item onclick={() => (sortBy = 'activity')}
								>Activity</DropdownMenu.Item
							>
							<DropdownMenu.Item onclick={() => (sortBy = 'name')}
								>Name</DropdownMenu.Item
							>
							<DropdownMenu.Item onclick={() => (sortBy = 'created')}
								>Created</DropdownMenu.Item
							>
						</DropdownMenu.Content>
					</DropdownMenu.Root>
				</div>
			</div>

			{#if loading}
				<div class="flex items-center justify-center py-12">
					<div
						class="size-8 animate-spin rounded-full border-4 border-muted border-t-primary"
					></div>
				</div>
			{:else if filteredProjects.length === 0}
				<div
					class="rounded-lg bg-white border border-border flex flex-col items-center p-12"
				>
					<h3 class="text-lg font-medium">No projects</h3>
					<p class="mt-1 text-sm text-muted-foreground">
						{#if searchQuery}
							No projects matching "{searchQuery}". Try a different search.
						{:else}
							Create your first project to organize documents and conversations.
						{/if}
					</p>
					<Button class="mt-4" onclick={() => (showCreateDialog = true)}>
						<Plus class="mr-2 size-4" />
						Create Project
					</Button>
				</div>
			{:else}
				<!-- Grid of project cards -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					{#each filteredProjects as project (project.id)}
						<button
							class="bg-white rounded-xl border border-border p-6 text-left hover:shadow-md transition-shadow flex flex-col min-h-[180px] cursor-pointer"
							onclick={() => handleClick(project.id)}
						>
							<div class="flex items-start gap-2 mb-2">
								<h3 class="font-semibold text-lg text-foreground">
									{project.name}
								</h3>
							</div>
							{#if project.description}
								<p class="text-muted-foreground text-sm flex-1 line-clamp-3">
									{project.description}
								</p>
							{:else}
								<div class="flex-1"></div>
							{/if}
							<p class="text-sm text-muted-foreground mt-4">
								{formatDate(project.updated_at)}
							</p>
						</button>
					{/each}
				</div>
			{/if}
		</div>
	</div>
</div>

<!-- Create Project Dialog -->
<ProjectDialog bind:open={showCreateDialog} project={null} onSave={handleCreate} />
