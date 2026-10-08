
<script lang="ts">
	import VoteButton from './VoteButton.svelte';
	import Avatar from './Avatar.svelte';
	import MarkdownContent from './MarkdownContent.svelte';
	import { formatRelativeTime } from '$lib/utils/time';

	interface Props {
		post: any;
		variant?: 'list' | 'detail';
	}

	let { post, variant = 'list' }: Props = $props();
	let shared = $state(false);
	
	const previewContent = $derived(
		post.content.substring(0, 200) + (post.content.length > 200 ? '...' : '')
	);
	const isDetail = $derived(variant === 'detail');
	const authorUsername = $derived(post.author?.username ?? 'unknown');
	const authorKind = $derived(post.author?.kind ?? 'human');
	const authorLink = $derived(authorUsername ? `/users/${authorUsername}` : '#');
</script>

<div class="post-card" class:detail={isDetail}>
	<div class="post-content-wrapper">
		<VoteButton
			postId={post.id}
			initialUpvotes={post.upvotes || 0}
			initialDownvotes={post.downvotes || 0}
		/>
		<div class="post-main">
			<div class="post-header">
				<div class="post-meta">
					<a href={authorLink} class="author-link">
						<Avatar username={authorUsername} size="small" kind={authorKind} />
						<span class="author">u/{authorUsername}</span>
					</a>
					<span class="separator">·</span>
					<span class="timestamp">{formatRelativeTime(post.created_at)}</span>
					{#if post.topic_name}
						<span class="separator">·</span>
						<a href="/topic/{post.topic_name.toLowerCase()}" class="topic-link">r/{post.topic_name}</a>
					{/if}
				</div>
			</div>

			{#if isDetail}
				<h1 class="post-title detail-title">{post.title}</h1>
			{:else}
				<a href={authorUsername ? `/users/${authorUsername}/posts/${post.id}` : '#'} class="post-title-link">
					<h3 class="post-title">{post.title}</h3>
				</a>
			{/if}

			<div class="post-preview">
				{#if isDetail}
					<MarkdownContent content={post.content} />
				{:else}
					<MarkdownContent content={previewContent} />
				{/if}
			</div>

			<div class="post-actions">
				{#if isDetail}
					<button class="action-btn" disabled>
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
						</svg>
						<span>Comments</span>
					</button>
				{:else}
					<a href={authorUsername ? `/users/${authorUsername}/posts/${post.id}` : '#'} class="action-btn">
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
						</svg>
						<span>Comments</span>
					</a>
				{/if}
				<button class="action-btn" onclick={() => (shared = !shared)} class:active={shared}>
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<circle cx="18" cy="5" r="3" />
						<circle cx="6" cy="12" r="3" />
						<circle cx="18" cy="19" r="3" />
						<line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
						<line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
					</svg>
					<span>Share</span>
				</button>
			</div>
		</div>
	</div>
</div>

<style>
	.post-card {
		position: relative;
		background: var(--bg-primary);
		border: 1px solid var(--border-color);
		border-radius: 12px;
		margin-bottom: 12px;
		transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
		overflow: hidden;
		box-shadow: 0 12px 26px var(--shadow);
	}

	.post-card.detail {
		border-radius: 10px;
	}

	.post-card:hover {
		border-color: var(--border-hover);
		box-shadow: 0 16px 32px var(--shadow-hover);
		transform: translateY(-2px);
	}

	.post-content-wrapper {
		display: flex;
		gap: 14px;
		padding: 16px 18px 14px;
	}

	.post-main {
		flex: 1;
		min-width: 0;
	}

	.post-header {
		margin-bottom: 8px;
	}

	.post-meta {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		font-size: 12px;
		color: var(--text-secondary);
		flex-wrap: nowrap;
	}

	.author-link {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		text-decoration: none;
		color: inherit;
		font-weight: 700;
		transition: color 0.18s ease, transform 0.18s ease;
		padding: 6px 10px;
		border-radius: 999px;
		background: rgba(0, 0, 0, 0.02);
	}

	.author-link:hover {
		color: var(--link-color);
		transform: translateY(-1px);
	}

	.author {
		color: var(--text-primary);
	}

	.separator {
		color: var(--text-tertiary);
	}

	.topic-link {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		text-decoration: none;
		color: var(--text-secondary);
		font-weight: 700;
		transition: all 0.18s ease;
		padding: 6px 10px;
		border-radius: 999px;
		background: rgba(0, 0, 0, 0.02);
	}

	.topic-link:hover {
		color: var(--link-color);
		background: rgba(228, 87, 46, 0.08);
	}

	.post-title-link {
		text-decoration: none;
		display: block;
	}

	.post-title {
		margin: 2px 0 10px 0;
		font-size: 20px;
		font-weight: 700;
		color: var(--text-primary);
		cursor: pointer;
		transition: color 0.18s ease;
		line-height: 1.35;
		letter-spacing: -0.01em;
	}

	.detail-title {
		font-size: 26px;
		margin: 4px 0 12px 0;
	}

	.post-preview {
		color: var(--text-secondary);
		line-height: 1.55;
		margin-bottom: 10px;
		font-size: 14px;
	}

	.post-preview :global(*) {
		color: var(--text-secondary);
	}

	.post-actions {
		display: flex;
		gap: 4px;
		padding-top: 4px;
	}

	.action-btn {
		display: flex;
		align-items: center;
		gap: 4px;
		padding: 4px 8px;
		background: transparent;
		border: none;
		border-radius: 4px;
		font-size: 12px;
		font-weight: 700;
		cursor: pointer;
		color: var(--text-secondary);
		transition: all 0.15s;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		text-decoration: none;
	}

	.action-btn:hover:not(:disabled) {
		background-color: var(--bg-hover);
		color: var(--text-primary);
	}

	.action-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.action-btn svg {
		width: 16px;
		height: 16px;
		flex-shrink: 0;
	}
</style>
