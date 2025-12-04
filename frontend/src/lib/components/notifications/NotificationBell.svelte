<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { Bell, Check, ExternalLink, Loader2 } from 'lucide-svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Popover from '$lib/components/ui/popover';
	import { Separator } from '$lib/components/ui/separator';
	import { ScrollArea } from '$lib/components/ui/scroll-area';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import { notificationStore } from '$lib/stores';
	import NotificationItem from './NotificationItem.svelte';

	let {
		maxItems = 5,
		class: className = ''
	}: {
		maxItems?: number;
		class?: string;
	} = $props();

	let open = $state(false);
	let markingAllRead = $state(false);

	// Derived state from store
	const notifications = $derived(notificationStore.notifications.slice(0, maxItems));
	const unreadCount = $derived(notificationStore.unreadCount);
	const loading = $derived(notificationStore.loading);
	const hasUnread = $derived(notificationStore.hasUnread);

	onMount(() => {
		notificationStore.startPolling();
	});

	onDestroy(() => {
		notificationStore.stopPolling();
	});

	async function handleOpen(isOpen: boolean) {
		open = isOpen;
		if (isOpen && notifications.length === 0) {
			await notificationStore.fetchNotifications({ per_page: maxItems });
		}
	}

	async function handleMarkAsRead(id: string) {
		await notificationStore.markAsRead(id);
	}

	async function handleMarkAllAsRead() {
		markingAllRead = true;
		await notificationStore.markAllAsRead();
		markingAllRead = false;
	}

	async function handleDelete(id: string) {
		await notificationStore.deleteNotification(id);
	}
</script>

<Popover.Root bind:open onOpenChange={handleOpen}>
	<Popover.Trigger>
		{#snippet child({ props })}
			<Button
				variant="ghost"
				size="icon"
				class="relative {className}"
				aria-label="Notifications"
				{...props}
			>
				<Bell class="size-5" />
				{#if hasUnread}
					<span
						class="absolute -top-0.5 -right-0.5 flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold text-white bg-red-500 rounded-full"
					>
						{unreadCount > 99 ? '99+' : unreadCount}
					</span>
				{/if}
			</Button>
		{/snippet}
	</Popover.Trigger>

	<Popover.Content class="w-80 p-0" align="end">
		<div class="flex items-center justify-between px-4 py-3 border-b">
			<h4 class="font-semibold text-sm">Notifications</h4>
			{#if hasUnread}
				<Button
					variant="ghost"
					size="sm"
					class="h-7 text-xs"
					onclick={handleMarkAllAsRead}
					disabled={markingAllRead}
				>
					{#if markingAllRead}
						<Loader2 class="size-3 animate-spin mr-1" />
					{:else}
						<Check class="size-3 mr-1" />
					{/if}
					Mark all read
				</Button>
			{/if}
		</div>

		<ScrollArea class="max-h-[350px]">
			{#if loading && notifications.length === 0}
				<div class="p-4 space-y-3">
					{#each { length: 3 } as _}
						<div class="flex items-start gap-3">
							<Skeleton class="size-4 rounded" />
							<div class="flex-1 space-y-2">
								<Skeleton class="h-4 w-3/4" />
								<Skeleton class="h-3 w-full" />
							</div>
						</div>
					{/each}
				</div>
			{:else if notifications.length === 0}
				<div class="flex flex-col items-center justify-center py-8 px-4 text-center">
					<Bell class="size-10 text-muted-foreground/50 mb-3" />
					<p class="text-sm font-medium text-muted-foreground">No notifications</p>
					<p class="text-xs text-muted-foreground/70 mt-1">You're all caught up!</p>
				</div>
			{:else}
				<div class="divide-y">
					{#each notifications as notification (notification.id)}
						<NotificationItem
							{notification}
							onMarkAsRead={handleMarkAsRead}
							onDelete={handleDelete}
						/>
					{/each}
				</div>
			{/if}
		</ScrollArea>

		<Separator />

		<div class="p-2">
			<Button variant="ghost" size="sm" class="w-full justify-center text-xs" href="/notifications">
				View all notifications
				<ExternalLink class="size-3 ml-1" />
			</Button>
		</div>
	</Popover.Content>
</Popover.Root>
