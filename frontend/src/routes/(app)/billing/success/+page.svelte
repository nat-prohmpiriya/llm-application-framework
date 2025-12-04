<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { CheckCircle, ArrowRight, Loader2, Sparkles } from 'lucide-svelte';
	import confetti from 'canvas-confetti';

	let loading = $state(true);
	let sessionId = $state<string | null>(null);

	onMount(() => {
		// Get session_id from URL
		sessionId = $page.url.searchParams.get('session_id');

		// Simulate verification delay
		setTimeout(() => {
			loading = false;
			// Trigger confetti on success
			triggerConfetti();
		}, 1500);
	});

	function triggerConfetti() {
		const duration = 3000;
		const end = Date.now() + duration;

		const frame = () => {
			confetti({
				particleCount: 3,
				angle: 60,
				spread: 55,
				origin: { x: 0 },
				colors: ['#6366f1', '#8b5cf6', '#a855f7']
			});
			confetti({
				particleCount: 3,
				angle: 120,
				spread: 55,
				origin: { x: 1 },
				colors: ['#6366f1', '#8b5cf6', '#a855f7']
			});

			if (Date.now() < end) {
				requestAnimationFrame(frame);
			}
		};

		frame();
	}
</script>

<svelte:head>
	<title>Payment Successful - RAG Agent Platform</title>
</svelte:head>

<div class="min-h-[80vh] flex items-center justify-center p-4">
	<Card.Root class="w-full max-w-md">
		<Card.Content class="pt-8 pb-8 text-center">
			{#if loading}
				<div class="flex flex-col items-center gap-4">
					<div class="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
						<Loader2 class="h-8 w-8 text-primary animate-spin" />
					</div>
					<div>
						<h2 class="text-xl font-semibold">Processing your payment...</h2>
						<p class="text-muted-foreground mt-1">Please wait while we confirm your subscription</p>
					</div>
				</div>
			{:else}
				<div class="flex flex-col items-center gap-6">
					<!-- Success Icon -->
					<div class="relative">
						<div class="h-20 w-20 rounded-full bg-green-500/10 flex items-center justify-center">
							<CheckCircle class="h-10 w-10 text-green-500" />
						</div>
						<div class="absolute -top-1 -right-1">
							<Sparkles class="h-6 w-6 text-yellow-500" />
						</div>
					</div>

					<!-- Success Message -->
					<div>
						<h2 class="text-2xl font-bold text-foreground">Payment Successful!</h2>
						<p class="text-muted-foreground mt-2">
							Thank you for subscribing. Your account has been upgraded and you now have access to all premium features.
						</p>
					</div>

					<!-- What's Next -->
					<div class="w-full p-4 rounded-lg bg-muted/50 text-left">
						<h3 class="font-medium mb-2">What's next?</h3>
						<ul class="text-sm text-muted-foreground space-y-2">
							<li class="flex items-start gap-2">
								<CheckCircle class="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
								<span>Your subscription is now active</span>
							</li>
							<li class="flex items-start gap-2">
								<CheckCircle class="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
								<span>Access to premium AI models enabled</span>
							</li>
							<li class="flex items-start gap-2">
								<CheckCircle class="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
								<span>A confirmation email has been sent</span>
							</li>
						</ul>
					</div>

					<!-- Action Buttons -->
					<div class="flex flex-col sm:flex-row gap-3 w-full">
						<Button href="/chat" class="flex-1">
							Start Chatting
							<ArrowRight class="h-4 w-4 ml-2" />
						</Button>
						<Button href="/settings" variant="outline" class="flex-1">
							Manage Subscription
						</Button>
					</div>

					<!-- Session ID (for debugging) -->
					{#if sessionId}
						<p class="text-xs text-muted-foreground">
							Session: {sessionId.slice(0, 20)}...
						</p>
					{/if}
				</div>
			{/if}
		</Card.Content>
	</Card.Root>
</div>
