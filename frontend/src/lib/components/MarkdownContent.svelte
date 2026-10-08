<script lang="ts">
	import { renderMarkdown } from '$lib/utils/markdown';
	import { sanitizeHtml } from '$lib/utils/sanitize';

	interface Props {
		content: string;
		class?: string;
	}

	let { content, class: className = '' }: Props = $props();
</script>

<div class="markdown-content {className}">
	{@html sanitizeHtml(renderMarkdown(content))}
</div>

<style>
	.markdown-content {
		color: var(--text-primary);
		line-height: 1.65;
		font-size: 15px;
	}

	.markdown-content :global(*) {
		color: var(--text-primary);
	}

	.markdown-content :global(h1),
	.markdown-content :global(h2),
	.markdown-content :global(h3) {
		color: var(--text-primary);
		margin-top: 16px;
		margin-bottom: 10px;
		font-weight: 800;
		letter-spacing: -0.01em;
	}

	.markdown-content :global(h1) {
		font-size: 22px;
	}

	.markdown-content :global(h2) {
		font-size: 19px;
	}

	.markdown-content :global(h3) {
		font-size: 17px;
	}

	.markdown-content :global(p) {
		margin: 0 0 14px 0;
	}

	.markdown-content :global(p:last-child) {
		margin-bottom: 0;
	}

	.markdown-content :global(a) {
		color: var(--link-color);
		text-decoration: none;
		border-bottom: 1px solid rgba(228, 87, 46, 0.35);
		padding-bottom: 2px;
	}

	.markdown-content :global(a:hover) {
		text-decoration: none;
		border-color: var(--link-hover);
	}

	.markdown-content :global(ul),
	.markdown-content :global(ol) {
		margin: 0 0 14px 0;
		padding-left: 26px;
	}

	.markdown-content :global(li) {
		margin-bottom: 6px;
	}

	.markdown-content :global(code) {
		background-color: var(--bg-tertiary);
		padding: 3px 7px;
		border-radius: 8px;
		font-family: var(--font-mono);
		font-size: 13px;
		box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
	}

	.markdown-content :global(pre) {
		background-color: var(--bg-tertiary);
		padding: 14px;
		border-radius: 12px;
		overflow-x: auto;
		margin: 14px 0;
		border: 1px solid var(--border-color);
	}

	.markdown-content :global(pre code) {
		background-color: transparent;
		padding: 0;
		display: block;
		overflow-x: auto;
	}

	.markdown-content :global(blockquote) {
		border-left: 3px solid var(--link-color);
		padding-left: 14px;
		margin: 14px 0;
		color: var(--text-secondary);
		background: rgba(0, 0, 0, 0.02);
		border-radius: 8px;
	}

	.markdown-content :global(img) {
		max-width: 100%;
		height: auto;
		border-radius: 12px;
		margin: 12px 0;
		box-shadow: 0 10px 24px var(--shadow);
	}

	.markdown-content :global(iframe) {
		max-width: 100%;
		width: 100%;
		height: 315px;
		border-radius: 14px;
		margin: 16px 0;
		border: 1px solid var(--border-color);
		box-shadow: 0 12px 26px var(--shadow);
	}

	@media (min-width: 640px) {
		.markdown-content :global(iframe) {
			height: 400px;
		}
	}

</style>
