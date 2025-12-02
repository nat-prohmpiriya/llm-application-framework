<script lang="ts">
	import { goto } from '$app/navigation';
	import { AppLayout } from '$lib/components/custom';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { auth } from '$lib/stores';
	import { getUserDisplayName } from '$lib/types';

	// Mock data for demo
	const mockProjects = [
		{ id: '1', name: 'Research Project' },
		{ id: '2', name: 'HR Documents' },
	];

	let currentProject = $state(mockProjects[0]);

	function handleLogout() {
		auth.logout();
		goto('/login');
	}

	function handleNewProject() {
		// TODO: Implement new project dialog
		console.log('New project');
	}

	function handleProjectSelect(projectId: string) {
		const project = mockProjects.find((p) => p.id === projectId);
		if (project) {
			currentProject = project;
		}
	}
</script>

<svelte:head>
	<title>RAG Agent Platform</title>
</svelte:head>

{#if auth.isLoading}
	<div class="min-h-screen flex items-center justify-center bg-background">
		<div class="flex flex-col items-center gap-4">
			<svg class="h-8 w-8 animate-spin text-primary" viewBox="0 0 24 24">
				<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
				<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
			</svg>
			<p class="text-muted-foreground">Loading...</p>
		</div>
	</div>
{:else if auth.isAuthenticated}
	<AppLayout
		user={auth.user ? { name: getUserDisplayName(auth.user), email: auth.user.email } : null}
		{currentProject}
		projects={mockProjects}
		onLogout={handleLogout}
		onNewProject={handleNewProject}
		onProjectSelect={handleProjectSelect}
	>
		<div class="space-y-6">
			<div>
				<h1 class="text-3xl font-bold">Welcome back, {auth.user ? getUserDisplayName(auth.user) : ''}!</h1>
				<p class="text-muted-foreground mt-2">
					Start chatting with your documents or manage your projects.
				</p>
			</div>

			<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
				<Card.Root class="hover:border-primary/50 transition-colors cursor-pointer">
					<Card.Header>
						<Card.Title class="flex items-center gap-2">
							<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
							</svg>
							Start Chat
						</Card.Title>
						<Card.Description>
							Chat with AI using your documents
						</Card.Description>
					</Card.Header>
					<Card.Content>
						<Button class="w-full" href="/chat">Open Chat</Button>
					</Card.Content>
				</Card.Root>

				<Card.Root class="hover:border-primary/50 transition-colors cursor-pointer">
					<Card.Header>
						<Card.Title class="flex items-center gap-2">
							<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
							</svg>
							Documents
						</Card.Title>
						<Card.Description>
							Upload and manage your documents
						</Card.Description>
					</Card.Header>
					<Card.Content>
						<Button variant="outline" class="w-full" href="/documents">Manage Documents</Button>
					</Card.Content>
				</Card.Root>

				<Card.Root class="hover:border-primary/50 transition-colors cursor-pointer">
					<Card.Header>
						<Card.Title class="flex items-center gap-2">
							<svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
							</svg>
							SQL Query
						</Card.Title>
						<Card.Description>
							Query your database with natural language
						</Card.Description>
					</Card.Header>
					<Card.Content>
						<Button variant="outline" class="w-full" href="/sql">Query Database</Button>
					</Card.Content>
				</Card.Root>
			</div>

			<Card.Root>
				<Card.Header>
					<Card.Title>Recent Conversations</Card.Title>
					<Card.Description>Continue where you left off</Card.Description>
				</Card.Header>
				<Card.Content>
					<p class="text-sm text-muted-foreground py-8 text-center">
						No recent conversations. Start a new chat to begin!
					</p>
				</Card.Content>
			</Card.Root>
		</div>
	</AppLayout>
{:else}
	<!-- Landing page for non-authenticated users -->
	<div class="min-h-screen bg-background">
		<header class="border-b">
			<div class="container mx-auto px-4 py-4 flex items-center justify-between">
				<div class="flex items-center gap-2">
					<svg class="h-6 w-6 text-primary" viewBox="0 0 24 24" fill="currentColor">
						<path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" stroke-width="2" fill="none"/>
					</svg>
					<span class="font-semibold">RAG Agent Platform</span>
				</div>
				<div class="flex items-center gap-2">
					<Button variant="ghost" href="/login">Login</Button>
					<Button href="/register">Get Started</Button>
				</div>
			</div>
		</header>

		<main class="container mx-auto px-4 py-16">
			<div class="max-w-3xl mx-auto text-center space-y-8">
				<h1 class="text-4xl md:text-6xl font-bold tracking-tight">
					AI-Powered Document Intelligence
				</h1>
				<p class="text-xl text-muted-foreground">
					Chat with your documents, query databases naturally, and let AI agents
					handle complex tasks - all with enterprise-grade privacy protection.
				</p>
				<div class="flex justify-center gap-4">
					<Button size="lg" href="/register">Start Free Trial</Button>
					<Button size="lg" variant="outline" href="/login">Sign In</Button>
				</div>
			</div>

			<div class="mt-24 grid gap-8 md:grid-cols-3">
				<Card.Root>
					<Card.Header>
						<Card.Title>RAG-Powered Chat</Card.Title>
					</Card.Header>
					<Card.Content>
						<p class="text-muted-foreground">
							Upload documents and ask questions. Get accurate answers with source citations.
						</p>
					</Card.Content>
				</Card.Root>

				<Card.Root>
					<Card.Header>
						<Card.Title>Text-to-SQL</Card.Title>
					</Card.Header>
					<Card.Content>
						<p class="text-muted-foreground">
							Query your databases using natural language. Review SQL before execution.
						</p>
					</Card.Content>
				</Card.Root>

				<Card.Root>
					<Card.Header>
						<Card.Title>Privacy First</Card.Title>
					</Card.Header>
					<Card.Content>
						<p class="text-muted-foreground">
							Built-in PII protection ensures sensitive data never leaves your control.
						</p>
					</Card.Content>
				</Card.Root>
			</div>
		</main>
	</div>
{/if}
