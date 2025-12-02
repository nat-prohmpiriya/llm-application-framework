---
applyTo: "frontend/**"
---

# Frontend Instructions (SvelteKit + Svelte 5)

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | SvelteKit 2.x |
| UI Library | Svelte 5 (Runes syntax) |
| Language | TypeScript (strict) |
| CSS | Tailwind CSS v4 |
| UI Components | shadcn-svelte |
| i18n | Paraglide.js |
| Build | Vite |

## CRITICAL: Svelte 5 Runes Syntax

**MUST use Svelte 5 Runes syntax** - NOT legacy Svelte 4 syntax!

| ❌ Legacy (Svelte 4) | ✅ Runes (Svelte 5) |
|---------------------|---------------------|
| `let count = 0` | `let count = $state(0)` |
| `$: doubled = count * 2` | `let doubled = $derived(count * 2)` |
| `$: { console.log(count) }` | `$effect(() => { console.log(count) })` |
| `export let name` | `let { name } = $props()` |
| `<slot />` | `{@render children()}` (Snippets) |
| `createEventDispatcher` | Callback props |

## State Management Example

```svelte
<script lang="ts">
  // Props with TypeScript
  let { title, onClick } = $props<{
    title: string;
    onClick?: () => void;
  }>();

  // Reactive state
  let count = $state(0);

  // Derived value
  let doubled = $derived(count * 2);

  // Side effect
  $effect(() => {
    console.log(`Count changed to ${count}`);
  });
</script>
```

## Component Events (Svelte 5 way)

```svelte
<script lang="ts">
  // Use callback props instead of createEventDispatcher
  let { onSubmit } = $props<{
    onSubmit: (data: FormData) => void;
  }>();
</script>

<button onclick={() => onSubmit(formData)}>Submit</button>
```

## Snippets (Replace slots)

**DO NOT use `<slot />`** - Use Snippets instead:

```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';

  let { children, header } = $props<{
    children: Snippet;
    header?: Snippet;
  }>();
</script>

<div class="card">
  {#if header}
    {@render header()}
  {/if}
  {@render children()}
</div>
```

## UI Components (shadcn-svelte)

Use components from `$lib/components/ui/`:

```svelte
<script lang="ts">
  import { Button } from '$lib/components/ui/button';
  import * as Card from '$lib/components/ui/card';
</script>

<Card.Root>
  <Card.Header>
    <Card.Title>Title</Card.Title>
  </Card.Header>
  <Card.Content>
    <p>Content here</p>
  </Card.Content>
  <Card.Footer>
    <Button variant="default">Save</Button>
  </Card.Footer>
</Card.Root>
```

## i18n (Paraglide)

```svelte
<script lang="ts">
  import * as m from '$lib/paraglide/messages';
</script>

<Button>{m.common_save()}</Button>
```

## Project Structure

| Location | Purpose |
|----------|---------|
| `src/routes/` | SvelteKit pages and layouts |
| `src/lib/components/ui/` | shadcn-svelte base components |
| `src/lib/components/custom/` | Business components (ChatWindow, etc.) |
| `src/lib/api/` | API client functions |
| `src/lib/stores/` | Svelte stores |
| `src/lib/types/` | TypeScript interfaces |

## File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `UserCard.svelte` |
| Routes | lowercase-with-hyphens | `user-profile/+page.svelte` |
| Utilities | camelCase | `formatDate.ts` |
| Types | PascalCase | `User.ts` |

## Component Structure Order

```svelte
<script lang="ts">
  // 1. Imports
  import { Button } from '$lib/components/ui/button';

  // 2. Props
  let { user, onSave } = $props<{ ... }>();

  // 3. State
  let isLoading = $state(false);

  // 4. Derived
  let fullName = $derived(`${user.firstName} ${user.lastName}`);

  // 5. Effects
  $effect(() => { ... });

  // 6. Functions
  function handleSubmit() { ... }
</script>

<!-- Template -->
<div class="container">...</div>

<!-- Styles (prefer Tailwind, use <style> only when necessary) -->
```

## Commands

```bash
cd frontend
npm install       # Install dependencies
npm run dev       # Run dev server
npm run build     # Build for production
npm run check     # Type check
npm run lint      # Lint code
```
