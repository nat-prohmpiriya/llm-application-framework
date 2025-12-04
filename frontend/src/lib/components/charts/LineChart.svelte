<script lang="ts">
	interface DataPoint {
		date: string;
		value: number;
	}

	let { data, label = 'Value' }: { data: DataPoint[]; label?: string } = $props();

	const width = 400;
	const height = 200;
	const padding = { top: 20, right: 20, bottom: 30, left: 40 };

	const chartWidth = width - padding.left - padding.right;
	const chartHeight = height - padding.top - padding.bottom;

	const maxValue = $derived(Math.max(...data.map((d) => d.value), 1));
	const minValue = $derived(0);

	const xScale = $derived((index: number) => {
		return padding.left + (index / Math.max(data.length - 1, 1)) * chartWidth;
	});

	const yScale = $derived((value: number) => {
		const range = maxValue - minValue || 1;
		return padding.top + chartHeight - ((value - minValue) / range) * chartHeight;
	});

	const linePath = $derived(() => {
		if (data.length === 0) return '';

		return data
			.map((d, i) => {
				const x = xScale(i);
				const y = yScale(d.value);
				return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
			})
			.join(' ');
	});

	const areaPath = $derived(() => {
		if (data.length === 0) return '';

		const line = data.map((d, i) => {
			const x = xScale(i);
			const y = yScale(d.value);
			return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
		});

		// Close the path to the bottom
		const lastX = xScale(data.length - 1);
		const firstX = xScale(0);
		const bottomY = padding.top + chartHeight;

		return `${line.join(' ')} L ${lastX} ${bottomY} L ${firstX} ${bottomY} Z`;
	});

	// Y-axis ticks
	const yTicks = $derived(() => {
		const tickCount = 5;
		const ticks = [];
		for (let i = 0; i <= tickCount; i++) {
			const value = minValue + ((maxValue - minValue) * i) / tickCount;
			ticks.push({
				value: Math.round(value),
				y: yScale(value)
			});
		}
		return ticks;
	});

	// X-axis ticks (show every 7th day)
	const xTicks = $derived(() => {
		const ticks = [];
		const step = Math.max(1, Math.floor(data.length / 5));
		for (let i = 0; i < data.length; i += step) {
			ticks.push({
				label: formatDate(data[i].date),
				x: xScale(i)
			});
		}
		return ticks;
	});

	function formatDate(dateStr: string): string {
		const date = new Date(dateStr);
		return `${date.getMonth() + 1}/${date.getDate()}`;
	}

	function formatNumber(num: number): string {
		if (num >= 1000) {
			return (num / 1000).toFixed(1) + 'k';
		}
		return num.toString();
	}
</script>

<div class="w-full overflow-x-auto">
	<svg viewBox="0 0 {width} {height}" class="w-full h-64" preserveAspectRatio="xMidYMid meet">
		<!-- Grid lines -->
		{#each yTicks() as tick}
			<line
				x1={padding.left}
				y1={tick.y}
				x2={width - padding.right}
				y2={tick.y}
				stroke="hsl(var(--border))"
				stroke-dasharray="4"
			/>
		{/each}

		<!-- Area under the line -->
		<path d={areaPath()} fill="hsl(var(--primary) / 0.1)" />

		<!-- Line -->
		<path d={linePath()} fill="none" stroke="hsl(var(--primary))" stroke-width="2" />

		<!-- Data points -->
		{#each data as d, i}
			<circle
				cx={xScale(i)}
				cy={yScale(d.value)}
				r="3"
				fill="hsl(var(--primary))"
				class="transition-all hover:r-[5px]"
			>
				<title>{d.date}: {d.value}</title>
			</circle>
		{/each}

		<!-- Y-axis -->
		<line
			x1={padding.left}
			y1={padding.top}
			x2={padding.left}
			y2={padding.top + chartHeight}
			stroke="hsl(var(--border))"
		/>

		<!-- Y-axis labels -->
		{#each yTicks() as tick}
			<text
				x={padding.left - 5}
				y={tick.y}
				text-anchor="end"
				dominant-baseline="middle"
				class="text-[10px] fill-muted-foreground"
			>
				{formatNumber(tick.value)}
			</text>
		{/each}

		<!-- X-axis -->
		<line
			x1={padding.left}
			y1={padding.top + chartHeight}
			x2={width - padding.right}
			y2={padding.top + chartHeight}
			stroke="hsl(var(--border))"
		/>

		<!-- X-axis labels -->
		{#each xTicks() as tick}
			<text
				x={tick.x}
				y={padding.top + chartHeight + 15}
				text-anchor="middle"
				class="text-[10px] fill-muted-foreground"
			>
				{tick.label}
			</text>
		{/each}
	</svg>
</div>
