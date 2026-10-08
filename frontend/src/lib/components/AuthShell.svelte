<script lang="ts">
	interface Props {
		title: string;
		subtitle?: string;
		children?: () => any;
	}

	let { title, subtitle, children }: Props = $props();
</script>

<div class="auth-shell">
	<div class="auth-card surface-panel">
		<header class="auth-card__header">
			<h1>{title}</h1>
			{#if subtitle}
				<p>{subtitle}</p>
			{/if}
		</header>
		{@render children?.()}
	</div>
</div>

<style>
	.auth-shell {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem 1rem;
	}

	.auth-card {
		width: min(460px, 100%);
		background: var(--bg-primary);
		border-radius: 1.5rem;
		box-shadow: 0 24px 48px var(--shadow);
	}

	.auth-card__header {
		margin-bottom: 1.5rem;
		text-align: center;
	}

	.auth-card__header h1 {
		margin: 0;
		font-size: 1.8rem;
		letter-spacing: -0.02em;
	}

	.auth-card__header p {
		margin: 0.4rem 0 0;
		color: var(--text-secondary);
	}
</style>
