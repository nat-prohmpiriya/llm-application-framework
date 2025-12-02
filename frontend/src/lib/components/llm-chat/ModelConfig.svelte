<script lang="ts" module>
	export interface ModelConfigValues {
		maxOutputTokens: number;
		temperature: number;
		topP: number;
		frequencyPenalty: number;
		presencePenalty: number;
	}
</script>

<script lang="ts">
	import { untrack } from 'svelte';
	import { Info } from 'lucide-svelte';
	import { Slider } from '$lib/components/ui/slider';
	import * as Popover from '$lib/components/ui/popover';

	interface Props {
		values?: ModelConfigValues;
		onChange?: (values: ModelConfigValues) => void;
	}

	let { values, onChange }: Props = $props();

	// Default values
	const defaults: ModelConfigValues = {
		maxOutputTokens: 64000,
		temperature: 0.7,
		topP: 1,
		frequencyPenalty: 0,
		presencePenalty: 0
	};

	// Local state for sliders - shadcn-svelte Slider uses arrays
	let maxOutputTokens = $state([defaults.maxOutputTokens]);
	let temperature = $state([defaults.temperature]);
	let topP = $state([defaults.topP]);
	let frequencyPenalty = $state([defaults.frequencyPenalty]);
	let presencePenalty = $state([defaults.presencePenalty]);

	// Sync when values prop changes from parent (external updates)
	$effect(() => {
		if (values) {
			const currentValues = untrack(() => ({
				maxOutputTokens: maxOutputTokens[0],
				temperature: temperature[0],
				topP: topP[0],
				frequencyPenalty: frequencyPenalty[0],
				presencePenalty: presencePenalty[0]
			}));

			// Only update if values actually differ (prevents loops)
			if (
				values.maxOutputTokens !== currentValues.maxOutputTokens ||
				values.temperature !== currentValues.temperature ||
				values.topP !== currentValues.topP ||
				values.frequencyPenalty !== currentValues.frequencyPenalty ||
				values.presencePenalty !== currentValues.presencePenalty
			) {
				maxOutputTokens = [values.maxOutputTokens];
				temperature = [values.temperature];
				topP = [values.topP];
				frequencyPenalty = [values.frequencyPenalty];
				presencePenalty = [values.presencePenalty];
			}
		}
	});

	// Handler to notify parent when slider changes
	function handleSliderChange() {
		onChange?.({
			maxOutputTokens: maxOutputTokens[0],
			temperature: temperature[0],
			topP: topP[0],
			frequencyPenalty: frequencyPenalty[0],
			presencePenalty: presencePenalty[0]
		});
	}

	function formatNumber(value: number, decimals: number = 2): string {
		return value.toFixed(decimals).replace(/\.?0+$/, '') || '0';
	}
</script>

<div class="w-72 space-y-5 p-4">
	<!-- Max Output Tokens -->
	<div class="space-y-2">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-1.5">
				<span class="text-sm font-medium">Max Output Tokens</span>
				<Popover.Root>
					<Popover.Trigger class="cursor-pointer">
						<Info
							class="size-3.5 text-muted-foreground hover:text-foreground transition-colors"
						/>
					</Popover.Trigger>
					<Popover.Content class="w-64 text-xs" side="top">
						Maximum number of tokens to generate in the response.
					</Popover.Content>
				</Popover.Root>
			</div>
			<span class="text-sm font-medium tabular-nums">{maxOutputTokens[0]}</span>
		</div>
		<Slider
			type="multiple"
			bind:value={maxOutputTokens}
			min={1}
			max={128000}
			step={1000}
			class="cursor-pointer"
			onValueChange={handleSliderChange}
		/>
	</div>

	<!-- Temperature -->
	<div class="space-y-2">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-1.5">
				<span class="text-sm font-medium">Temperature</span>
				<Popover.Root>
					<Popover.Trigger class="cursor-pointer">
						<Info
							class="size-3.5 text-muted-foreground hover:text-foreground transition-colors"
						/>
					</Popover.Trigger>
					<Popover.Content class="w-64 text-xs" side="top">
						Controls randomness. Lower values make output more focused and
						deterministic.
					</Popover.Content>
				</Popover.Root>
			</div>
			<span class="text-sm font-medium tabular-nums">{formatNumber(temperature[0])}</span>
		</div>
		<Slider
			type="multiple"
			bind:value={temperature}
			min={0}
			max={2}
			step={0.01}
			class="cursor-pointer"
			onValueChange={handleSliderChange}
		/>
	</div>

	<!-- Top P -->
	<div class="space-y-2">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-1.5">
				<span class="text-sm font-medium">Top P</span>
				<Popover.Root>
					<Popover.Trigger class="cursor-pointer">
						<Info
							class="size-3.5 text-muted-foreground hover:text-foreground transition-colors"
						/>
					</Popover.Trigger>
					<Popover.Content class="w-64 text-xs" side="top">
						Nucleus sampling. Consider tokens with top_p probability mass.
					</Popover.Content>
				</Popover.Root>
			</div>
			<span class="text-sm font-medium tabular-nums">{formatNumber(topP[0])}</span>
		</div>
		<Slider
			type="multiple"
			bind:value={topP}
			min={0}
			max={1}
			step={0.01}
			class="cursor-pointer"
			onValueChange={handleSliderChange}
		/>
	</div>

	<!-- Frequency Penalty -->
	<div class="space-y-2">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-1.5">
				<span class="text-sm font-medium">Frequency Penalty</span>
				<Popover.Root>
					<Popover.Trigger class="cursor-pointer">
						<Info
							class="size-3.5 text-muted-foreground hover:text-foreground transition-colors"
						/>
					</Popover.Trigger>
					<Popover.Content class="w-64 text-xs" side="top">
						Penalize tokens based on their frequency in the text so far.
					</Popover.Content>
				</Popover.Root>
			</div>
			<span class="text-sm font-medium tabular-nums">{formatNumber(frequencyPenalty[0])}</span
			>
		</div>
		<Slider
			type="multiple"
			bind:value={frequencyPenalty}
			min={0}
			max={2}
			step={0.01}
			class="cursor-pointer"
			onValueChange={handleSliderChange}
		/>
	</div>

	<!-- Presence Penalty -->
	<div class="space-y-2">
		<div class="flex items-center justify-between">
			<div class="flex items-center gap-1.5">
				<span class="text-sm font-medium">Presence Penalty</span>
				<Popover.Root>
					<Popover.Trigger class="cursor-pointer">
						<Info
							class="size-3.5 text-muted-foreground hover:text-foreground transition-colors"
						/>
					</Popover.Trigger>
					<Popover.Content class="w-64 text-xs" side="top">
						Penalize tokens based on whether they appear in the text so far.
					</Popover.Content>
				</Popover.Root>
			</div>
			<span class="text-sm font-medium tabular-nums">{formatNumber(presencePenalty[0])}</span>
		</div>
		<Slider
			type="multiple"
			bind:value={presencePenalty}
			min={0}
			max={2}
			step={0.01}
			class="cursor-pointer"
			onValueChange={handleSliderChange}
		/>
	</div>
</div>
