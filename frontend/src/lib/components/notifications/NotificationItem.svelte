<script lang="ts">
	import { cn } from '$lib/utils';
	import type { Notification } from '$lib/api';
	import {
		CreditCard,
		FileText,
		Settings,
		User,
		AlertTriangle,
		CheckCircle,
		Info,
		AlertCircle
	} from 'lucide-svelte';

	let {
		notification,
		onMarkAsRead,
		onDelete
	}: {
		notification: Notification;
		onMarkAsRead?: (id: string) => void;
		onDelete?: (id: string) => void;
	} = $props();

	// Format relative time
	function formatRelativeTime(dateString: string): string {
		const date = new Date(dateString);
		const now = new Date();
		const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

		if (diffInSeconds < 60) return 'just now';
		if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
		if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
		if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;

		return date.toLocaleDateString();
	}

	// Get category icon component
	function getCategoryIcon(category: string) {
		switch (category) {
			case 'billing':
				return CreditCard;
			case 'document':
				return FileText;
			case 'system':
				return Settings;
			case 'account':
				return User;
			default:
				return Info;
		}
	}

	// Get priority styles
	function getPriorityStyles(priority: string) {
		switch (priority) {
			case 'critical':
				return 'border-l-red-500';
			case 'high':
				return 'border-l-orange-500';
			case 'medium':
				return 'border-l-yellow-500';
			default:
				return 'border-l-blue-500';
		}
	}

	// Get priority icon
	function getPriorityIcon(priority: string) {
		switch (priority) {
			case 'critical':
				return AlertCircle;
			case 'high':
				return AlertTriangle;
			case 'medium':
				return Info;
			default:
				return CheckCircle;
		}
	}

	const CategoryIcon = $derived(getCategoryIcon(notification.category));
	const PriorityIcon = $derived(getPriorityIcon(notification.priority));
	const isRead = $derived(!!notification.read_at);
	const relativeTime = $derived(formatRelativeTime(notification.created_at));

	function handleClick() {
		if (!isRead && onMarkAsRead) {
			onMarkAsRead(notification.id);
		}
		if (notification.action_url) {
			window.location.href = notification.action_url;
		}
	}
</script>

<button
	type="button"
	onclick={handleClick}
	class={cn(
		'w-full text-left px-4 py-3 border-l-4 transition-colors',
		'hover:bg-accent/50 focus:outline-none focus:bg-accent/50',
		getPriorityStyles(notification.priority),
		isRead ? 'bg-background opacity-70' : 'bg-accent/20'
	)}
>
	<div class="flex items-start gap-3">
		<div class="flex-shrink-0 mt-0.5">
			<CategoryIcon class="size-4 text-muted-foreground" />
		</div>
		<div class="flex-1 min-w-0">
			<div class="flex items-center justify-between gap-2">
				<p class={cn('text-sm font-medium truncate', !isRead && 'text-foreground')}>
					{notification.title}
				</p>
				<span class="text-xs text-muted-foreground whitespace-nowrap">{relativeTime}</span>
			</div>
			<p class="text-sm text-muted-foreground line-clamp-2 mt-0.5">
				{notification.message}
			</p>
		</div>
		{#if !isRead}
			<div class="flex-shrink-0">
				<span class="size-2 rounded-full bg-primary block"></span>
			</div>
		{/if}
	</div>
</button>
