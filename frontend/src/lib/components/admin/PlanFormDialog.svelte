<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Textarea } from '$lib/components/ui/textarea';
	import { Switch } from '$lib/components/ui/switch';
	import * as Select from '$lib/components/ui/select';
	import { createPlan, updatePlan, type Plan } from '$lib/api/admin';
	import { toast } from 'svelte-sonner';
	import { Loader2 } from 'lucide-svelte';

	let {
		open = $bindable(false),
		plan = null,
		onSave
	}: {
		open?: boolean;
		plan?: Plan | null;
		onSave?: () => void;
	} = $props();

	let saving = $state(false);

	// Form state
	let formData = $state({
		name: '',
		display_name: '',
		description: '',
		plan_type: 'free' as 'free' | 'pro' | 'enterprise',
		price_monthly: 0,
		price_yearly: null as number | null,
		currency: 'USD',
		tokens_per_month: 100000,
		requests_per_minute: 10,
		requests_per_day: 1000,
		max_documents: 10,
		max_projects: 3,
		max_agents: 1,
		allowed_models: [] as string[],
		is_active: true,
		is_public: true,
		stripe_price_id_monthly: '',
		stripe_price_id_yearly: '',
		stripe_product_id: ''
	});

	let modelsInput = $state('');

	// Reset form when dialog opens
	$effect(() => {
		if (open) {
			if (plan) {
				formData = {
					name: plan.name,
					display_name: plan.display_name,
					description: plan.description || '',
					plan_type: plan.plan_type,
					price_monthly: plan.price_monthly,
					price_yearly: plan.price_yearly,
					currency: plan.currency,
					tokens_per_month: plan.tokens_per_month,
					requests_per_minute: plan.requests_per_minute,
					requests_per_day: plan.requests_per_day,
					max_documents: plan.max_documents,
					max_projects: plan.max_projects,
					max_agents: plan.max_agents,
					allowed_models: plan.allowed_models,
					is_active: plan.is_active,
					is_public: plan.is_public,
					stripe_price_id_monthly: plan.stripe_price_id_monthly || '',
					stripe_price_id_yearly: plan.stripe_price_id_yearly || '',
					stripe_product_id: plan.stripe_product_id || ''
				};
				modelsInput = plan.allowed_models.join(', ');
			} else {
				formData = {
					name: '',
					display_name: '',
					description: '',
					plan_type: 'free',
					price_monthly: 0,
					price_yearly: null,
					currency: 'USD',
					tokens_per_month: 100000,
					requests_per_minute: 10,
					requests_per_day: 1000,
					max_documents: 10,
					max_projects: 3,
					max_agents: 1,
					allowed_models: [],
					is_active: true,
					is_public: true,
					stripe_price_id_monthly: '',
					stripe_price_id_yearly: '',
					stripe_product_id: ''
				};
				modelsInput = '';
			}
		}
	});

	async function handleSubmit(e: Event) {
		e.preventDefault();

		// Parse models from comma-separated string
		const models = modelsInput
			.split(',')
			.map((m) => m.trim())
			.filter((m) => m.length > 0);

		const data = {
			...formData,
			allowed_models: models,
			description: formData.description || null,
			price_yearly: formData.price_yearly || null,
			stripe_price_id_monthly: formData.stripe_price_id_monthly || null,
			stripe_price_id_yearly: formData.stripe_price_id_yearly || null,
			stripe_product_id: formData.stripe_product_id || null
		};

		saving = true;
		try {
			if (plan) {
				await updatePlan(plan.id, data);
				toast.success('Plan updated successfully');
			} else {
				await createPlan(data);
				toast.success('Plan created successfully');
			}
			open = false;
			onSave?.();
		} catch (e) {
			toast.error(e instanceof Error ? e.message : 'Failed to save plan');
		} finally {
			saving = false;
		}
	}

	const planTypes = [
		{ value: 'free', label: 'Free' },
		{ value: 'pro', label: 'Pro' },
		{ value: 'enterprise', label: 'Enterprise' }
	];
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="max-w-2xl max-h-[90vh] overflow-y-auto">
		<Dialog.Header>
			<Dialog.Title>{plan ? 'Edit Plan' : 'Create Plan'}</Dialog.Title>
			<Dialog.Description>
				{plan ? 'Update the plan details below.' : 'Fill in the details for the new plan.'}
			</Dialog.Description>
		</Dialog.Header>

		<form onsubmit={handleSubmit} class="space-y-6">
			<!-- Basic Info -->
			<div class="grid gap-4 md:grid-cols-2">
				<div class="space-y-2">
					<Label for="name">Internal Name</Label>
					<Input
						id="name"
						bind:value={formData.name}
						placeholder="e.g., pro_monthly"
						required
					/>
				</div>
				<div class="space-y-2">
					<Label for="display_name">Display Name</Label>
					<Input
						id="display_name"
						bind:value={formData.display_name}
						placeholder="e.g., Pro Plan"
						required
					/>
				</div>
			</div>

			<div class="space-y-2">
				<Label for="description">Description</Label>
				<Textarea
					id="description"
					bind:value={formData.description}
					placeholder="Describe the plan benefits..."
					rows={2}
				/>
			</div>

			<div class="grid gap-4 md:grid-cols-2">
				<div class="space-y-2">
					<Label for="plan_type">Plan Type</Label>
					<Select.Root
						type="single"
						value={formData.plan_type}
						onValueChange={(v) => {
							if (v) formData.plan_type = v as 'free' | 'pro' | 'enterprise';
						}}
					>
						<Select.Trigger>
							{planTypes.find((t) => t.value === formData.plan_type)?.label || 'Select type'}
						</Select.Trigger>
						<Select.Content>
							{#each planTypes as type}
								<Select.Item value={type.value}>{type.label}</Select.Item>
							{/each}
						</Select.Content>
					</Select.Root>
				</div>
				<div class="space-y-2">
					<Label for="currency">Currency</Label>
					<Input id="currency" bind:value={formData.currency} placeholder="USD" maxlength={3} />
				</div>
			</div>

			<!-- Pricing -->
			<div class="space-y-2">
				<h3 class="font-medium">Pricing</h3>
				<div class="grid gap-4 md:grid-cols-2">
					<div class="space-y-2">
						<Label for="price_monthly">Monthly Price</Label>
						<Input
							id="price_monthly"
							type="number"
							bind:value={formData.price_monthly}
							min={0}
							step={0.01}
						/>
					</div>
					<div class="space-y-2">
						<Label for="price_yearly">Yearly Price (optional)</Label>
						<Input
							id="price_yearly"
							type="number"
							bind:value={formData.price_yearly}
							min={0}
							step={0.01}
							placeholder="Leave empty for monthly only"
						/>
					</div>
				</div>
			</div>

			<!-- Limits -->
			<div class="space-y-2">
				<h3 class="font-medium">Usage Limits</h3>
				<div class="grid gap-4 md:grid-cols-3">
					<div class="space-y-2">
						<Label for="tokens_per_month">Tokens/Month</Label>
						<Input
							id="tokens_per_month"
							type="number"
							bind:value={formData.tokens_per_month}
							min={0}
						/>
					</div>
					<div class="space-y-2">
						<Label for="requests_per_minute">Requests/Minute</Label>
						<Input
							id="requests_per_minute"
							type="number"
							bind:value={formData.requests_per_minute}
							min={1}
						/>
					</div>
					<div class="space-y-2">
						<Label for="requests_per_day">Requests/Day</Label>
						<Input
							id="requests_per_day"
							type="number"
							bind:value={formData.requests_per_day}
							min={1}
						/>
					</div>
				</div>
				<div class="grid gap-4 md:grid-cols-3">
					<div class="space-y-2">
						<Label for="max_documents">Max Documents</Label>
						<Input
							id="max_documents"
							type="number"
							bind:value={formData.max_documents}
							min={0}
						/>
					</div>
					<div class="space-y-2">
						<Label for="max_projects">Max Projects</Label>
						<Input id="max_projects" type="number" bind:value={formData.max_projects} min={0} />
					</div>
					<div class="space-y-2">
						<Label for="max_agents">Max Agents</Label>
						<Input id="max_agents" type="number" bind:value={formData.max_agents} min={0} />
					</div>
				</div>
			</div>

			<!-- Models -->
			<div class="space-y-2">
				<Label for="allowed_models">Allowed Models</Label>
				<Input
					id="allowed_models"
					bind:value={modelsInput}
					placeholder="gpt-4, gpt-3.5-turbo, claude-3-opus (comma-separated)"
				/>
				<p class="text-xs text-muted-foreground">Comma-separated list of model names</p>
			</div>

			<!-- Stripe IDs -->
			<div class="space-y-2">
				<h3 class="font-medium">Stripe Integration (optional)</h3>
				<div class="grid gap-4 md:grid-cols-3">
					<div class="space-y-2">
						<Label for="stripe_product_id">Product ID</Label>
						<Input
							id="stripe_product_id"
							bind:value={formData.stripe_product_id}
							placeholder="prod_..."
						/>
					</div>
					<div class="space-y-2">
						<Label for="stripe_price_id_monthly">Monthly Price ID</Label>
						<Input
							id="stripe_price_id_monthly"
							bind:value={formData.stripe_price_id_monthly}
							placeholder="price_..."
						/>
					</div>
					<div class="space-y-2">
						<Label for="stripe_price_id_yearly">Yearly Price ID</Label>
						<Input
							id="stripe_price_id_yearly"
							bind:value={formData.stripe_price_id_yearly}
							placeholder="price_..."
						/>
					</div>
				</div>
			</div>

			<!-- Status -->
			<div class="flex items-center gap-6">
				<div class="flex items-center gap-2">
					<Switch id="is_active" bind:checked={formData.is_active} />
					<Label for="is_active">Active</Label>
				</div>
				<div class="flex items-center gap-2">
					<Switch id="is_public" bind:checked={formData.is_public} />
					<Label for="is_public">Public</Label>
				</div>
			</div>

			<Dialog.Footer>
				<Button type="button" variant="outline" onclick={() => (open = false)}>Cancel</Button>
				<Button type="submit" disabled={saving}>
					{#if saving}
						<Loader2 class="h-4 w-4 mr-2 animate-spin" />
					{/if}
					{plan ? 'Update Plan' : 'Create Plan'}
				</Button>
			</Dialog.Footer>
		</form>
	</Dialog.Content>
</Dialog.Root>
