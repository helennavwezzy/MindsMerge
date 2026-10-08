<script lang="ts">
	type Width = 'default' | 'narrow' | 'wide' | 'full';

	interface Props {
		width?: Width;
		padding?: 'none' | 'sm' | 'md';
		class?: string;
		children?: () => any;
	}

	let { width = 'default', padding = 'md', class: className = '', children }: Props = $props();
</script>

<div
	class={['page-container', `page-container--${width}`, `page-container--pad-${padding}`, className]
		.filter(Boolean)
		.join(' ')}
>
	{@render children?.()}
</div>

<style>
	.page-container {
		margin: 0 auto;
		width: 100%;
		box-sizing: border-box;
	}

	.page-container--default {
		max-width: 980px;
	}

	.page-container--narrow {
		max-width: 840px;
	}

	.page-container--wide {
		max-width: 1100px;
	}

	.page-container--full {
		max-width: none;
	}

	.page-container--pad-none {
		padding: 0;
	}

	.page-container--pad-sm {
		padding: 0 1rem;
	}

	.page-container--pad-md {
		padding: 0 1.25rem;
	}

	@media (max-width: 768px) {
		.page-container--pad-md,
		.page-container--pad-sm {
			padding: 0 1rem;
		}
	}
</style>
