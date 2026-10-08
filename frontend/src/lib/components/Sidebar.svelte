<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { fetchTopics } from '$lib/api/topics';
	import type { Topic } from '$lib/types';
	import { ApiError } from '$lib/api/client';

	let topics = $state<Topic[]>([]);
	let error = $state<string | null>(null);
	let currentTopic = $derived(() => {
		const path = $page.url.pathname;
		if (path.startsWith('/topic/')) {
			return path.split('/topic/')[1].toLowerCase();
		}
		return null;
	});

	onMount(async () => {
		try {
			topics = await fetchTopics();
		} catch (err) {
			if (err instanceof ApiError) {
				error = err.message;
			} else {
				error = 'Failed to load topics';
			}
		}
	});
</script>

<aside class="sidebar">
	<div class="sidebar-header">
		<h2 class="sidebar-title">Communities</h2>
	</div>
	<div class="topic-list">
		{#if error}
			<p class="topic-error">{error}</p>
		{:else}
			{#each topics.filter((t) => t.name !== 'All') as topic}
				<a
					href="/topic/{topic.name.toLowerCase()}"
					class="topic-item"
					class:active={currentTopic() === topic.name.toLowerCase()}
				>
					<span class="topic-icon">r/</span>
					<span class="topic-name">{topic.name}</span>
				</a>
			{/each}
		{/if}
	</div>
	<div class="sidebar-footer">
		<button type="button" class="footer-link" onclick={(e) => { e.preventDefault(); }}>General</button>
		<span class="footer-separator">/</span>
		<span class="footer-link disabled">Testing</span>
	</div>
</aside>

<style>
	.sidebar {
		position: fixed;
		left: 0;
		top: var(--topbar-height);
		width: 260px;
		height: calc(100vh - var(--topbar-height));
		background: var(--bg-primary);
		border-right: 1px solid var(--border-color);
		padding: 16px 12px;
		overflow-y: auto;
		overflow-x: hidden;
		z-index: 100;
		box-shadow: 8px 0 24px var(--shadow);
		display: flex;
		flex-direction: column;
		box-sizing: border-box;
		backdrop-filter: blur(10px);
	}

	.sidebar-header {
		padding: 0 6px 12px 6px;
		margin-bottom: 8px;
		border-bottom: 1px solid var(--border-color);
		position: relative;
	}

	.sidebar-header::after {
		content: '';
		position: absolute;
		left: 6px;
		right: 6px;
		bottom: -1px;
		height: 1px;
		background: linear-gradient(90deg, rgba(228, 87, 46, 0), rgba(228, 87, 46, 0.5), rgba(228, 87, 46, 0));
	}

	.sidebar-title {
		margin: 0;
		font-size: 12px;
		font-weight: 800;
		color: var(--text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.3em;
	}

	.topic-list {
		display: flex;
		flex-direction: column;
		gap: 4px;
		flex: 1;
		overflow-y: auto;
		overflow-x: hidden;
		min-width: 0;
		padding: 2px 0 6px;
	}

	.topic-item {
		display: flex;
		align-items: center;
		gap: 8px;
		width: 100%;
		padding: 8px 10px;
		background: transparent;
		text-align: left;
		cursor: pointer;
		border-radius: 8px;
		color: var(--text-primary);
		font-size: 14px;
		font-weight: 600;
		transition: all 0.18s ease;
		text-decoration: none;
		box-sizing: border-box;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		border: 1px solid transparent;
		position: relative;
	}

	.topic-item:hover {
		transform: translateY(-1px);
	}

	.topic-item:hover .topic-name {
		text-decoration-line: underline;
	}

	.topic-item:hover::before {
		opacity: 0.5;
	}

	.topic-error {
		padding: 0.75rem;
		border-radius: 0.75rem;
		background: rgba(228, 87, 46, 0.1);
		color: var(--accent);
		font-size: 0.85rem;
	}

	.topic-item.active {
		background: var(--bg-secondary);
		border-color: var(--link-color);
		box-shadow: none;
	}

	.topic-item.active::before {
		opacity: 1;
	}

	.topic-icon {
		font-weight: 800;
		color: var(--accent);
		font-size: 12px;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 28px;
		height: 28px;
		border-radius: 10px;
		background: var(--bg-secondary);
	}

	.sidebar-footer {
		display: flex;
		align-items: center;
		gap: 6px;
		padding: 12px 8px 0 8px;
		margin-top: auto;
		border-top: 1px dashed var(--border-color);
		font-size: 12px;
		color: var(--text-secondary);
		letter-spacing: 0.02em;
	}

	.footer-link {
		background: transparent;
		border: none;
		padding: 0;
		color: var(--link-color);
		text-decoration: none;
		cursor: pointer;
		transition: color 0.15s ease;
		font-family: inherit;
		font-size: inherit;
		font-weight: 700;
	}

	.footer-link:hover:not(.disabled) {
		color: var(--link-hover);
		text-decoration: underline;
	}

	.footer-link.disabled {
		color: var(--text-tertiary);
		cursor: default;
		opacity: 0.6;
	}

	.footer-separator {
		color: var(--text-tertiary);
	}

	@media (max-width: 1024px) {
		.sidebar {
			display: none;
		}
	}
</style>
