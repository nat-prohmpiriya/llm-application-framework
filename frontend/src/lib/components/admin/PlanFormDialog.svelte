<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog';
	import { Button } from '$lib/components/ui/button';
	import { createPlan, updatePlan, type Plan } from '$lib/api/admin';
	import { toast } from 'svelte-sonner';
	import { Loader2 } from 'lucide-svelte';
	import PlanForm, { type PlanFormData } from './PlanForm.svelte';

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

	async function handleSubmit(data: PlanFormData) {
		saving = true;
		try {
			// Transform data to API format
			const apiData = {
				name: data.name,
				display_name: data.display_name,
				description: data.description || null,
				plan_type: data.plan_type,
				price_monthly: data.price_monthly,
				price_yearly: data.price_yearly || null,
				currency: data.currency,
				tokens_per_month: data.tokens_per_month,
				requests_per_minute: data.requests_per_minute,
				requests_per_day: data.requests_per_day,
				max_documents: data.max_documents,
				max_projects: data.max_projects,
				max_agents: data.max_agents,
				allowed_models: data.allowed_models,
				is_active: data.is_active,
				is_public: data.is_public,
				stripe_price_id_monthly: data.stripe_price_id_monthly || null,
				stripe_price_id_yearly: data.stripe_price_id_yearly || null,
				stripe_product_id: data.stripe_product_id || null
			};

			if (plan) {
				await updatePlan(plan.id, apiData);
				toast.success('Plan updated successfully');
			} else {
				await createPlan(apiData);
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
</script>

<Dialog.Root bind:open>
	<Dialog.Content class="max-w-4xl max-h-[90vh] overflow-y-auto">
		<Dialog.Header>
			<Dialog.Title>{plan ? 'Edit Plan' : 'Create Plan'}</Dialog.Title>
			<Dialog.Description>
				{plan ? 'Update the plan details below.' : 'Fill in the details for the new plan.'}
			</Dialog.Description>
		</Dialog.Header>

		<PlanForm {plan} onSubmit={handleSubmit}>
			{#snippet actions()}
				<Button type="button" variant="outline" onclick={() => (open = false)}>Cancel</Button>
				<Button type="submit" disabled={saving}>
					{#if saving}
						<Loader2 class="h-4 w-4 mr-2 animate-spin" />
					{/if}
					{plan ? 'Update Plan' : 'Create Plan'}
				</Button>
			{/snippet}
		</PlanForm>
	</Dialog.Content>
</Dialog.Root>
