<script lang="ts">
	type Variant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'subtle' | 'danger';
	type Size = 'sm' | 'md' | 'lg';
	type ButtonType = 'button' | 'submit' | 'reset';

	interface Props {
		variant?: Variant;
		size?: Size;
		fullWidth?: boolean;
		loading?: boolean;
		iconOnly?: boolean;
		href?: string;
		isExternal?: boolean;
		type?: ButtonType;
		disabled?: boolean;
		onclick?: (event: MouseEvent) => void;
		children?: () => any;
	}

	let {
		variant = 'primary',
		size = 'md',
		fullWidth = false,
		loading = false,
		iconOnly = false,
		href,
		isExternal = false,
		type = 'button',
		disabled = false,
		onclick,
		children
	}: Props = $props();

	const Tag = $derived(href ? 'a' : 'button');
	const isButton = $derived(Tag === 'button');
</script>

<svelte:element
	this={Tag}
	class={['ui-button', `ui-button--${variant}`, `ui-button--${size}`, fullWidth ? 'ui-button--full' : '', iconOnly ? 'ui-button--icon' : '']
		.filter(Boolean)
		.join(' ')}
	href={href}
	type={isButton ? type : undefined}
	disabled={isButton ? disabled || loading : undefined}
	aria-busy={loading}
	onclick={onclick}
	{...(Tag === 'a' && isExternal ? { target: '_blank', rel: 'noreferrer noopener' } : {})}
>
	{#if loading}
		<span class="ui-button__spinner"></span>
	{/if}
	<span class="ui-button__content">
		{@render children?.()}
	</span>
</svelte:element>

<style>
	.ui-button {
		--btn-bg: var(--accent);
		--btn-color: var(--text-inverse);
		--btn-border: var(--accent);
		--btn-bg-hover: var(--accent-hover);
		--btn-color-hover: var(--text-inverse);
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.45rem;
		border-radius: 0.75rem;
		font-weight: 700;
		font-size: 0.88rem;
		letter-spacing: 0.05em;
		text-transform: uppercase;
		padding: 0.55rem 1.1rem;
		border: 1px solid var(--btn-border);
		background: var(--btn-bg);
		color: var(--btn-color);
		cursor: pointer;
		transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease, color 0.18s ease, border-color 0.18s ease;
		text-decoration: none;
		box-shadow: 0 10px 20px var(--shadow);
	}

	.ui-button:hover:not([disabled]) {
		transform: translateY(-1px);
		background: var(--btn-bg-hover);
		color: var(--btn-color-hover);
	}

	.ui-button:active:not([disabled]) {
		transform: translateY(0);
	}

	.ui-button:disabled,
	.ui-button[aria-busy='true'] {
		opacity: 0.7;
		cursor: not-allowed;
	}

	.ui-button--full {
		width: 100%;
	}

	.ui-button--icon {
		padding-inline: 0.75rem;
	}

	.ui-button--sm {
		padding: 0.4rem 0.9rem;
		font-size: 0.75rem;
	}

	.ui-button--lg {
		padding: 0.7rem 1.4rem;
		font-size: 0.92rem;
	}

	.ui-button--secondary {
		--btn-bg: var(--link-color);
		--btn-border: var(--link-color);
		--btn-bg-hover: var(--link-hover);
	}

	.ui-button--outline {
		--btn-bg: transparent;
		--btn-color: var(--text-primary);
		--btn-border: var(--border-color);
		--btn-bg-hover: var(--bg-hover);
		--btn-color-hover: var(--text-primary);
		box-shadow: none;
	}

	.ui-button--ghost {
		--btn-bg: transparent;
		--btn-color: var(--text-secondary);
		--btn-border: transparent;
		--btn-bg-hover: rgba(0, 0, 0, 0.05);
		--btn-color-hover: var(--text-primary);
		box-shadow: none;
	}

	.ui-button--subtle {
		--btn-bg: var(--bg-secondary);
		--btn-color: var(--text-primary);
		--btn-border: var(--border-color);
		--btn-bg-hover: var(--bg-hover);
	}

	.ui-button--danger {
		--btn-bg: rgba(228, 87, 46, 0.12);
		--btn-color: var(--accent);
		--btn-border: rgba(228, 87, 46, 0.4);
		--btn-bg-hover: rgba(228, 87, 46, 0.2);
		box-shadow: none;
	}

	.ui-button__spinner {
		width: 1rem;
		height: 1rem;
		border: 2px solid rgba(255, 255, 255, 0.4);
		border-top-color: currentColor;
		border-radius: 999px;
		animation: spin 0.8s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
