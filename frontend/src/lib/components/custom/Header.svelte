<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import * as Avatar from '$lib/components/ui/avatar';
	import type { Snippet } from 'svelte';

	let { user, onLogout, sidebarTrigger } = $props<{
		user?: { name: string; email: string; avatar?: string } | null;
		onLogout?: () => void;
		sidebarTrigger?: Snippet;
	}>();
</script>

<header class="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
	<div class="flex h-14 items-center px-4">
		<!-- Sidebar trigger (mobile) -->
		{#if sidebarTrigger}
			<div class="mr-2 md:hidden">
				{@render sidebarTrigger()}
			</div>
		{/if}

		<!-- Logo -->
		<div class="flex items-center gap-2">
			<svg class="h-6 w-6 text-primary" viewBox="0 0 24 24" fill="currentColor">
				<path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" fill="none"/>
			</svg>
			<span class="font-semibold hidden sm:inline-block">RAG Agent Platform</span>
		</div>

		<!-- Spacer -->
		<div class="flex-1"></div>

		<!-- User menu -->
		{#if user}
			<DropdownMenu.Root>
				<DropdownMenu.Trigger>
					{#snippet child({ props })}
						<button {...props} class="relative h-8 w-8 rounded-full">
							<Avatar.Root class="h-8 w-8">
								{#if user.avatar}
									<Avatar.Image src={user.avatar} alt={user.name} />
								{/if}
								<Avatar.Fallback>{user.name.slice(0, 2).toUpperCase()}</Avatar.Fallback>
							</Avatar.Root>
						</button>
					{/snippet}
				</DropdownMenu.Trigger>
				<DropdownMenu.Content class="w-56" align="end">
					<DropdownMenu.Label class="font-normal">
						<div class="flex flex-col space-y-1">
							<p class="text-sm font-medium leading-none">{user.name}</p>
							<p class="text-xs leading-none text-muted-foreground">{user.email}</p>
						</div>
					</DropdownMenu.Label>
					<DropdownMenu.Separator />
					<DropdownMenu.Item>Profile</DropdownMenu.Item>
					<DropdownMenu.Item>Settings</DropdownMenu.Item>
					<DropdownMenu.Separator />
					<DropdownMenu.Item onclick={onLogout}>
						Log out
					</DropdownMenu.Item>
				</DropdownMenu.Content>
			</DropdownMenu.Root>
		{:else}
			<div class="flex items-center gap-2">
				<Button variant="ghost" href="/login">Login</Button>
				<Button href="/register">Register</Button>
			</div>
		{/if}
	</div>
</header>
