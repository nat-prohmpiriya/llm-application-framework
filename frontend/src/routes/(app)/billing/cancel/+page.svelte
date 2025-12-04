<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { XCircle, ArrowLeft, HelpCircle, MessageSquare } from 'lucide-svelte';
</script>

<svelte:head>
	<title>Payment Cancelled - RAG Agent Platform</title>
</svelte:head>

<div class="min-h-[80vh] flex items-center justify-center p-4">
	<Card.Root class="w-full max-w-md">
		<Card.Content class="pt-8 pb-8 text-center">
			<div class="flex flex-col items-center gap-6">
				<!-- Cancel Icon -->
				<div class="h-20 w-20 rounded-full bg-muted flex items-center justify-center">
					<XCircle class="h-10 w-10 text-muted-foreground" />
				</div>

				<!-- Cancel Message -->
				<div>
					<h2 class="text-2xl font-bold text-foreground">Payment Cancelled</h2>
					<p class="text-muted-foreground mt-2">
						Your payment was cancelled. No charges have been made to your account.
					</p>
				</div>

				<!-- Help Section -->
				<div class="w-full p-4 rounded-lg bg-muted/50 text-left">
					<h3 class="font-medium mb-2 flex items-center gap-2">
						<HelpCircle class="h-4 w-4" />
						Need help?
					</h3>
					<p class="text-sm text-muted-foreground">
						If you encountered any issues during checkout or have questions about our plans, we're here to help.
					</p>
				</div>

				<!-- Action Buttons -->
				<div class="flex flex-col sm:flex-row gap-3 w-full">
					<Button href="/pricing" variant="default" class="flex-1">
						<ArrowLeft class="h-4 w-4 mr-2" />
						Back to Pricing
					</Button>
					<Button href="/contact" variant="outline" class="flex-1">
						<MessageSquare class="h-4 w-4 mr-2" />
						Contact Support
					</Button>
				</div>

				<!-- Continue Free -->
				<p class="text-sm text-muted-foreground">
					You can continue using the
					<a href="/chat" class="text-primary hover:underline">free plan</a>
					with limited features.
				</p>
			</div>
		</Card.Content>
	</Card.Root>
</div>
