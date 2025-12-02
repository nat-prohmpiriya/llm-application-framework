<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { ScrollArea } from '$lib/components/ui/scroll-area';
	import { Separator } from '$lib/components/ui/separator';

	let { currentProject, projects, onProjectSelect, onNewProject } = $props<{
		currentProject?: { id: string; name: string } | null;
		projects?: { id: string; name: string }[];
		onProjectSelect?: (projectId: string) => void;
		onNewProject?: () => void;
	}>();

	interface NavItem {
		label: string;
		href: string;
		icon: string;
	}

	const navItems: NavItem[] = [
		{ label: 'Chat', href: '/chat', icon: 'chat' },
		{ label: 'Documents', href: '/documents', icon: 'document' },
		{ label: 'Agents', href: '/agents', icon: 'agent' },
		{ label: 'SQL Query', href: '/sql', icon: 'database' },
		{ label: 'Fine-tuning', href: '/finetune', icon: 'tune' },
		{ label: 'Settings', href: '/settings', icon: 'settings' },
	];

	function getIcon(icon: string): string {
		const icons: Record<string, string> = {
			chat: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z',
			document: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
			agent: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z',
			database: 'M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4',
			tune: 'M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4',
			settings: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
		};
		return icons[icon] || icons.chat;
	}
</script>

<aside class="flex h-full w-64 flex-col border-r bg-background">
	<!-- Project selector -->
	<div class="p-4">
		<div class="flex items-center justify-between mb-2">
			<span class="text-sm font-medium text-muted-foreground">Projects</span>
			<Button variant="ghost" size="sm" onclick={onNewProject}>
				<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M12 5v14M5 12h14" />
				</svg>
			</Button>
		</div>
		{#if currentProject}
			<Button variant="outline" class="w-full justify-start">
				<svg class="mr-2 h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
				</svg>
				{currentProject.name}
			</Button>
		{:else}
			<Button variant="outline" class="w-full justify-start text-muted-foreground">
				Select a project...
			</Button>
		{/if}
	</div>

	<Separator />

	<!-- Navigation -->
	<ScrollArea class="flex-1 px-3 py-4">
		<nav class="flex flex-col gap-1">
			{#each navItems as item}
				<a
					href={item.href}
					class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors hover:bg-accent hover:text-accent-foreground"
				>
					<svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d={getIcon(item.icon)} />
					</svg>
					{item.label}
				</a>
			{/each}
		</nav>
	</ScrollArea>

	<!-- Footer -->
	<div class="border-t p-4">
		<p class="text-xs text-muted-foreground text-center">
			RAG Agent Platform v1.0
		</p>
	</div>
</aside>
