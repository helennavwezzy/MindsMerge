<script lang="ts">
	interface Props {
		label?: string;
		message?: string;
		for?: string;
		inline?: boolean;
		children?: () => any;
	}

	let { label, message, for: htmlFor, inline = false, children }: Props = $props();
</script>

<div class={['form-field', inline ? 'form-field--inline' : ''].join(' ')}>
	{#if label}
		<label for={htmlFor}>{label}</label>
	{/if}
	<div class="form-field__control">
		{@render children?.()}
	</div>
	{#if message}
		<p class="form-field__message">{message}</p>
	{/if}
</div>

<style>
	.form-field {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
	}

	.form-field--inline {
		flex-direction: row;
		align-items: center;
		gap: 0.75rem;
	}

	.form-field label {
		font-size: 0.85rem;
		font-weight: 700;
		color: var(--text-secondary);
		letter-spacing: 0.05em;
		text-transform: uppercase;
	}

	.form-field__message {
		margin: 0;
		font-size: 0.8rem;
		color: var(--text-tertiary);
	}
</style>
