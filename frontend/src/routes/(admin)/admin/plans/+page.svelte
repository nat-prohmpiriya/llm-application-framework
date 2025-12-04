<script lang="ts">
	import { onMount } from 'svelte';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import { Skeleton } from '$lib/components/ui/skeleton';
	import * as AlertDialog from '$lib/components/ui/alert-dialog';
	import { getPlans, deletePlan, type Plan } from '$lib/api/admin';
	import {
		Plus,
		Pencil,
		Trash2,
		Users,
		Zap,
		FileText,
		Folder,
		Bot,
		CreditCard,
		DollarSign
	} from 'lucide-svelte';
	import PlanFormDialog from '$lib/components/admin/PlanFormDialog.svelte';
	import { toast } from 'svelte-sonner';

	let plans = $state<Plan[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Dialog states
	let showCreateDialog = $state(false);
	let showEditDialog = $state(false);
	let editingPlan = $state<Plan | null>(null);
	let deleteConfirmPlan = $state<Plan | null>(null);
	let deleting = $state(false);

	// Stats
	let totalSubscribers = $derived(plans.reduce((sum, p) => sum + (p.subscriber_count || 0), 0));
	let mrr = $derived(
		plans.reduce((sum, p) => sum + (p.subscriber_count || 0) * p.price_monthly, 0)
	);

	onMount(loadPlans);

	async function loadPlans() {
		loading = true;
		error = null;
		try {
			const response = await getPlans(1, 100, true);
			plans = response.items;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load plans';
		} finally {
			loading = false;
		}
	}

	function handleEdit(plan: Plan) {
		editingPlan = plan;
		showEditDialog = true;
	}

	function handleDeleteClick(plan: Plan) {
		deleteConfirmPlan = plan;
	}

	async function confirmDelete() {
		if (!deleteConfirmPlan) return;

		deleting = true;
		try {
			await deletePlan(deleteConfirmPlan.id);
			toast.success('Plan deleted successfully');
			await loadPlans();
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Failed to delete plan');
		} finally {
			deleting = false;
			deleteConfirmPlan = null;
		}
	}

	async function handlePlanSaved() {
		showCreateDialog = false;
		showEditDialog = false;
		editingPlan = null;
		await loadPlans();
	}

	function formatCurrency(amount: number): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: 'USD',
			minimumFractionDigits: 0,
			maximumFractionDigits: 0
		}).format(amount);
	}

	function getPlanTypeColor(type: string): 'default' | 'secondary' | 'destructive' | 'outline' {
		switch (type) {
			case 'free':
				return 'secondary';
			case 'pro':
				return 'default';
			case 'enterprise':
				return 'destructive';
			default:
				return 'outline';
		}
	}
</script>

<svelte:head>
	<title>Plans - Admin - RAG Agent Platform</title>
</svelte:head>

<div class="p-6 space-y-6">
	<!-- Header -->
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold">Plans</h1>
			<p class="text-muted-foreground mt-1">Manage subscription plans and pricing</p>
		</div>
		<Button onclick={() => (showCreateDialog = true)}>
			<Plus class="h-4 w-4 mr-2" />
			Create Plan
		</Button>
	</div>

	<!-- Stats Cards -->
	<div class="grid gap-4 md:grid-cols-3">
		<Card.Root>
			<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
				<Card.Title class="text-sm font-medium">Total Plans</Card.Title>
				<CreditCard class="h-4 w-4 text-muted-foreground" />
			</Card.Header>
			<Card.Content>
				<div class="text-2xl font-bold">{loading ? '-' : plans.length}</div>
				<p class="text-xs text-muted-foreground">
					{plans.filter((p) => p.is_active).length} active
				</p>
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
				<Card.Title class="text-sm font-medium">Total Subscribers</Card.Title>
				<Users class="h-4 w-4 text-muted-foreground" />
			</Card.Header>
			<Card.Content>
				<div class="text-2xl font-bold">{loading ? '-' : totalSubscribers}</div>
				<p class="text-xs text-muted-foreground">Across all plans</p>
			</Card.Content>
		</Card.Root>

		<Card.Root>
			<Card.Header class="flex flex-row items-center justify-between space-y-0 pb-2">
				<Card.Title class="text-sm font-medium">Monthly Revenue</Card.Title>
				<DollarSign class="h-4 w-4 text-muted-foreground" />
			</Card.Header>
			<Card.Content>
				<div class="text-2xl font-bold">{loading ? '-' : formatCurrency(mrr)}</div>
				<p class="text-xs text-muted-foreground">MRR from subscriptions</p>
			</Card.Content>
		</Card.Root>
	</div>

	<!-- Plans Grid -->
	{#if loading}
		<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
			{#each Array(3) as _}
				<Card.Root>
					<Card.Header>
						<Skeleton class="h-6 w-32" />
						<Skeleton class="h-4 w-48 mt-2" />
					</Card.Header>
					<Card.Content class="space-y-3">
						<Skeleton class="h-8 w-24" />
						<Skeleton class="h-4 w-full" />
						<Skeleton class="h-4 w-full" />
						<Skeleton class="h-4 w-3/4" />
					</Card.Content>
				</Card.Root>
			{/each}
		</div>
	{:else if error}
		<Card.Root class="border-destructive">
			<Card.Content class="pt-6">
				<p class="text-destructive">{error}</p>
				<Button variant="outline" class="mt-4" onclick={loadPlans}>Retry</Button>
			</Card.Content>
		</Card.Root>
	{:else if plans.length === 0}
		<Card.Root>
			<Card.Content class="flex flex-col items-center justify-center py-12">
				<CreditCard class="h-12 w-12 text-muted-foreground mb-4" />
				<h3 class="text-lg font-medium">No plans yet</h3>
				<p class="text-muted-foreground text-sm mt-1">
					Create your first plan to start accepting subscriptions
				</p>
				<Button class="mt-4" onclick={() => (showCreateDialog = true)}>
					<Plus class="h-4 w-4 mr-2" />
					Create Plan
				</Button>
			</Card.Content>
		</Card.Root>
	{:else}
		<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
			{#each plans as plan (plan.id)}
				<Card.Root class="relative {!plan.is_active ? 'opacity-60' : ''}">
					<!-- Actions -->
					<div class="absolute top-4 right-4 flex gap-1">
						<Button variant="ghost" size="icon" onclick={() => handleEdit(plan)}>
							<Pencil class="h-4 w-4" />
						</Button>
						<Button
							variant="ghost"
							size="icon"
							onclick={() => handleDeleteClick(plan)}
							disabled={(plan.subscriber_count || 0) > 0}
						>
							<Trash2 class="h-4 w-4" />
						</Button>
					</div>

					<Card.Header>
						<div class="flex items-center gap-2">
							<Card.Title>{plan.display_name}</Card.Title>
							<Badge variant={getPlanTypeColor(plan.plan_type)}>{plan.plan_type}</Badge>
							{#if !plan.is_active}
								<Badge variant="outline">Inactive</Badge>
							{/if}
						</div>
						<Card.Description class="line-clamp-2">
							{plan.description || 'No description'}
						</Card.Description>
					</Card.Header>

					<Card.Content class="space-y-4">
						<!-- Price -->
						<div>
							<span class="text-3xl font-bold">{formatCurrency(plan.price_monthly)}</span>
							<span class="text-muted-foreground">/month</span>
							{#if plan.price_yearly}
								<p class="text-sm text-muted-foreground">
									or {formatCurrency(plan.price_yearly)}/year
								</p>
							{/if}
						</div>

						<!-- Subscribers -->
						<div class="flex items-center gap-2 text-sm">
							<Users class="h-4 w-4 text-muted-foreground" />
							<span class="font-medium">{plan.subscriber_count || 0}</span>
							<span class="text-muted-foreground">subscribers</span>
						</div>

						<!-- Limits -->
						<div class="space-y-2 text-sm">
							<div class="flex items-center gap-2">
								<Zap class="h-4 w-4 text-muted-foreground" />
								<span>{(plan.tokens_per_month / 1000).toFixed(0)}K tokens/month</span>
							</div>
							<div class="flex items-center gap-2">
								<FileText class="h-4 w-4 text-muted-foreground" />
								<span>{plan.max_documents} documents</span>
							</div>
							<div class="flex items-center gap-2">
								<Folder class="h-4 w-4 text-muted-foreground" />
								<span>{plan.max_projects} projects</span>
							</div>
							<div class="flex items-center gap-2">
								<Bot class="h-4 w-4 text-muted-foreground" />
								<span>{plan.max_agents} agents</span>
							</div>
						</div>

						<!-- Models -->
						{#if plan.allowed_models.length > 0}
							<div class="pt-2 border-t">
								<p class="text-xs text-muted-foreground mb-1">Allowed Models</p>
								<div class="flex flex-wrap gap-1">
									{#each plan.allowed_models.slice(0, 3) as model}
										<Badge variant="outline" class="text-xs">{model}</Badge>
									{/each}
									{#if plan.allowed_models.length > 3}
										<Badge variant="outline" class="text-xs">
											+{plan.allowed_models.length - 3} more
										</Badge>
									{/if}
								</div>
							</div>
						{/if}
					</Card.Content>
				</Card.Root>
			{/each}
		</div>
	{/if}
</div>

<!-- Create Plan Dialog -->
<PlanFormDialog bind:open={showCreateDialog} onSave={handlePlanSaved} />

<!-- Edit Plan Dialog -->
<PlanFormDialog bind:open={showEditDialog} plan={editingPlan} onSave={handlePlanSaved} />

<!-- Delete Confirmation Dialog -->
<AlertDialog.Root open={deleteConfirmPlan !== null}>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>Delete Plan</AlertDialog.Title>
			<AlertDialog.Description>
				Are you sure you want to delete "{deleteConfirmPlan?.display_name}"? This action cannot be
				undone.
			</AlertDialog.Description>
		</AlertDialog.Header>
		<AlertDialog.Footer>
			<AlertDialog.Cancel onclick={() => (deleteConfirmPlan = null)}>Cancel</AlertDialog.Cancel>
			<AlertDialog.Action
				onclick={confirmDelete}
				disabled={deleting}
				class="bg-destructive text-destructive-foreground hover:bg-destructive/90"
			>
				{deleting ? 'Deleting...' : 'Delete'}
			</AlertDialog.Action>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>
