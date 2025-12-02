---
applyTo: "**/*.svelte"
---

# Svelte 5 Component Instructions

## CRITICAL: Use Svelte 5 Runes

**You MUST use Svelte 5 Runes syntax**, NOT legacy Svelte 4 syntax.

## Quick Reference

### State
```svelte
<script lang="ts">
  // ❌ Wrong (Svelte 4)
  let count = 0;
  
  // ✅ Correct (Svelte 5)
  let count = $state(0);
</script>
```

### Derived Values
```svelte
<script lang="ts">
  // ❌ Wrong (Svelte 4)
  $: doubled = count * 2;
  
  // ✅ Correct (Svelte 5)
  let doubled = $derived(count * 2);
</script>
```

### Effects
```svelte
<script lang="ts">
  // ❌ Wrong (Svelte 4)
  $: {
    console.log(count);
  }
  
  // ✅ Correct (Svelte 5)
  $effect(() => {
    console.log(count);
  });
</script>
```

### Props
```svelte
<script lang="ts">
  // ❌ Wrong (Svelte 4)
  export let name: string;
  export let onClick: () => void;
  
  // ✅ Correct (Svelte 5)
  let { name, onClick } = $props<{
    name: string;
    onClick: () => void;
  }>();
</script>
```

### Events
```svelte
<script lang="ts">
  // ❌ Wrong (Svelte 4)
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();
  dispatch('submit', data);
  
  // ✅ Correct (Svelte 5) - Use callback props
  let { onSubmit } = $props<{
    onSubmit: (data: Data) => void;
  }>();
  onSubmit(data);
</script>
```

### Slots → Snippets
```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';
  
  // ❌ Wrong (Svelte 4)
  // <slot />
  // <slot name="header" />
  
  // ✅ Correct (Svelte 5)
  let { children, header } = $props<{
    children: Snippet;
    header?: Snippet;
  }>();
</script>

<!-- ❌ Wrong -->
<slot />

<!-- ✅ Correct -->
{@render children()}
{#if header}
  {@render header()}
{/if}
```

## Complete Component Template

```svelte
<script lang="ts">
  import type { Snippet } from 'svelte';
  import { Button } from '$lib/components/ui/button';
  
  // Props
  let { 
    title,
    children,
    onClose 
  } = $props<{
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
    if (!isOpen && onClose) {
      onClose();
    }
  });
  
  // Functions
  function handleClose() {
    isOpen = false;
  }
</script>

{#if isOpen}
  <div class="card">
    <h2>{displayTitle}</h2>
    {@render children()}
    <Button onclick={handleClose}>Close</Button>
  </div>
{/if}
```

## Using the Component

```svelte
<script lang="ts">
  import MyCard from './MyCard.svelte';
</script>

<MyCard title="Hello" onClose={() => console.log('closed')}>
  {#snippet children()}
    <p>Card content here</p>
  {/snippet}
</MyCard>

<!-- Or for simple children, just use regular content -->
<MyCard title="Hello">
  <p>Card content here</p>
</MyCard>
```
