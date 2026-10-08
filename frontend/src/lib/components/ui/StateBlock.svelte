<script lang="ts">
	type Tone = 'default' | 'info' | 'error' | 'success';

	interface Props {
		icon?: 'chat' | 'info' | 'error' | 'empty' | 'spinner';
		title?: string;
		message?: string;
		tone?: Tone;
		size?: 'sm' | 'md' | 'lg';
		children?: () => any;
	}

	let {
		icon = 'info',
		title,
		message,
		tone = 'default',
		size = 'md',
		children
	}: Props = $props();
</script>

<div class={['state-block', `state-block--${tone}`, `state-block--${size}`].join(' ')}>
	<div class="state-block__icon">
		{#if icon === 'spinner'}
			<div class="state-block__spinner"></div>
		{:else if icon === 'chat'}
			<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
		{:else if icon === 'error'}
			<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" /></svg>
		{:else}
			<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10" /></svg>
		{/if}
	</div>
	<div class="state-block__text">
		{#if title}
			<h2>{title}</h2>
		{/if}
		{#if message}
			<p>{message}</p>
		{/if}
		{@render children?.()}
	</div>
</div>

<style>
	.state-block {
		border: 1px dashed var(--border-color);
		border-radius: 1rem;
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		gap: 0.75rem;
		color: var(--text-secondary);
		box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
	}

	.state-block--lg {
		padding: 3rem 1.5rem;
	}

	.state-block__icon {
		color: var(--text-tertiary);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.state-block__icon svg {
		width: 2.5rem;
		height: 2.5rem;
		stroke: currentColor;
		stroke-width: 1.5;
		fill: none;
	}

	.state-block__spinner {
		width: 2rem;
		height: 2rem;
		border-radius: 999px;
		border: 3px solid var(--border-color);
		border-top-color: var(--link-color);
		animation: spin 0.8s linear infinite;
	}

	.state-block h2 {
		margin: 0;
		font-size: 1.1rem;
		color: var(--text-primary);
	}

	.state-block p {
		margin: 0;
		font-size: 0.9rem;
	}

	.state-block--error {
		border-color: rgba(228, 87, 46, 0.4);
		color: var(--accent);
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
