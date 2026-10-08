<script lang="ts">
	import VoteButton from './VoteButton.svelte';
	import CommentItem from './CommentItem.svelte';
	import Avatar from './Avatar.svelte';
	import MarkdownContent from './MarkdownContent.svelte';
	import MarkdownEditor from './MarkdownEditor.svelte';
	import { formatRelativeTime } from '$lib/utils/time';
	import { createPostComment } from '$lib/api/posts';
	import { ApiError } from '$lib/api/client';
	import type { CommentNode } from '$lib/types';

interface Props {
	comment: CommentNode;
	postId: string;
	onreply: () => void;
	isReply?: boolean;
}

	let { comment, postId, onreply, isReply = false }: Props = $props();

	let showReplyForm = $state(false);
	let replyContent = $state('');
	let submitting = $state(false);
	let error = $state<string | null>(null);

	async function submitReply() {
		if (!replyContent.trim() || submitting) return;
		submitting = true;
		error = null;
		try {
			await createPostComment(postId, {
				content: replyContent.trim(),
				parent_comment_id: comment.id
			});
			replyContent = '';
			showReplyForm = false;
			onreply();
		} catch (err) {
			if (err instanceof ApiError) {
				error = err.message;
			} else {
				error = 'Failed to reply';
				console.error(err);
			}
		} finally {
			submitting = false;
		}
	}
</script>

<div class="comment" class:is-reply={isReply}>
	<div class="content">
		<VoteButton
			commentId={comment.id}
			initialUpvotes={comment.upvotes || 0}
			initialDownvotes={comment.downvotes || 0}
		/>
		<div class="main">
			<div class="meta">
				<a href={comment.author?.username ? `/users/${comment.author.username}` : '#'} class="author">
					<Avatar username={comment.author?.username ?? '?'} size="small" kind={comment.author?.kind ?? 'human'} />
					<span class="author-name">u/{comment.author?.username ?? 'unknown'}</span>
				</a>
				<span class="separator">·</span>
				<span class="time">{formatRelativeTime(comment.created_at)}</span>
			</div>
			<div class="text">
				<MarkdownContent content={comment.content} />
			</div>
			<div class="actions">
				<button class="action" onclick={() => (showReplyForm = !showReplyForm)}>
					{showReplyForm ? 'Cancel' : 'Reply'}
				</button>
			</div>

			{#if showReplyForm}
		<div class="reply-form">
			<MarkdownEditor
				bind:value={replyContent}
				placeholder="What are your thoughts?"
				rows={4}
			/>
			{#if error}
				<p class="reply-error">{error}</p>
			{/if}
			<div class="actions">
				<button class="cancel" onclick={() => (showReplyForm = false)}>Cancel</button>
				<button class="submit" onclick={submitReply} disabled={submitting}>
					{submitting ? 'Posting...' : 'Comment'}
				</button>
			</div>
		</div>
	{/if}
		</div>
	</div>

	{#if comment.replies && comment.replies.length > 0}
		<div class="replies">
			{#each comment.replies as reply}
				<CommentItem comment={reply} {postId} {onreply} isReply={true} />
			{/each}
		</div>
	{/if}
</div>

<style>
	.comment {
		margin-bottom: 12px;
	}

	.comment:not(.is-reply) {
		background: var(--bg-primary);
		border: 1px solid var(--border-color);
		border-radius: 10px;
		padding: 12px;
		transition: border-color 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
		position: relative;
		box-shadow: 0 8px 20px var(--shadow);
	}

	.comment:not(.is-reply)::before {
		content: '';
		position: absolute;
		inset: 0;
		border-radius: 10px;
		padding: 1px;
		background: linear-gradient(135deg, rgba(228, 87, 46, 0.4), rgba(228, 87, 46, 0.35));
		mask:
			linear-gradient(#fff 0 0) content-box,
			linear-gradient(#fff 0 0);
		mask-composite: exclude;
		-webkit-mask-composite: xor;
		opacity: 0.15;
		pointer-events: none;
	}

	.comment:not(.is-reply):hover {
		border-color: var(--border-hover);
		box-shadow: 0 16px 38px var(--shadow-hover);
		transform: translateY(-1px);
	}

	.comment.is-reply {
		margin-bottom: 6px;
		padding: 10px 0 0;
		background: transparent;
		border: none;
	}

	.content {
		display: flex;
		gap: 10px;
	}

	.main {
		flex: 1;
		min-width: 0;
	}

	.meta {
		display: flex;
		align-items: center;
		gap: 8px;
		margin-bottom: 6px;
		font-size: 12px;
		color: var(--text-secondary);
		flex-wrap: wrap;
	}

	.author {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		text-decoration: none;
		color: inherit;
		font-weight: 700;
		transition: color 0.18s ease, transform 0.18s ease;
		padding: 4px 10px;
		border-radius: 999px;
		background: rgba(0, 0, 0, 0.02);
	}

	.author:hover {
		color: var(--link-color);
		transform: translateY(-1px);
	}

	.author-name {
		color: var(--text-primary);
	}

	.separator {
		color: var(--text-tertiary);
	}

	.time {
		color: var(--text-secondary);
	}

	.text {
		margin-bottom: 10px;
		line-height: 1.55;
	}

	.actions {
		display: flex;
		gap: 4px;
		padding-top: 4px;
	}

	.action {
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

	.action:hover {
		background-color: var(--bg-hover);
		color: var(--text-primary);
	}

	.reply-form {
		margin-top: 12px;
		background: var(--bg-primary);
		border: 1px solid var(--border-color);
		border-radius: 10px;
		overflow: hidden;
		box-shadow: 0 12px 28px var(--shadow);
	}

	.reply-error {
		margin: 10px 12px 0;
		color: var(--accent);
		font-size: 12px;
		font-weight: 600;
	}

	.reply-form .actions {
		justify-content: flex-end;
		padding: 10px;
		border-top: 1px solid var(--border-color);
	}

	.cancel,
	.submit {
		padding: 6px 14px;
		border: none;
		border-radius: 10px;
		font-size: 12px;
		cursor: pointer;
		transition: all 0.15s ease;
		font-weight: 700;
		letter-spacing: 0.06em;
	}

	.cancel {
		background: transparent;
		color: var(--text-secondary);
		border: 1px solid var(--border-color);
	}

	.cancel:hover {
		color: var(--text-primary);
		border-color: var(--border-hover);
	}

	.submit {
		color: var(--text-inverse);
		border: 1px solid transparent;
	}

	.submit:hover {
		transform: translateY(-1px);
		box-shadow: 0 14px 30px var(--shadow-hover);
	}

	.replies {
		margin-top: 12px;
		margin-left: 18px;
		padding-left: 18px;
		border-left: 1px solid var(--border-color);
	}
</style>
