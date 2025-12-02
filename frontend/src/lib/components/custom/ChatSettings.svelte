<script lang="ts">
	import * as Select from '$lib/components/ui/select';
	import { Slider } from '$lib/components/ui/slider';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Button } from '$lib/components/ui/button';
	import * as Sheet from '$lib/components/ui/sheet';
	import ChevronDownIcon from '@lucide/svelte/icons/chevron-down';
	import SlidersHorizontalIcon from '@lucide/svelte/icons/sliders-horizontal';

	export interface ChatSettingsData {
		model: string;
		temperature: number;
		maxTokens: number | null;
	}

	export interface Model {
		id: string;
		name: string;
		provider: string;
	}

	const models: Model[] = [
		{ id: 'gemini-2.0-flash', name: 'Gemini 2.0 Flash', provider: 'Google' },
		{ id: 'gemini-1.5-pro', name: 'Gemini 1.5 Pro', provider: 'Google' },
		{ id: 'gemini-1.5-flash', name: 'Gemini 1.5 Flash', provider: 'Google' },
		{ id: 'llama-3.3-70b', name: 'Llama 3.3 70B', provider: 'Groq' },
		{ id: 'llama-3.1-8b', name: 'Llama 3.1 8B', provider: 'Groq' },
		{ id: 'mixtral-8x7b', name: 'Mixtral 8x7B', provider: 'Groq' },
	];

	let {
		settings = $bindable<ChatSettingsData>({
			model: 'gemini-2.0-flash',
			temperature: 0.7,
			maxTokens: null,
		}),
	}: {
		settings?: ChatSettingsData;
	} = $props();

	let isOpen = $state(false);
	let tempSliderValue = $state(settings.temperature);
	let maxTokensInput = $state(settings.maxTokens?.toString() || '');

	// Update temperature from slider
	$effect(() => {
		if (tempSliderValue !== undefined) {
			settings.temperature = Math.round(tempSliderValue * 100) / 100;
		}
	});

	// Sync slider when settings change externally
	$effect(() => {
		if (settings.temperature !== tempSliderValue) {
			tempSliderValue = settings.temperature;
		}
	});

	function handleMaxTokensChange(e: Event) {
		const target = e.target as HTMLInputElement;
		const value = target.value.trim();
		if (value === '') {
			settings.maxTokens = null;
			maxTokensInput = '';
		} else {
			const num = parseInt(value, 10);
			if (!isNaN(num) && num >= 100 && num <= 4096) {
				settings.maxTokens = num;
				maxTokensInput = value;
			}
		}
	}

	function getSelectedModel() {
		return models.find((m) => m.id === settings.model);
	}
</script>

<!-- Compact header layout -->
<div class="flex items-center gap-2">
	<!-- Model Selector (Dropdown) -->
	<Select.Root
		type="single"
		value={settings.model}
		onValueChange={(value) => {
			if (value) settings.model = value;
		}}
	>
		<Select.Trigger
			class="h-9 gap-2 border-none shadow-none bg-transparent hover:bg-accent px-3"
		>
			<div class="flex items-center gap-3">
				<!-- Model chip -->
				<div class="flex items-center gap-3 px-3 py-1 rounded-full border bg-background/50">
					<span class="font-medium text-sm"
						>{getSelectedModel()?.name || 'Select model'}</span
					>
					<!-- Badge - show provider or Pro label -->
					<span
						class="inline-flex items-center rounded-full bg-primary/10 text-primary text-xs px-2 py-0.5"
						>{getSelectedModel()?.provider || 'Pro'}</span
					>
				</div>
				<!-- Chevron -->
				<svg
					class="h-4 w-4 text-muted-foreground"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
				>
					<path d="M6 9l6 6 6-6" stroke-linecap="round" stroke-linejoin="round" />
				</svg>
			</div>
		</Select.Trigger>
		<Select.Content>
			<Select.Group>
				<Select.GroupHeading>Google</Select.GroupHeading>
				{#each models.filter((m) => m.provider === 'Google') as model}
					<Select.Item value={model.id}>
						{model.name}
					</Select.Item>
				{/each}
			</Select.Group>
			<Select.Separator />
			<Select.Group>
				<Select.GroupHeading>Groq</Select.GroupHeading>
				{#each models.filter((m) => m.provider === 'Groq') as model}
					<Select.Item value={model.id}>
						{model.name}
					</Select.Item>
				{/each}
			</Select.Group>
		</Select.Content>
	</Select.Root>

	<!-- Settings Button (opens sheet) -->
	<Sheet.Root bind:open={isOpen}>
		<Sheet.Trigger>
			{#snippet child({ props })}
				<Button variant="ghost" size="icon" {...props} class="h-9 w-9">
					<SlidersHorizontalIcon class="h-4 w-4" />
					<span class="sr-only">Settings</span>
				</Button>
			{/snippet}
		</Sheet.Trigger>
		<Sheet.Content side="right" class="w-[320px] sm:w-[400px]">
			<Sheet.Header>
				<Sheet.Title>Chat Settings</Sheet.Title>
				<Sheet.Description>Configure generation parameters</Sheet.Description>
			</Sheet.Header>

			<div class="grid gap-6 py-6">
				<!-- Temperature Slider -->
				<div class="grid gap-4">
					<div class="flex items-center justify-between">
						<Label for="temperature">Temperature</Label>
						<span class="text-sm text-muted-foreground font-mono">
							{settings.temperature.toFixed(2)}
						</span>
					</div>
					<Slider
						type="single"
						bind:value={tempSliderValue}
						min={0}
						max={2}
						step={0.1}
						class="w-full"
					/>
					<p class="text-xs text-muted-foreground">
						Lower = more focused. Higher = more creative.
					</p>
				</div>

				<!-- Max Tokens Input -->
				<div class="grid gap-2">
					<Label for="max-tokens">Max Tokens (optional)</Label>
					<Input
						id="max-tokens"
						type="number"
						placeholder="Default"
						min={100}
						max={4096}
						value={maxTokensInput}
						oninput={handleMaxTokensChange}
					/>
					<p class="text-xs text-muted-foreground">
						Maximum tokens to generate (100-4096).
					</p>
				</div>
			</div>

			<Sheet.Footer>
				<Button variant="outline" onclick={() => (isOpen = false)}>Done</Button>
			</Sheet.Footer>
		</Sheet.Content>
	</Sheet.Root>
</div>
