<script lang="ts">
	interface Props {
		open: boolean;
		onClose: () => void;
		title?: string;
		width?: 'default' | 'wide';
		children?: () => any;
	}

	let { open, onClose, title, width = 'default', children }: Props = $props();

	function handleBackgroundClick(event: MouseEvent) {
		if (event.target === event.currentTarget) {
			onClose();
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			onClose();
		}
	}

	function stopPropagation(event: MouseEvent) {
		event.stopPropagation();
	}
</script>

{#if open}
	<div class="modal" role="dialog" aria-modal="true" onkeydown={handleKeydown} tabindex="-1">
		<div class="modal__overlay" role="presentation" tabindex="-1" onclick={handleBackgroundClick}>
			<div
				class={['modal__content', width === 'wide' ? 'modal__content--wide' : ''].join(' ')}
				role="presentation"
				onclick={stopPropagation}
			>
				<header class="modal__header">
					{#if title}
						<h2>{title}</h2>
					{/if}
					<button class="modal__close" type="button" aria-label="Close" onclick={onClose}>
						×
					</button>
				</header>
				<div class="modal__body">
					{@render children?.()}
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	.modal {
		position: fixed;
		inset: 0;
		z-index: 2000;
	}

	.modal__overlay {
		position: absolute;
		inset: 0;
		background: rgba(8, 10, 15, 0.6);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 1.5rem;
		backdrop-filter: blur(10px);
	}

	.modal__content {
		width: min(640px, 95vw);
		max-height: 90vh;
		background: var(--bg-secondary);
		border-radius: 1.25rem;
		box-shadow: 0 28px 60px rgba(0, 0, 0, 0.35);
		border: 1px solid var(--border-color);
		overflow: hidden;
		display: flex;
		flex-direction: column;
	}

	.modal__content--wide {
		width: min(880px, 95vw);
	}

	.modal__header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem 1.25rem;
		border-bottom: 1px solid var(--border-color);
		background: var(--bg-primary);
	}

	.modal__header h2 {
		margin: 0;
		font-size: 1.1rem;
		color: var(--text-primary);
	}

	.modal__close {
		border: none;
		background: var(--bg-secondary);
		color: var(--text-secondary);
		border-radius: 0.75rem;
		width: 2.25rem;
		height: 2.25rem;
		cursor: pointer;
		font-size: 1.4rem;
		line-height: 1;
	}

	.modal__body {
		padding: 1.25rem;
		overflow-y: auto;
	}
</style>
