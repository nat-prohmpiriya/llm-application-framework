# Frontend Instructions

> **Full documentation**: See `CLAUDE.full.md` or `../.claude/frontend.md`

## Tech Stack
SvelteKit 2.x + Svelte 5 (Runes) + TypeScript + Tailwind v4 + shadcn-svelte

## CRITICAL: Svelte 5 Runes

| ❌ Wrong (Svelte 4) | ✅ Correct (Svelte 5) |
|---------------------|----------------------|
| `let count = 0` | `let count = $state(0)` |
| `$: doubled = count * 2` | `let doubled = $derived(count * 2)` |
| `export let name` | `let { name } = $props()` |
| `<slot />` | `{@render children()}` |

## Quick Template

```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';
  
  let { title, children } = $props<{
    title: string;
    children: Snippet;
  }>();
  
  let count = $state(0);
  let doubled = $derived(count * 2);
</script>

<h1>{title}</h1>
{@render children()}
```

## Structure

| Location | Purpose |
|----------|---------|
| `src/routes/` | Pages |
| `src/lib/components/ui/` | shadcn-svelte |
| `src/lib/components/custom/` | Business components |
| `src/lib/api/` | API client |

## Commands

```bash
npm run dev     # Dev server
npm run build   # Build
npm run check   # Type check
```
