<script lang="ts">
	interface Props {
		size?: number;
		tone?: 'default' | 'accent';
	}

	let { size = 28, tone = 'default' }: Props = $props();
</script>

<div class={['spinner', tone === 'accent' ? 'spinner--accent' : ''].join(' ')} style={`--spinner-size: ${size}px;`}></div>

<style>
	.spinner {
		width: var(--spinner-size, 28px);
		height: var(--spinner-size, 28px);
		border: 3px solid rgba(0, 0, 0, 0.08);
		border-top-color: var(--link-color);
		border-radius: 999px;
		animation: spin 0.8s linear infinite;
	}

	.spinner--accent {
		border-top-color: var(--accent);
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
