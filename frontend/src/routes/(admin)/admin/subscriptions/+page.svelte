<script lang="ts">
	import { onMount } from 'svelte';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { Input } from '$lib/components/ui/input';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import * as Select from '$lib/components/ui/select';
	import * as AlertDialog from '$lib/components/ui/alert-dialog';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import * as Table from '$lib/components/ui/table';
	import {
		getSubscriptions,
		getPlans,
		upgradeSubscription,
		downgradeSubscription,
		cancelSubscription,
		reactivateSubscription,
		type Subscription,
		type Plan
	} from '$lib/api/admin';
	import {
		Search,
		MoreHorizontal,
		ArrowUpCircle,
		ArrowDownCircle,
		XCircle,
		RefreshCw,
		ChevronLeft,
		ChevronRight,
		CreditCard,
		Calendar,
		DollarSign
	} from 'lucide-svelte';
	import { toast } from 'svelte-sonner';

	let subscriptions = $state<Subscription[]>([]);
	let plans = $state<Plan[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Pagination
	let page = $state(1);
	let perPage = $state(20);
	let totalSubscriptions = $state(0);
	let totalPages = $state(0);

	// Filters
	let statusFilter = $state('all');
	let planFilter = $state('all');
	let searchTimeout: ReturnType<typeof setTimeout>;

	// Action dialogs
	let actionSubscription = $state<Subscription | null>(null);
	let actionType = $state<'upgrade' | 'downgrade' | 'cancel' | 'reactivate' | null>(null);
	let selectedPlanId = $state('');
	let cancelReason = $state('');
	let actionLoading = $state(false);

	// Stats
	let stats = $derived({
		total: totalSubscriptions,
		active: subscriptions.filter((s) => s.status === 'active').length,
		trialing: subscriptions.filter((s) => s.status === 'trialing').length,
		canceled: subscriptions.filter((s) => s.status === 'canceled').length,
		mrr: subscriptions
			.filter((s) => s.status === 'active')
			.reduce((sum, s) => {
				const price = s.billing_interval === 'yearly'
					? (s.plan.price_yearly || s.plan.price_monthly * 12) / 12
					: s.plan.price_monthly;
				return sum + price;
			}, 0)
	});

	onMount(async () => {
		await Promise.all([loadSubscriptions(), loadPlans()]);
	});

	async function loadSubscriptions() {
		loading = true;
		error = null;
		try {
			const filters: { status?: string; plan_id?: string } = {};
			if (statusFilter !== 'all') filters.status = statusFilter;
			if (planFilter !== 'all') filters.plan_id = planFilter;

			const response = await getSubscriptions(page, perPage, filters);
			subscriptions = response.items;
			totalSubscriptions = response.total;
			totalPages = response.pages;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load subscriptions';
		} finally {
			loading = false;
		}
	}

	async function loadPlans() {
		try {
			const response = await getPlans(1, 100, true);
			plans = response.items;
		} catch (e) {
			console.error('Failed to load plans:', e);
		}
	}

	function handleStatusFilterChange(value: string | undefined) {
		if (value) {
			statusFilter = value;
			page = 1;
			loadSubscriptions();
		}
	}

	function handlePlanFilterChange(value: string | undefined) {
		if (value) {
			planFilter = value;
			page = 1;
			loadSubscriptions();
		}
	}

	function openActionDialog(subscription: Subscription, type: 'upgrade' | 'downgrade' | 'cancel' | 'reactivate') {
		actionSubscription = subscription;
		actionType = type;
		selectedPlanId = '';
		cancelReason = '';
	}

	function closeActionDialog() {
		actionSubscription = null;
		actionType = null;
		selectedPlanId = '';
		cancelReason = '';
	}

	async function executeAction() {
		if (!actionSubscription || !actionType) return;

		actionLoading = true;
		try {
			switch (actionType) {
				case 'upgrade':
					if (!selectedPlanId) {
						toast.error('Please select a plan');
						return;
					}
					await upgradeSubscription(actionSubscription.id, selectedPlanId);
					toast.success('Subscription upgraded successfully');
					break;
				case 'downgrade':
					if (!selectedPlanId) {
						toast.error('Please select a plan');
						return;
					}
					await downgradeSubscription(actionSubscription.id, selectedPlanId);
					toast.success('Subscription downgraded successfully');
					break;
				case 'cancel':
					await cancelSubscription(actionSubscription.id, cancelReason || undefined);
					toast.success('Subscription canceled successfully');
					break;
				case 'reactivate':
					await reactivateSubscription(actionSubscription.id);
					toast.success('Subscription reactivated successfully');
					break;
			}
			closeActionDialog();
			await loadSubscriptions();
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Action failed');
		} finally {
			actionLoading = false;
		}
	}

	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 0,
			maximumFractionDigits: 2
		}).format(amount);
	}

	function formatDate(date: string | null): string {
		if (!date) return '-';
		return new Intl.DateTimeFormat('en-US', {
			month: 'short',
			day: 'numeric',
			year: 'numeric'
		}).format(new Date(date));
	}

	function getStatusBadge(status: string): { variant: 'default' | 'secondary' | 'destructive' | 'outline'; label: string } {
		switch (status) {
			case 'active':
				return { variant: 'default', label: 'Active' };
			case 'trialing':
				return { variant: 'secondary', label: 'Trial' };
			case 'canceled':
				return { variant: 'destructive', label: 'Canceled' };
			case 'past_due':
				return { variant: 'destructive', label: 'Past Due' };
			case 'paused':
				return { variant: 'outline', label: 'Paused' };
			case 'expired':
				return { variant: 'outline', label: 'Expired' };
			default:
				return { variant: 'secondary', label: status };
		}
	}

	function getBillingBadge(interval: string): 'default' | 'secondary' {
		return interval === 'yearly' ? 'default' : 'secondary';
	}

	function getAvailablePlansForUpgrade(currentPlanId: string): Plan[] {
		const currentPlan = plans.find((p) => p.id === currentPlanId);
		if (!currentPlan) return plans;
		return plans.filter((p) => p.price_monthly > currentPlan.price_monthly && p.is_active);
	}

	function getAvailablePlansForDowngrade(currentPlanId: string): Plan[] {
		const currentPlan = plans.find((p) => p.id === currentPlanId);
		if (!currentPlan) return plans;
		return plans.filter((p) => p.price_monthly < currentPlan.price_monthly && p.is_active);
	}
</script>

<svelte:head>
	<title>Subscriptions - Admin - RAG Agent Platform</title>
</svelte:head>

<div class="p-6 space-y-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold">Subscriptions</h1>
			<p class="text-muted-foreground mt-1">Manage user subscriptions and billing</p>
		</div>
		<Button variant="outline" onclick={loadSubscriptions}>
			<RefreshCw class="h-4 w-4 mr-2" />
			Refresh
		</Button>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
		<Card.Root>
			<Card.Content class="pt-6">
				<div class="flex items-center gap-3">
					<div class="p-2 bg-primary/10 rounded-lg">
						<CreditCard class="h-5 w-5 text-primary" />
					</div>
					<div>
						<p class="text-sm text-muted-foreground">Total</p>
						<p class="text-2xl font-bold">{totalSubscriptions}</p>
					</div>
				</div>
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Content class="pt-6">
				<div class="flex items-center gap-3">
					<div class="p-2 bg-green-500/10 rounded-lg">
						<CreditCard class="h-5 w-5 text-green-500" />
					</div>
					<div>
						<p class="text-sm text-muted-foreground">Active</p>
						<p class="text-2xl font-bold">{stats.active}</p>
					</div>
				</div>
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Content class="pt-6">
				<div class="flex items-center gap-3">
					<div class="p-2 bg-blue-500/10 rounded-lg">
						<Calendar class="h-5 w-5 text-blue-500" />
					</div>
					<div>
						<p class="text-sm text-muted-foreground">Trialing</p>
						<p class="text-2xl font-bold">{stats.trialing}</p>
					</div>
				</div>
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Content class="pt-6">
				<div class="flex items-center gap-3">
					<div class="p-2 bg-red-500/10 rounded-lg">
						<XCircle class="h-5 w-5 text-red-500" />
					</div>
					<div>
						<p class="text-sm text-muted-foreground">Canceled</p>
						<p class="text-2xl font-bold">{stats.canceled}</p>
					</div>
				</div>
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Content class="pt-6">
				<div class="flex items-center gap-3">
					<div class="p-2 bg-yellow-500/10 rounded-lg">
						<DollarSign class="h-5 w-5 text-yellow-500" />
					</div>
					<div>
						<p class="text-sm text-muted-foreground">MRR</p>
						<p class="text-2xl font-bold">{formatCurrency(stats.mrr)}</p>
					</div>
				</div>
			</Card.Content>
		</Card.Root>
	</div>

	<!-- Filters -->
	<Card.Root>
		<Card.Content class="pt-6">
			<div class="flex flex-col md:flex-row gap-4">
				<!-- Status Filter -->
				<Select.Root type="single" value={statusFilter} onValueChange={handleStatusFilterChange}>
					<Select.Trigger class="w-[180px]">
						{statusFilter === 'all' ? 'All Status' : statusFilter.charAt(0).toUpperCase() + statusFilter.slice(1)}
					</Select.Trigger>
					<Select.Content>
						<Select.Item value="all">All Status</Select.Item>
						<Select.Item value="active">Active</Select.Item>
						<Select.Item value="trialing">Trialing</Select.Item>
						<Select.Item value="canceled">Canceled</Select.Item>
						<Select.Item value="past_due">Past Due</Select.Item>
						<Select.Item value="paused">Paused</Select.Item>
						<Select.Item value="expired">Expired</Select.Item>
					</Select.Content>
				</Select.Root>

				<!-- Plan Filter -->
				<Select.Root type="single" value={planFilter} onValueChange={handlePlanFilterChange}>
					<Select.Trigger class="w-[180px]">
						{planFilter === 'all' ? 'All Plans' : plans.find((p) => p.id === planFilter)?.display_name || 'Select Plan'}
					</Select.Trigger>
					<Select.Content>
						<Select.Item value="all">All Plans</Select.Item>
						{#each plans as plan}
							<Select.Item value={plan.id}>{plan.display_name}</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
			</div>
		</Card.Content>
	</Card.Root>

	<!-- Subscriptions Table -->
	{#if loading}
		<Card.Root>
			<Card.Content class="pt-6">
				<div class="space-y-4">
					{#each Array(5) as _}
						<div class="flex items-center gap-4">
							<Skeleton class="h-10 w-10 rounded-full" />
							<div class="flex-1 space-y-2">
								<Skeleton class="h-4 w-48" />
								<Skeleton class="h-3 w-32" />
							</div>
							<Skeleton class="h-6 w-16" />
							<Skeleton class="h-6 w-20" />
							<Skeleton class="h-4 w-24" />
						</div>
					{/each}
				</div>
			</Card.Content>
		</Card.Root>
	{:else if error}
		<Card.Root class="border-destructive">
			<Card.Content class="pt-6">
				<p class="text-destructive">{error}</p>
				<Button variant="outline" class="mt-4" onclick={loadSubscriptions}>Retry</Button>
			</Card.Content>
		</Card.Root>
	{:else if subscriptions.length === 0}
		<Card.Root>
			<Card.Content class="flex flex-col items-center justify-center py-12">
				<CreditCard class="h-12 w-12 text-muted-foreground mb-4" />
				<h3 class="text-lg font-medium">No subscriptions found</h3>
				<p class="text-muted-foreground text-sm mt-1">
					{statusFilter !== 'all' || planFilter !== 'all'
						? 'Try adjusting your filters'
						: 'No subscriptions have been created yet'}
				</p>
			</Card.Content>
		</Card.Root>
	{:else}
		<Card.Root>
			<Table.Root>
				<Table.Header>
					<Table.Row>
						<Table.Head>User</Table.Head>
						<Table.Head>Plan</Table.Head>
						<Table.Head>Status</Table.Head>
						<Table.Head>Billing</Table.Head>
						<Table.Head>Price</Table.Head>
						<Table.Head>Started</Table.Head>
						<Table.Head>Next Billing</Table.Head>
						<Table.Head class="w-12"></Table.Head>
					</Table.Row>
				</Table.Header>
				<Table.Body>
					{#each subscriptions as subscription (subscription.id)}
						<Table.Row class={subscription.status === 'canceled' ? 'opacity-60' : ''}>
							<Table.Cell>
								<div class="flex items-center gap-3">
									<div class="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
										<span class="text-sm font-medium text-primary">
											{subscription.user.email.charAt(0).toUpperCase()}
										</span>
									</div>
									<div>
										<p class="font-medium">{subscription.user.username}</p>
										<p class="text-sm text-muted-foreground">{subscription.user.email}</p>
									</div>
								</div>
							</Table.Cell>
							<Table.Cell>
								<Badge variant="outline">{subscription.plan.display_name}</Badge>
							</Table.Cell>
							<Table.Cell>
								{@const status = getStatusBadge(subscription.status)}
								<Badge variant={status.variant}>{status.label}</Badge>
							</Table.Cell>
							<Table.Cell>
								<Badge variant={getBillingBadge(subscription.billing_interval)}>
									{subscription.billing_interval}
								</Badge>
							</Table.Cell>
							<Table.Cell>
								<span class="font-medium">
									{formatCurrency(
										subscription.billing_interval === 'yearly'
											? subscription.plan.price_yearly || subscription.plan.price_monthly * 12
											: subscription.plan.price_monthly
									)}
								</span>
								<span class="text-muted-foreground text-sm">
									/{subscription.billing_interval === 'yearly' ? 'yr' : 'mo'}
								</span>
							</Table.Cell>
							<Table.Cell>
								<span class="text-sm">{formatDate(subscription.start_date)}</span>
							</Table.Cell>
							<Table.Cell>
								<span class="text-sm">{formatDate(subscription.current_period_end)}</span>
							</Table.Cell>
							<Table.Cell>
								<DropdownMenu.Root>
									<DropdownMenu.Trigger>
										<Button variant="ghost" size="icon">
											<MoreHorizontal class="h-4 w-4" />
										</Button>
									</DropdownMenu.Trigger>
									<DropdownMenu.Content align="end">
										{#if subscription.status === 'active' || subscription.status === 'trialing'}
											<DropdownMenu.Item onclick={() => openActionDialog(subscription, 'upgrade')}>
												<ArrowUpCircle class="h-4 w-4 mr-2" />
												Upgrade
											</DropdownMenu.Item>
											<DropdownMenu.Item onclick={() => openActionDialog(subscription, 'downgrade')}>
												<ArrowDownCircle class="h-4 w-4 mr-2" />
												Downgrade
											</DropdownMenu.Item>
											<DropdownMenu.Separator />
											<DropdownMenu.Item
												class="text-destructive"
												onclick={() => openActionDialog(subscription, 'cancel')}
											>
												<XCircle class="h-4 w-4 mr-2" />
												Cancel
											</DropdownMenu.Item>
										{:else if subscription.status === 'canceled'}
											<DropdownMenu.Item onclick={() => openActionDialog(subscription, 'reactivate')}>
												<RefreshCw class="h-4 w-4 mr-2" />
												Reactivate
											</DropdownMenu.Item>
										{/if}
									</DropdownMenu.Content>
								</DropdownMenu.Root>
							</Table.Cell>
						</Table.Row>
					{/each}
				</Table.Body>
			</Table.Root>
		</Card.Root>

		<!-- Pagination -->
		{#if totalPages > 1}
			<div class="flex items-center justify-between">
				<p class="text-sm text-muted-foreground">
					Showing {(page - 1) * perPage + 1} to {Math.min(page * perPage, totalSubscriptions)} of {totalSubscriptions} subscriptions
				</p>
				<div class="flex items-center gap-2">
					<Button
						variant="outline"
						size="sm"
						disabled={page === 1}
						onclick={() => {
							page--;
							loadSubscriptions();
						}}
					>
						<ChevronLeft class="h-4 w-4" />
						Previous
					</Button>
					<span class="text-sm">
						Page {page} of {totalPages}
					</span>
					<Button
						variant="outline"
						size="sm"
						disabled={page === totalPages}
						onclick={() => {
							page++;
							loadSubscriptions();
						}}
					>
						Next
						<ChevronRight class="h-4 w-4" />
					</Button>
				</div>
			</div>
		{/if}
	{/if}
</div>

<!-- Action Dialog -->
<AlertDialog.Root open={actionSubscription !== null && actionType !== null}>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>
				{#if actionType === 'upgrade'}
					Upgrade Subscription
				{:else if actionType === 'downgrade'}
					Downgrade Subscription
				{:else if actionType === 'cancel'}
					Cancel Subscription
				{:else if actionType === 'reactivate'}
					Reactivate Subscription
				{/if}
			</AlertDialog.Title>
			<AlertDialog.Description>
				{#if actionType === 'upgrade'}
					Select a higher tier plan for {actionSubscription?.user.email}.
				{:else if actionType === 'downgrade'}
					Select a lower tier plan for {actionSubscription?.user.email}. The change will take effect at the end of the current billing period.
				{:else if actionType === 'cancel'}
					Are you sure you want to cancel the subscription for {actionSubscription?.user.email}? They will lose access at the end of the current billing period.
				{:else if actionType === 'reactivate'}
					Are you sure you want to reactivate the subscription for {actionSubscription?.user.email}?
				{/if}
			</AlertDialog.Description>
		</AlertDialog.Header>

		{#if actionType === 'upgrade' && actionSubscription}
			<div class="py-4">
				<Select.Root type="single" value={selectedPlanId} onValueChange={(v) => (selectedPlanId = v || '')}>
					<Select.Trigger>
						{plans.find((p) => p.id === selectedPlanId)?.display_name || 'Select a plan'}
					</Select.Trigger>
					<Select.Content>
						{#each getAvailablePlansForUpgrade(actionSubscription.plan_id) as plan}
							<Select.Item value={plan.id}>
								{plan.display_name} - {formatCurrency(plan.price_monthly)}/mo
							</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
			</div>
		{:else if actionType === 'downgrade' && actionSubscription}
			<div class="py-4">
				<Select.Root type="single" value={selectedPlanId} onValueChange={(v) => (selectedPlanId = v || '')}>
					<Select.Trigger>
						{plans.find((p) => p.id === selectedPlanId)?.display_name || 'Select a plan'}
					</Select.Trigger>
					<Select.Content>
						{#each getAvailablePlansForDowngrade(actionSubscription.plan_id) as plan}
							<Select.Item value={plan.id}>
								{plan.display_name} - {formatCurrency(plan.price_monthly)}/mo
							</Select.Item>
						{/each}
					</Select.Content>
				</Select.Root>
			</div>
		{:else if actionType === 'cancel'}
			<div class="py-4">
				<Input placeholder="Reason for cancellation (optional)" bind:value={cancelReason} />
			</div>
		{/if}

		<AlertDialog.Footer>
			<AlertDialog.Cancel onclick={closeActionDialog}>Cancel</AlertDialog.Cancel>
			<AlertDialog.Action
				onclick={executeAction}
				disabled={actionLoading || ((actionType === 'upgrade' || actionType === 'downgrade') && !selectedPlanId)}
				class={actionType === 'cancel' ? 'bg-destructive text-destructive-foreground hover:bg-destructive/90' : ''}
			>
				{actionLoading ? 'Processing...' : 'Confirm'}
			</AlertDialog.Action>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>
