<script lang="ts">
	interface Props {
		title: string;
		subtitle?: string;
		badge?: string;
		actionLabel?: string;
		actionIcon?: 'plus' | null;
		onAction?: () => void;
	}

	let {
		title,
		subtitle,
		badge,
		actionLabel,
		actionIcon = 'plus',
		onAction
	}: Props = $props();
</script>

<header class="page-header">
	<div class="page-header__text">
		<div class="page-header__headline">
			<h1>{title}</h1>
			{#if badge}
				<span class="page-header__badge">{badge}</span>
			{/if}
		</div>
		{#if subtitle}
			<p>{subtitle}</p>
		{/if}
	</div>
	<div class="page-header__actions">
		{#if actionLabel && onAction}
			<button class="page-header__button" type="button" onclick={onAction}>
				{#if actionIcon === 'plus'}
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<line x1="12" y1="5" x2="12" y2="19" />
						<line x1="5" y1="12" x2="19" y2="12" />
					</svg>
				{/if}
				<span>{actionLabel}</span>
			</button>
		{/if}
	</div>
</header>

<style>
	.page-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		padding: 1rem 2rem;
		border-radius: 1rem;
		background: var(--bg-primary);
		border: 1px solid var(--border-color);
		box-shadow: 0 10px 22px var(--shadow);
	}

	.page-header__text {
		flex: 1;
		min-width: 0;
	}

	.page-header__headline {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.page-header h1 {
		margin: 0;
		font-size: 1.4rem;
		font-weight: 800;
		color: var(--text-primary);
		letter-spacing: -0.02em;
	}

	.page-header__badge {
		padding: 0.2rem 0.65rem;
		border-radius: 999px;
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		font-weight: 700;
		background: rgba(0, 0, 0, 0.04);
		color: var(--text-secondary);
		border: 1px solid var(--border-color);
	}

	.page-header p {
		margin: 0.3rem 0 0;
		color: var(--text-secondary);
		font-size: 0.85rem;
	}

	.page-header__actions {
		display: flex;
		flex-wrap: wrap;
		justify-content: flex-end;
		gap: 0.4rem;
	}

	.page-header__button {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.6rem 1rem;
		border-radius: 0.85rem;
		border: 1px solid var(--border-color);
		background: var(--link-color);
		color: var(--text-inverse);
		font-size: 0.8rem;
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		cursor: pointer;
		box-shadow: 0 10px 24px var(--shadow);
		transition: transform 0.18s ease, box-shadow 0.18s ease;
	}

	.page-header__button:hover {
		transform: translateY(-1px);
		box-shadow: 0 14px 32px var(--shadow-hover);
	}

	.page-header__button svg {
		flex-shrink: 0;
	}

	@media (max-width: 768px) {
		.page-header {
			flex-direction: column;
			align-items: flex-start;
		}

		.page-header__actions {
			width: 100%;
			justify-content: flex-start;
		}
	}
</style>
