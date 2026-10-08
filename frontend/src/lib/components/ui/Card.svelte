<script lang="ts">
	interface Props {
		padding?: 'none' | 'sm' | 'md' | 'lg';
		interactive?: boolean;
		bordered?: boolean;
		stackGap?: string;
		class?: string;
		children?: () => any;
	}

	let {
		padding = 'md',
		interactive = false,
		bordered = true,
		stackGap = '0',
		class: className = '',
		children
	}: Props = $props();
</script>

<div
	class={[
		'ui-card',
		`ui-card--padding-${padding}`,
		interactive ? 'ui-card--interactive' : '',
		bordered ? 'ui-card--bordered' : 'ui-card--no-border',
		className
	]
		.filter(Boolean)
		.join(' ')}
	style={`--ui-card-gap: ${stackGap};`}
>
	{@render children?.()}
</div>

<style>
	.ui-card {
		background: var(--bg-primary);
		border-radius: 1rem;
		box-shadow: 0 12px 26px var(--shadow);
		border: 1px solid transparent;
		display: flex;
		flex-direction: column;
		gap: var(--ui-card-gap, 0);
	}

	.ui-card--bordered {
		border-color: var(--border-color);
	}

	.ui-card--no-border {
		border-color: transparent;
	}

	.ui-card--interactive {
		transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease;
		cursor: pointer;
	}

	.ui-card--interactive:hover {
		transform: translateY(-2px);
		border-color: var(--border-hover);
		box-shadow: 0 16px 34px var(--shadow-hover);
	}

	.ui-card--padding-none {
		padding: 0;
	}

	.ui-card--padding-sm {
		padding: 0.75rem;
	}

	.ui-card--padding-md {
		padding: 1rem;
	}

	.ui-card--padding-lg {
		padding: 1.5rem;
	}
</style>
