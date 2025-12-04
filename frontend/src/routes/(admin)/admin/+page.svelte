<script lang="ts">
	import { onMount } from 'svelte';
	import * as Card from '$lib/components/ui/card';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import { getDashboardStats, type DashboardStats } from '$lib/api/admin';
	import { Users, Activity, DollarSign, TrendingUp, Loader2 } from 'lucide-svelte';
	import PieChart from '$lib/components/charts/PieChart.svelte';
	import LineChart from '$lib/components/charts/LineChart.svelte';

	let stats = $state<DashboardStats | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	onMount(async () => {
		try {
			stats = await getDashboardStats();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load dashboard stats';
		} finally {
			loading = false;
		}
	});

	function formatNumber(num: number): string {
		if (num >= 1000000) {
			return (num / 1000000).toFixed(1) + 'M';
		}
		if (num >= 1000) {
			return (num / 1000).toFixed(1) + 'K';
		}
		return num.toString();
	}

	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(amount);
	}

	function formatCurrencyDecimal(amount: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 2,
			maximumFractionDigits: 4
		}).format(amount);
	}
</script>

<svelte:head>
	<title>Admin Dashboard - RAG Agent Platform</title>
</svelte:head>

<div class="p-6 space-y-6">
	<div>
		<h1 class="text-3xl font-bold">Dashboard</h1>
		<p class="text-muted-foreground mt-1">Overview of your platform metrics</p>
	</div>

	{#if loading}
		<!-- Loading skeletons -->
		<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
			{#each Array(4) as _}
				<Card.Root>
					<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
						<Skeleton class="h-4 w-24" />
						<Skeleton class="h-4 w-4 rounded" />
					</Card.Header>
					<Card.Content>
						<Skeleton class="h-8 w-20 mb-1" />
						<Skeleton class="h-3 w-32" />
					</Card.Content>
				</Card.Root>
			{/each}
		</div>
	{:else if error}
		<Card.Root class="border-destructive">
			<Card.Content class="pt-6">
				<p class="text-destructive">{error}</p>
			</Card.Content>
		</Card.Root>
	{:else if stats}
		<!-- Metric Cards -->
		<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
			<!-- Total Users -->
			<Card.Root>
				<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
					<Card.Title class="text-sm font-medium">Total Users</Card.Title>
					<Users class="h-4 w-4 text-muted-foreground" />
				</Card.Header>
				<Card.Content>
					<div class="text-2xl font-bold">{formatNumber(stats.users.total_users)}</div>
					<p class="text-xs text-muted-foreground">
						+{stats.users.new_this_month} this month
					</p>
				</Card.Content>
			</Card.Root>

			<!-- Active Today -->
			<Card.Root>
				<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
					<Card.Title class="text-sm font-medium">Active Today</Card.Title>
					<Activity class="h-4 w-4 text-muted-foreground" />
				</Card.Header>
				<Card.Content>
					<div class="text-2xl font-bold">{formatNumber(stats.users.active_today)}</div>
					<p class="text-xs text-muted-foreground">
						{stats.usage.requests_today} requests today
					</p>
				</Card.Content>
			</Card.Root>

			<!-- Monthly Revenue (MRR) -->
			<Card.Root>
				<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
					<Card.Title class="text-sm font-medium">MRR</Card.Title>
					<DollarSign class="h-4 w-4 text-muted-foreground" />
				</Card.Header>
				<Card.Content>
					<div class="text-2xl font-bold">{formatCurrency(stats.revenue.mrr)}</div>
					<p class="text-xs text-muted-foreground">
						ARR: {formatCurrency(stats.revenue.arr)}
					</p>
				</Card.Content>
			</Card.Root>

			<!-- API Cost -->
			<Card.Root>
				<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
					<Card.Title class="text-sm font-medium">API Cost (Month)</Card.Title>
					<TrendingUp class="h-4 w-4 text-muted-foreground" />
				</Card.Header>
				<Card.Content>
					<div class="text-2xl font-bold">{formatCurrencyDecimal(stats.usage.cost_this_month)}</div>
					<p class="text-xs text-muted-foreground">
						{formatNumber(stats.usage.tokens_this_month)} tokens
					</p>
				</Card.Content>
			</Card.Root>
		</div>

		<!-- Charts Row -->
		<div class="grid gap-4 md:grid-cols-2">
			<!-- Subscribers by Plan -->
			<Card.Root>
				<Card.Header>
					<Card.Title>Subscribers by Plan</Card.Title>
					<Card.Description>Distribution of subscribers across plans</Card.Description>
				</Card.Header>
				<Card.Content>
					{#if stats.subscribers_by_plan.length === 0}
						<div class="flex items-center justify-center h-64 text-muted-foreground">
							No subscribers yet
						</div>
					{:else}
						<PieChart
							data={stats.subscribers_by_plan.map((p) => ({
								label: p.display_name,
								value: p.subscriber_count
							}))}
						/>
					{/if}
				</Card.Content>
			</Card.Root>

			<!-- Usage Over Time -->
			<Card.Root>
				<Card.Header>
					<Card.Title>Usage Over Time</Card.Title>
					<Card.Description>Daily requests over the last 30 days</Card.Description>
				</Card.Header>
				<Card.Content>
					{#if stats.usage_over_time.length === 0}
						<div class="flex items-center justify-center h-64 text-muted-foreground">
							No usage data yet
						</div>
					{:else}
						<LineChart
							data={stats.usage_over_time.map((d) => ({
								date: d.date,
								value: d.requests
							}))}
							label="Requests"
						/>
					{/if}
				</Card.Content>
			</Card.Root>
		</div>

		<!-- Additional Stats -->
		<div class="grid gap-4 md:grid-cols-3">
			<!-- Today's Usage -->
			<Card.Root>
				<Card.Header>
					<Card.Title class="text-sm font-medium">Today's Usage</Card.Title>
				</Card.Header>
				<Card.Content class="space-y-2">
					<div class="flex justify-between">
						<span class="text-muted-foreground">Requests</span>
						<span class="font-medium">{formatNumber(stats.usage.requests_today)}</span>
					</div>
					<div class="flex justify-between">
						<span class="text-muted-foreground">Tokens</span>
						<span class="font-medium">{formatNumber(stats.usage.tokens_today)}</span>
					</div>
					<div class="flex justify-between">
						<span class="text-muted-foreground">Cost</span>
						<span class="font-medium">{formatCurrencyDecimal(stats.usage.cost_today)}</span>
					</div>
				</Card.Content>
			</Card.Root>

			<!-- Monthly Usage -->
			<Card.Root>
				<Card.Header>
					<Card.Title class="text-sm font-medium">This Month</Card.Title>
				</Card.Header>
				<Card.Content class="space-y-2">
					<div class="flex justify-between">
						<span class="text-muted-foreground">Requests</span>
						<span class="font-medium">{formatNumber(stats.usage.requests_this_month)}</span>
					</div>
					<div class="flex justify-between">
						<span class="text-muted-foreground">Tokens</span>
						<span class="font-medium">{formatNumber(stats.usage.tokens_this_month)}</span>
					</div>
					<div class="flex justify-between">
						<span class="text-muted-foreground">Cost</span>
						<span class="font-medium">{formatCurrencyDecimal(stats.usage.cost_this_month)}</span>
					</div>
				</Card.Content>
			</Card.Root>

			<!-- User Growth -->
			<Card.Root>
				<Card.Header>
					<Card.Title class="text-sm font-medium">User Growth</Card.Title>
				</Card.Header>
				<Card.Content class="space-y-2">
					<div class="flex justify-between">
						<span class="text-muted-foreground">Total Users</span>
						<span class="font-medium">{stats.users.total_users}</span>
					</div>
					<div class="flex justify-between">
						<span class="text-muted-foreground">New This Week</span>
						<span class="font-medium text-green-600">+{stats.users.new_this_week}</span>
					</div>
					<div class="flex justify-between">
						<span class="text-muted-foreground">New This Month</span>
						<span class="font-medium text-green-600">+{stats.users.new_this_month}</span>
					</div>
				</Card.Content>
			</Card.Root>
		</div>
	{/if}
</div>
