<script lang="ts">
	interface DataPoint {
		label: string;
		value: number;
	}

	let { data }: { data: DataPoint[] } = $props();

	const colors = [
		'hsl(var(--primary))',
		'hsl(var(--chart-2, 173 58% 39%))',
		'hsl(var(--chart-3, 197 37% 24%))',
		'hsl(var(--chart-4, 43 74% 66%))',
		'hsl(var(--chart-5, 27 87% 67%))'
	];

	const total = $derived(data.reduce((sum, d) => sum + d.value, 0));

	const segments = $derived(() => {
		if (total === 0) return [];

		let currentAngle = 0;
		return data.map((d, i) => {
			const percentage = d.value / total;
			const angle = percentage * 360;
			const startAngle = currentAngle;
			const endAngle = currentAngle + angle;
			currentAngle = endAngle;

			// Calculate path for the arc
			const startRad = ((startAngle - 90) * Math.PI) / 180;
			const endRad = ((endAngle - 90) * Math.PI) / 180;

			const x1 = 50 + 40 * Math.cos(startRad);
			const y1 = 50 + 40 * Math.sin(startRad);
			const x2 = 50 + 40 * Math.cos(endRad);
			const y2 = 50 + 40 * Math.sin(endRad);

			const largeArc = angle > 180 ? 1 : 0;

			const path =
				percentage === 1
					? `M 50 10 A 40 40 0 1 1 49.99 10`
					: `M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArc} 1 ${x2} ${y2} Z`;

			return {
				...d,
				path,
				color: colors[i % colors.length],
				percentage: (percentage * 100).toFixed(1)
			};
		});
	});
</script>

<div class="flex flex-col items-center gap-4">
	<svg viewBox="0 0 100 100" class="w-48 h-48">
		{#each segments() as segment}
			<path d={segment.path} fill={segment.color} class="transition-opacity hover:opacity-80" />
		{/each}
		<!-- Center circle for donut effect -->
		<circle cx="50" cy="50" r="20" fill="hsl(var(--background))" />
		<text
			x="50"
			y="50"
			text-anchor="middle"
			dominant-baseline="middle"
			class="text-xs font-bold fill-foreground"
		>
			{total}
		</text>
	</svg>

	<!-- Legend -->
	<div class="flex flex-wrap justify-center gap-3 text-sm">
		{#each segments() as segment}
			<div class="flex items-center gap-1.5">
				<div class="w-3 h-3 rounded-full" style="background-color: {segment.color}"></div>
				<span class="text-muted-foreground">{segment.label}</span>
				<span class="font-medium">{segment.value}</span>
				<span class="text-muted-foreground">({segment.percentage}%)</span>
			</div>
		{/each}
	</div>
</div>
