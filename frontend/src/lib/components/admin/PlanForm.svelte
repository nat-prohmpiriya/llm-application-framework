<script lang="ts" module>
	export interface PlanFeatures {
		api_access: boolean;
		priority_support: boolean;
		max_team_members: number;
	}

	export interface PlanFormData {
		name: string;
		display_name: string;
		description: string | null;
		plan_type: 'free' | 'pro' | 'enterprise';
		price_monthly: number;
		price_yearly: number | null;
		currency: string;
		tokens_per_month: number;
		requests_per_minute: number;
		requests_per_day: number;
		max_documents: number;
		max_projects: number;
		max_agents: number;
		max_file_size_mb: number;
		allowed_models: string[];
		features: PlanFeatures;
		is_active: boolean;
		is_public: boolean;
		stripe_price_id_monthly: string | null;
		stripe_price_id_yearly: string | null;
		stripe_product_id: string | null;
	}
</script>

<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Textarea } from '$lib/components/ui/textarea';
	import { Switch } from '$lib/components/ui/switch';
	import { Checkbox } from '$lib/components/ui/checkbox';
	import { Slider } from '$lib/components/ui/slider';
	import { Button } from '$lib/components/ui/button';
	import * as Select from '$lib/components/ui/select';
	import * as Card from '$lib/components/ui/card';
	import { Separator } from '$lib/components/ui/separator';
	import type { Plan } from '$lib/api/admin';

	let {
		plan = null,
		onSubmit,
		actions
	}: {
		plan?: Plan | null;
		onSubmit?: (data: PlanFormData) => void;
		actions?: Snippet;
	} = $props();

	// Model tiers
	const modelTiers = {
		basic: {
			label: 'Basic',
			models: ['gpt-3.5-turbo', 'claude-3-haiku', 'gemini-1.5-flash', 'llama-3.1-8b']
		},
		standard: {
			label: 'Standard',
			models: ['gpt-4o-mini', 'claude-3.5-sonnet', 'gemini-1.5-pro', 'llama-3.1-70b']
		},
		premium: {
			label: 'Premium',
			models: ['gpt-4o', 'gpt-4-turbo', 'claude-3-opus', 'gemini-1.5-ultra', 'llama-3.1-405b']
		}
	};

	// Form state
	let formData = $state<PlanFormData>({
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
		max_file_size_mb: 10,
		allowed_models: [],
		features: {
			api_access: false,
			priority_support: false,
			max_team_members: 1
		},
		is_active: true,
		is_public: true,
		stripe_price_id_monthly: null,
		stripe_price_id_yearly: null,
		stripe_product_id: null
	});

	// Slider values (single number for type="single")
	let tokenSliderValue = $state(100000);
	let requestsPerMinuteSlider = $state(10);
	let requestsPerDaySlider = $state(1000);

	// Sync slider values with form data
	$effect(() => {
		formData.tokens_per_month = tokenSliderValue;
	});

	$effect(() => {
		formData.requests_per_minute = requestsPerMinuteSlider;
	});

	$effect(() => {
		formData.requests_per_day = requestsPerDaySlider;
	});

	// Auto-generate slug from display name
	function generateSlug(name: string): string {
		return name
			.toLowerCase()
			.replace(/[^a-z0-9\s-]/g, '')
			.replace(/\s+/g, '_')
			.replace(/-+/g, '_');
	}

	function handleDisplayNameChange(e: Event) {
		const target = e.target as HTMLInputElement;
		formData.display_name = target.value;
		if (!plan) {
			formData.name = generateSlug(target.value);
		}
	}

	// Calculate annual savings
	let annualSavings = $derived(() => {
		if (!formData.price_yearly || formData.price_monthly === 0) return null;
		const monthlyTotal = formData.price_monthly * 12;
		const savings = ((monthlyTotal - formData.price_yearly) / monthlyTotal) * 100;
		return savings > 0 ? savings.toFixed(0) : null;
	});

	// Initialize form with plan data
	$effect(() => {
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
				max_file_size_mb: (plan as any).max_file_size_mb || 10,
				allowed_models: [...plan.allowed_models],
				features: (plan as any).features || {
					api_access: false,
					priority_support: false,
					max_team_members: 1
				},
				is_active: plan.is_active,
				is_public: plan.is_public,
				stripe_price_id_monthly: plan.stripe_price_id_monthly || null,
				stripe_price_id_yearly: plan.stripe_price_id_yearly || null,
				stripe_product_id: plan.stripe_product_id || null
			};
			tokenSliderValue = plan.tokens_per_month;
			requestsPerMinuteSlider = plan.requests_per_minute;
			requestsPerDaySlider = plan.requests_per_day;
		}
	});

	// Model selection helpers
	function isModelSelected(model: string): boolean {
		return formData.allowed_models.includes(model);
	}

	function toggleModel(model: string) {
		if (isModelSelected(model)) {
			formData.allowed_models = formData.allowed_models.filter((m) => m !== model);
		} else {
			formData.allowed_models = [...formData.allowed_models, model];
		}
	}

	function selectTier(tier: keyof typeof modelTiers) {
		const tierModels = modelTiers[tier].models;
		const allSelected = tierModels.every((m) => isModelSelected(m));

		if (allSelected) {
			formData.allowed_models = formData.allowed_models.filter((m) => !tierModels.includes(m));
		} else {
			const newModels = tierModels.filter((m) => !isModelSelected(m));
			formData.allowed_models = [...formData.allowed_models, ...newModels];
		}
	}

	function isTierFullySelected(tier: keyof typeof modelTiers): boolean {
		return modelTiers[tier].models.every((m) => isModelSelected(m));
	}

	function isTierPartiallySelected(tier: keyof typeof modelTiers): boolean {
		const models = modelTiers[tier].models;
		const selectedCount = models.filter((m) => isModelSelected(m)).length;
		return selectedCount > 0 && selectedCount < models.length;
	}

	// Quick select buttons for token limits
	const tokenPresets = [
		{ label: '100K', value: 100000 },
		{ label: '500K', value: 500000 },
		{ label: '1M', value: 1000000 },
		{ label: '5M', value: 5000000 },
		{ label: '10M', value: 10000000 },
		{ label: 'Unlimited', value: 999999999 }
	];

	function setTokenPreset(value: number) {
		tokenSliderValue = value;
		formData.tokens_per_month = value;
	}

	// Format numbers
	function formatTokens(value: number): string {
		if (value >= 999999999) return 'Unlimited';
		if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
		if (value >= 1000) return `${(value / 1000).toFixed(0)}K`;
		return value.toString();
	}

	const planTypes = [
		{ value: 'free', label: 'Free' },
		{ value: 'pro', label: 'Pro' },
		{ value: 'enterprise', label: 'Enterprise' }
	];

	function handleSubmit(e: Event) {
		e.preventDefault();
		onSubmit?.(formData);
	}
</script>

<form onsubmit={handleSubmit} class="space-y-8">
	<!-- Section 1: Basic Info -->
	<Card.Root>
		<Card.Header>
			<Card.Title class="text-lg">Basic Information</Card.Title>
			<Card.Description>Plan name, type, and visibility settings</Card.Description>
		</Card.Header>
		<Card.Content class="space-y-4">
			<div class="grid gap-4 md:grid-cols-2">
				<div class="space-y-2">
					<Label for="display_name">Display Name</Label>
					<Input
						id="display_name"
						value={formData.display_name}
						oninput={handleDisplayNameChange}
						placeholder="e.g., Pro Plan"
						required
					/>
				</div>
				<div class="space-y-2">
					<Label for="name">Internal Name (slug)</Label>
					<Input
						id="name"
						bind:value={formData.name}
						placeholder="e.g., pro_plan"
						required
						disabled={!!plan}
						class={plan ? 'bg-muted' : ''}
					/>
					<p class="text-xs text-muted-foreground">Auto-generated from display name</p>
				</div>
			</div>

			<div class="space-y-2">
				<Label for="description">Description</Label>
				<Textarea
					id="description"
					bind:value={formData.description}
					placeholder="Describe what's included in this plan..."
					rows={3}
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
				<div class="flex items-end gap-6">
					<div class="flex items-center gap-2">
						<Switch id="is_active" bind:checked={formData.is_active} />
						<Label for="is_active">Active</Label>
					</div>
					<div class="flex items-center gap-2">
						<Switch id="is_public" bind:checked={formData.is_public} />
						<Label for="is_public">Public</Label>
					</div>
				</div>
			</div>
		</Card.Content>
	</Card.Root>

	<!-- Section 2: Pricing -->
	<Card.Root>
		<Card.Header>
			<Card.Title class="text-lg">Pricing</Card.Title>
			<Card.Description>Monthly and annual pricing options</Card.Description>
		</Card.Header>
		<Card.Content class="space-y-4">
			<div class="grid gap-4 md:grid-cols-3">
				<div class="space-y-2">
					<Label for="currency">Currency</Label>
					<Input id="currency" bind:value={formData.currency} placeholder="USD" maxlength={3} />
				</div>
				<div class="space-y-2">
					<Label for="price_monthly">Monthly Price</Label>
					<div class="relative">
						<span class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
						<Input
							id="price_monthly"
							type="number"
							bind:value={formData.price_monthly}
							min={0}
							step={0.01}
							class="pl-7"
						/>
					</div>
				</div>
				<div class="space-y-2">
					<Label for="price_yearly">
						Annual Price
						{#if annualSavings()}
							<span class="ml-2 text-xs text-green-600 font-medium">
								Save {annualSavings()}%
							</span>
						{/if}
					</Label>
					<div class="relative">
						<span class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">$</span>
						<Input
							id="price_yearly"
							type="number"
							bind:value={formData.price_yearly}
							min={0}
							step={0.01}
							placeholder="Optional"
							class="pl-7"
						/>
					</div>
				</div>
			</div>
		</Card.Content>
	</Card.Root>

	<!-- Section 3: Usage Limits -->
	<Card.Root>
		<Card.Header>
			<Card.Title class="text-lg">Usage Limits</Card.Title>
			<Card.Description>Token and resource allocation</Card.Description>
		</Card.Header>
		<Card.Content class="space-y-6">
			<!-- Token Limit with Slider -->
			<div class="space-y-4">
				<div class="flex items-center justify-between">
					<Label>Tokens per Month</Label>
					<span class="text-lg font-semibold">{formatTokens(formData.tokens_per_month)}</span>
				</div>
				<Slider
					type="single"
					bind:value={tokenSliderValue}
					min={10000}
					max={10000000}
					step={10000}
					class="w-full"
				/>
				<div class="flex flex-wrap gap-2">
					{#each tokenPresets as preset}
						<Button
							type="button"
							variant={formData.tokens_per_month === preset.value ? 'default' : 'outline'}
							size="sm"
							onclick={() => setTokenPreset(preset.value)}
						>
							{preset.label}
						</Button>
					{/each}
				</div>
			</div>

			<Separator />

			<!-- Other Limits -->
			<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
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
				<div class="space-y-2">
					<Label for="max_file_size_mb">Max File Size (MB)</Label>
					<Input
						id="max_file_size_mb"
						type="number"
						bind:value={formData.max_file_size_mb}
						min={1}
					/>
				</div>
			</div>
		</Card.Content>
	</Card.Root>

	<!-- Section 4: Rate Limits -->
	<Card.Root>
		<Card.Header>
			<Card.Title class="text-lg">Rate Limits</Card.Title>
			<Card.Description>Request throttling settings</Card.Description>
		</Card.Header>
		<Card.Content class="space-y-6">
			<div class="grid gap-6 md:grid-cols-2">
				<div class="space-y-4">
					<div class="flex items-center justify-between">
						<Label>Requests per Minute</Label>
						<span class="font-semibold">{formData.requests_per_minute} RPM</span>
					</div>
					<Slider
						type="single"
						bind:value={requestsPerMinuteSlider}
						min={1}
						max={100}
						step={1}
						class="w-full"
					/>
				</div>
				<div class="space-y-4">
					<div class="flex items-center justify-between">
						<Label>Requests per Day</Label>
						<span class="font-semibold">{formData.requests_per_day.toLocaleString()} RPD</span>
					</div>
					<Slider
						type="single"
						bind:value={requestsPerDaySlider}
						min={100}
						max={100000}
						step={100}
						class="w-full"
					/>
				</div>
			</div>
		</Card.Content>
	</Card.Root>

	<!-- Section 5: Model Access -->
	<Card.Root>
		<Card.Header>
			<Card.Title class="text-lg">Model Access</Card.Title>
			<Card.Description>Select which AI models are available in this plan</Card.Description>
		</Card.Header>
		<Card.Content class="space-y-6">
			<!-- Quick Select Tier Buttons -->
			<div class="flex flex-wrap gap-2">
				{#each Object.entries(modelTiers) as [tier, data]}
					<Button
						type="button"
						variant={isTierFullySelected(tier as keyof typeof modelTiers) ? 'default' : 'outline'}
						size="sm"
						onclick={() => selectTier(tier as keyof typeof modelTiers)}
					>
						{isTierFullySelected(tier as keyof typeof modelTiers) ? '✓ ' : ''}
						{data.label} Tier
					</Button>
				{/each}
				<Button
					type="button"
					variant="ghost"
					size="sm"
					onclick={() => (formData.allowed_models = [])}
				>
					Clear All
				</Button>
			</div>

			<Separator />

			<!-- Model Groups -->
			<div class="grid gap-6 md:grid-cols-3">
				{#each Object.entries(modelTiers) as [tier, data]}
					<div class="space-y-3">
						<div class="flex items-center gap-2">
							<Checkbox
								id={`tier-${tier}`}
								checked={isTierFullySelected(tier as keyof typeof modelTiers)}
								indeterminate={isTierPartiallySelected(tier as keyof typeof modelTiers)}
								onCheckedChange={() => selectTier(tier as keyof typeof modelTiers)}
							/>
							<Label for={`tier-${tier}`} class="font-medium">{data.label}</Label>
						</div>
						<div class="ml-6 space-y-2">
							{#each data.models as model}
								<div class="flex items-center gap-2">
									<Checkbox
										id={`model-${model}`}
										checked={isModelSelected(model)}
										onCheckedChange={() => toggleModel(model)}
									/>
									<Label for={`model-${model}`} class="text-sm font-normal">{model}</Label>
								</div>
							{/each}
						</div>
					</div>
				{/each}
			</div>

			<!-- Selected Models Summary -->
			{#if formData.allowed_models.length > 0}
				<div class="mt-4 p-3 bg-muted rounded-lg">
					<p class="text-sm text-muted-foreground">
						<span class="font-medium">{formData.allowed_models.length}</span> models selected:
						<span class="text-foreground">{formData.allowed_models.join(', ')}</span>
					</p>
				</div>
			{/if}
		</Card.Content>
	</Card.Root>

	<!-- Section 6: Features -->
	<Card.Root>
		<Card.Header>
			<Card.Title class="text-lg">Additional Features</Card.Title>
			<Card.Description>Extra capabilities included in this plan</Card.Description>
		</Card.Header>
		<Card.Content class="space-y-4">
			<div class="grid gap-4 md:grid-cols-3">
				<div class="flex items-center gap-3 p-4 border rounded-lg">
					<Switch
						id="api_access"
						checked={formData.features.api_access}
						onCheckedChange={(checked) => (formData.features.api_access = checked)}
					/>
					<div>
						<Label for="api_access" class="font-medium">API Access</Label>
						<p class="text-xs text-muted-foreground">Direct API key access</p>
					</div>
				</div>

				<div class="flex items-center gap-3 p-4 border rounded-lg">
					<Switch
						id="priority_support"
						checked={formData.features.priority_support}
						onCheckedChange={(checked) => (formData.features.priority_support = checked)}
					/>
					<div>
						<Label for="priority_support" class="font-medium">Priority Support</Label>
						<p class="text-xs text-muted-foreground">Faster response times</p>
					</div>
				</div>

				<div class="space-y-2 p-4 border rounded-lg">
					<Label for="max_team_members">Max Team Members</Label>
					<Input
						id="max_team_members"
						type="number"
						bind:value={formData.features.max_team_members}
						min={1}
						class="mt-1"
					/>
				</div>
			</div>
		</Card.Content>
	</Card.Root>

	<!-- Stripe Integration (Collapsible) -->
	<Card.Root>
		<Card.Header>
			<Card.Title class="text-lg">Stripe Integration</Card.Title>
			<Card.Description>Optional payment gateway configuration</Card.Description>
		</Card.Header>
		<Card.Content>
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
		</Card.Content>
	</Card.Root>

	<!-- Form Actions -->
	<div class="flex justify-end gap-3">
		{#if actions}
			{@render actions()}
		{/if}
	</div>
</form>
