# Frontend Instructions (SvelteKit + Svelte 5)

## Tech Stack
- SvelteKit 2.x + Svelte 5 (Runes)
- TypeScript (strict)
- Tailwind CSS v4
- shadcn-svelte
- Paraglide.js (i18n)

## CRITICAL: Svelte 5 Runes Syntax

**NEVER use Svelte 4 syntax!**

| ❌ Svelte 4 | ✅ Svelte 5 |
|-------------|-------------|
| `let count = 0` | `let count = $state(0)` |
| `$: doubled = count * 2` | `let doubled = $derived(count * 2)` |
| `$: { ... }` | `$effect(() => { ... })` |
| `export let name` | `let { name } = $props()` |
| `<slot />` | `{@render children()}` |
| `createEventDispatcher` | Callback props |

## Component Template

```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { Button } from '$lib/components/ui/button';
  
  // Props
  let { title, children, onClose } = $props<{
    title: string;
    children: Snippet;
    onClose?: () => void;
  }>();
  
  // State
  let isOpen = $state(true);
  
  // Derived
  let displayTitle = $derived(title.toUpperCase());
  
  // Effect
  $effect(() => {
    if (!isOpen && onClose) onClose();
  });
</script>

{#if isOpen}
  <div class="card">
    <h2>{displayTitle}</h2>
    {@render children()}
    <Button onclick={() => isOpen = false}>Close</Button>
  </div>
{/if}
```

## Project Structure

| Location | Purpose |
|----------|---------|
| `src/routes/` | Pages and layouts |
| `src/lib/components/ui/` | shadcn-svelte components |
| `src/lib/components/custom/` | Business components |
| `src/lib/api/` | API client functions |
| `src/lib/stores/` | Svelte stores |
| `src/lib/types/` | TypeScript interfaces |

## i18n (Paraglide)

```svelte
<script lang="ts">
  import * as m from '$lib/paraglide/messages';
</script>

<Button>{m.common_save()}</Button>
```

## Commands

```bash
npm install       # Install
npm run dev       # Dev server
npm run build     # Build
npm run check     # Type check
```
