<script lang="ts">
	import { onMount } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import { Card } from '$lib/components/ui/card';
	import { Badge } from '$lib/components/ui/badge';
	import * as Tabs from '$lib/components/ui/tabs';
	import * as Table from '$lib/components/ui/table';
	import * as Select from '$lib/components/ui/select';
	import {
		Activity,
		Zap,
		DollarSign,
		Users,
		Cpu,
		TrendingUp,
		TrendingDown,
		RefreshCw
	} from 'lucide-svelte';
	import {
		getUsageAnalytics,
		type UsageAnalytics,
		type ModelUsage,
		type DailyUsageData,
		type UserSpendData
	} from '$lib/api/admin';

	let analytics = $state<UsageAnalytics | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let selectedPeriod = $state('30');

	const periodOptions = [
		{ value: '7', label: 'Last 7 days' },
		{ value: '14', label: 'Last 14 days' },
		{ value: '30', label: 'Last 30 days' },
		{ value: '60', label: 'Last 60 days' },
		{ value: '90', label: 'Last 90 days' }
	];

	onMount(async () => {
		await loadData();
	});

	async function loadData() {
		try {
			loading = true;
			error = null;
			analytics = await getUsageAnalytics(parseInt(selectedPeriod));
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load analytics';
		} finally {
			loading = false;
		}
	}

	async function handlePeriodChange(value: string | undefined) {
		if (value) {
			selectedPeriod = value;
			await loadData();
		}
	}

	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 2,
			maximumFractionDigits: 4
		}).format(amount);
	}

	function formatNumber(num: number): string {
		return new Intl.NumberFormat('en-US').format(num);
	}

	function formatCompactNumber(num: number): string {
		if (num >= 1000000) {
			return (num / 1000000).toFixed(1) + 'M';
		}
		if (num >= 1000) {
			return (num / 1000).toFixed(1) + 'K';
		}
		return num.toString();
	}

	function formatDate(dateStr: string): string {
		return new Date(dateStr).toLocaleDateString('en-US', {
			month: 'short',
			day: 'numeric'
		});
	}

	// Calculate model distribution for pie chart visualization
	let modelDistribution = $derived(
		analytics?.by_model.map((m) => ({
			...m,
			percentage: analytics?.summary.total_cost
				? (m.cost / analytics.summary.total_cost) * 100
				: 0
		})) ?? []
	);

	// Colors for models
	const modelColors = [
		'bg-blue-500',
		'bg-green-500',
		'bg-yellow-500',
		'bg-purple-500',
		'bg-pink-500',
		'bg-indigo-500',
		'bg-red-500',
		'bg-orange-500'
	];

	// Calculate max values for chart scaling
	let maxDailyCost = $derived(Math.max(...(analytics?.by_date.map((d) => d.cost) ?? [0]), 1));
	let maxDailyTokens = $derived(Math.max(...(analytics?.by_date.map((d) => d.tokens) ?? [0]), 1));
</script>

<svelte:head>
	<title>Usage Analytics | Admin</title>
</svelte:head>

<div class="flex-1 space-y-6 p-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold">Usage Analytics</h1>
			<p class="text-muted-foreground">Monitor usage and costs across all users</p>
		</div>
		<div class="flex items-center gap-4">
			<Select.Root
				type="single"
				value={selectedPeriod}
				onValueChange={handlePeriodChange}
			>
				<Select.Trigger class="w-40">
					{periodOptions.find((p) => p.value === selectedPeriod)?.label ?? 'Select period'}
				</Select.Trigger>
				<Select.Content>
					{#each periodOptions as option}
						<Select.Item value={option.value}>{option.label}</Select.Item>
					{/each}
				</Select.Content>
			</Select.Root>
			<Button variant="outline" onclick={loadData} disabled={loading}>
				<RefreshCw class="mr-2 h-4 w-4 {loading ? 'animate-spin' : ''}" />
				Refresh
			</Button>
		</div>
	</div>

	{#if loading && !analytics}
		<div class="flex items-center justify-center py-12">
			<div class="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent">
			</div>
		</div>
	{:else if error}
		<Card class="p-6">
			<p class="text-destructive">{error}</p>
			<Button onclick={loadData} class="mt-4">Retry</Button>
		</Card>
	{:else if analytics}
		<!-- Summary Cards -->
		<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
			<Card class="p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-muted-foreground">Total Requests</p>
						<p class="text-2xl font-bold">{formatCompactNumber(analytics.summary.total_requests)}</p>
						<p class="text-xs text-muted-foreground">
							{formatNumber(analytics.summary.requests_today)} today
						</p>
					</div>
					<div class="rounded-full bg-blue-100 p-3 dark:bg-blue-900">
						<Activity class="h-6 w-6 text-blue-600 dark:text-blue-400" />
					</div>
				</div>
			</Card>

			<Card class="p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-muted-foreground">Total Tokens</p>
						<p class="text-2xl font-bold">{formatCompactNumber(analytics.summary.total_tokens)}</p>
						<p class="text-xs text-muted-foreground">
							{formatCompactNumber(analytics.summary.tokens_today)} today
						</p>
					</div>
					<div class="rounded-full bg-green-100 p-3 dark:bg-green-900">
						<Zap class="h-6 w-6 text-green-600 dark:text-green-400" />
					</div>
				</div>
			</Card>

			<Card class="p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-muted-foreground">Total Cost</p>
						<p class="text-2xl font-bold">{formatCurrency(analytics.summary.total_cost)}</p>
						<p class="text-xs text-muted-foreground">
							{formatCurrency(analytics.summary.cost_today)} today
						</p>
					</div>
					<div class="rounded-full bg-yellow-100 p-3 dark:bg-yellow-900">
						<DollarSign class="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
					</div>
				</div>
			</Card>

			<Card class="p-6">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-sm text-muted-foreground">Active Users</p>
						<p class="text-2xl font-bold">{analytics.by_user.length}</p>
						<p class="text-xs text-muted-foreground">in last {analytics.summary.period_days} days</p>
					</div>
					<div class="rounded-full bg-purple-100 p-3 dark:bg-purple-900">
						<Users class="h-6 w-6 text-purple-600 dark:text-purple-400" />
					</div>
				</div>
			</Card>
		</div>

		<!-- Charts Row -->
		<div class="grid gap-6 lg:grid-cols-2">
			<!-- Daily Cost Trend -->
			<Card class="p-6">
				<h3 class="mb-4 font-semibold">Daily Cost Trend</h3>
				{#if analytics.by_date.length > 0}
					<div class="h-64">
						<div class="flex h-full flex-col">
							<!-- Y-axis labels -->
							<div class="mb-2 flex justify-between text-xs text-muted-foreground">
								<span>{formatCurrency(maxDailyCost)}</span>
								<span>{formatCurrency(maxDailyCost / 2)}</span>
								<span>$0</span>
							</div>
							<!-- Chart area -->
							<div class="flex flex-1 items-end gap-1">
								{#each analytics.by_date.slice(-30) as day, i}
									{@const height = (day.cost / maxDailyCost) * 100}
									<div
										class="group relative flex-1 cursor-pointer"
										title="{formatDate(day.date)}: {formatCurrency(day.cost)}"
									>
										<div
											class="w-full rounded-t bg-primary/80 transition-colors hover:bg-primary"
											style="height: {Math.max(height, 1)}%"
										></div>
										<!-- Tooltip -->
										<div
											class="absolute bottom-full left-1/2 z-10 mb-2 hidden -translate-x-1/2 whitespace-nowrap rounded bg-popover px-2 py-1 text-xs shadow-lg group-hover:block"
										>
											<p class="font-medium">{formatDate(day.date)}</p>
											<p>Cost: {formatCurrency(day.cost)}</p>
											<p>Requests: {formatNumber(day.requests)}</p>
										</div>
									</div>
								{/each}
							</div>
							<!-- X-axis labels -->
							<div class="mt-2 flex justify-between text-xs text-muted-foreground">
								{#if analytics.by_date.length > 0}
									<span>{formatDate(analytics.by_date[0]?.date ?? '')}</span>
									<span>{formatDate(analytics.by_date[analytics.by_date.length - 1]?.date ?? '')}</span>
								{/if}
							</div>
						</div>
					</div>
				{:else}
					<div class="flex h-64 items-center justify-center text-muted-foreground">
						No data available
					</div>
				{/if}
			</Card>

			<!-- Cost by Model (Pie chart visualization) -->
			<Card class="p-6">
				<h3 class="mb-4 font-semibold">Cost by Model</h3>
				{#if modelDistribution.length > 0}
					<div class="flex gap-6">
						<!-- Pie chart representation -->
						<div class="relative h-48 w-48 flex-shrink-0">
							<svg viewBox="0 0 100 100" class="h-full w-full -rotate-90">
								{#each modelDistribution as model, i}
									{@const offset = modelDistribution.slice(0, i).reduce((sum, m) => sum + m.percentage, 0)}
									<circle
										cx="50"
										cy="50"
										r="40"
										fill="transparent"
										stroke="currentColor"
										stroke-width="20"
										stroke-dasharray="{model.percentage * 2.51} {251 - model.percentage * 2.51}"
										stroke-dashoffset="{-offset * 2.51}"
										class="{modelColors[i % modelColors.length].replace('bg-', 'text-')}"
									/>
								{/each}
							</svg>
							<div class="absolute inset-0 flex flex-col items-center justify-center">
								<p class="text-2xl font-bold">{formatCurrency(analytics.summary.total_cost)}</p>
								<p class="text-xs text-muted-foreground">Total</p>
							</div>
						</div>
						<!-- Legend -->
						<div class="flex-1 space-y-2">
							{#each modelDistribution.slice(0, 6) as model, i}
								<div class="flex items-center justify-between text-sm">
									<div class="flex items-center gap-2">
										<div class="h-3 w-3 rounded-full {modelColors[i % modelColors.length]}"></div>
										<span class="truncate max-w-[120px]" title={model.model}>{model.model}</span>
									</div>
									<div class="text-right">
										<span class="font-medium">{formatCurrency(model.cost)}</span>
										<span class="ml-1 text-muted-foreground">({model.percentage.toFixed(1)}%)</span>
									</div>
								</div>
							{/each}
							{#if modelDistribution.length > 6}
								<p class="text-xs text-muted-foreground">
									+{modelDistribution.length - 6} more models
								</p>
							{/if}
						</div>
					</div>
				{:else}
					<div class="flex h-48 items-center justify-center text-muted-foreground">
						No model data available
					</div>
				{/if}
			</Card>
		</div>

		<!-- Detailed Tables -->
		<Tabs.Root value="users">
			<Tabs.List class="grid w-full grid-cols-3">
				<Tabs.Trigger value="users">By User</Tabs.Trigger>
				<Tabs.Trigger value="models">By Model</Tabs.Trigger>
				<Tabs.Trigger value="daily">Daily Breakdown</Tabs.Trigger>
			</Tabs.List>

			<!-- By User -->
			<Tabs.Content value="users" class="mt-4">
				<Card>
					<Table.Root>
						<Table.Header>
							<Table.Row>
								<Table.Head>User</Table.Head>
								<Table.Head class="text-right">Total Spend</Table.Head>
								<Table.Head class="text-right">Requests</Table.Head>
								<Table.Head class="text-right">Tokens</Table.Head>
								<Table.Head class="text-right">Avg per Request</Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#if analytics.by_user.length === 0}
								<Table.Row>
									<Table.Cell colspan={5} class="text-center text-muted-foreground">
										No user data available
									</Table.Cell>
								</Table.Row>
							{:else}
								{#each analytics.by_user.slice(0, 20) as user}
									{@const avgPerRequest = (user.total_requests ?? 0) > 0
										? user.total_spend / (user.total_requests ?? 1)
										: 0}
									<Table.Row>
										<Table.Cell class="font-medium">
											{user.user_email || user.user_id || 'Unknown'}
										</Table.Cell>
										<Table.Cell class="text-right">
											{formatCurrency(user.total_spend)}
										</Table.Cell>
										<Table.Cell class="text-right">
											{formatNumber(user.total_requests ?? 0)}
										</Table.Cell>
										<Table.Cell class="text-right">
											{formatCompactNumber(user.total_tokens ?? 0)}
										</Table.Cell>
										<Table.Cell class="text-right">
											{formatCurrency(avgPerRequest)}
										</Table.Cell>
									</Table.Row>
								{/each}
							{/if}
						</Table.Body>
					</Table.Root>
				</Card>
			</Tabs.Content>

			<!-- By Model -->
			<Tabs.Content value="models" class="mt-4">
				<Card>
					<Table.Root>
						<Table.Header>
							<Table.Row>
								<Table.Head>Model</Table.Head>
								<Table.Head class="text-right">Requests</Table.Head>
								<Table.Head class="text-right">Prompt Tokens</Table.Head>
								<Table.Head class="text-right">Completion Tokens</Table.Head>
								<Table.Head class="text-right">Total Tokens</Table.Head>
								<Table.Head class="text-right">Cost</Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#if analytics.by_model.length === 0}
								<Table.Row>
									<Table.Cell colspan={6} class="text-center text-muted-foreground">
										No model data available
									</Table.Cell>
								</Table.Row>
							{:else}
								{#each analytics.by_model as model}
									<Table.Row>
										<Table.Cell class="font-medium">
											<div class="flex items-center gap-2">
												<Cpu class="h-4 w-4 text-muted-foreground" />
												{model.model}
											</div>
										</Table.Cell>
										<Table.Cell class="text-right">
											{formatNumber(model.requests)}
										</Table.Cell>
										<Table.Cell class="text-right">
											{formatCompactNumber(model.prompt_tokens)}
										</Table.Cell>
										<Table.Cell class="text-right">
											{formatCompactNumber(model.completion_tokens)}
										</Table.Cell>
										<Table.Cell class="text-right">
											{formatCompactNumber(model.total_tokens)}
										</Table.Cell>
										<Table.Cell class="text-right font-medium">
											{formatCurrency(model.cost)}
										</Table.Cell>
									</Table.Row>
								{/each}
							{/if}
						</Table.Body>
					</Table.Root>
				</Card>
			</Tabs.Content>

			<!-- Daily Breakdown -->
			<Tabs.Content value="daily" class="mt-4">
				<Card>
					<Table.Root>
						<Table.Header>
							<Table.Row>
								<Table.Head>Date</Table.Head>
								<Table.Head class="text-right">Requests</Table.Head>
								<Table.Head class="text-right">Tokens</Table.Head>
								<Table.Head class="text-right">Cost</Table.Head>
								<Table.Head class="text-right">Trend</Table.Head>
							</Table.Row>
						</Table.Header>
						<Table.Body>
							{#if analytics.by_date.length === 0}
								<Table.Row>
									<Table.Cell colspan={5} class="text-center text-muted-foreground">
										No daily data available
									</Table.Cell>
								</Table.Row>
							{:else}
								{#each analytics.by_date.slice().reverse().slice(0, 30) as day, i}
									{@const prevDay = analytics.by_date.slice().reverse()[i + 1]}
									{@const trend = prevDay ? day.cost - prevDay.cost : 0}
									<Table.Row>
										<Table.Cell class="font-medium">
											{new Date(day.date).toLocaleDateString('en-US', {
												weekday: 'short',
												month: 'short',
												day: 'numeric'
											})}
										</Table.Cell>
										<Table.Cell class="text-right">
											{formatNumber(day.requests)}
										</Table.Cell>
										<Table.Cell class="text-right">
											{formatCompactNumber(day.tokens)}
										</Table.Cell>
										<Table.Cell class="text-right font-medium">
											{formatCurrency(day.cost)}
										</Table.Cell>
										<Table.Cell class="text-right">
											{#if trend > 0}
												<span class="flex items-center justify-end text-red-500">
													<TrendingUp class="mr-1 h-4 w-4" />
													+{formatCurrency(trend)}
												</span>
											{:else if trend < 0}
												<span class="flex items-center justify-end text-green-500">
													<TrendingDown class="mr-1 h-4 w-4" />
													{formatCurrency(trend)}
												</span>
											{:else}
												<span class="text-muted-foreground">-</span>
											{/if}
										</Table.Cell>
									</Table.Row>
								{/each}
							{/if}
						</Table.Body>
					</Table.Root>
				</Card>
			</Tabs.Content>
		</Tabs.Root>
	{/if}
</div>
