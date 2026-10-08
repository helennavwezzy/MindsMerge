<script lang="ts">
	import CommentItem from './CommentItem.svelte';
	import MarkdownEditor from './MarkdownEditor.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import StateBlock from '$lib/components/ui/StateBlock.svelte';
	import type { CommentNode } from '$lib/types';
	import { ApiError } from '$lib/api/client';
	import { fetchPostComments, createPostComment } from '$lib/api/posts';

interface Props {
	postId: string;
}

	let { postId }: Props = $props();

	let comments = $state<CommentNode[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let showForm = $state(false);
	let content = $state('');
	let submitting = $state(false);

	async function loadComments() {
		loading = true;
		error = null;
		try {
			comments = await fetchPostComments(postId);
		} catch (err) {
			if (err instanceof ApiError) {
				error = err.message;
			} else {
				error = 'Failed to load comments';
				console.error(err);
			}
		} finally {
			loading = false;
		}
	}

	loadComments();

	async function submitComment() {
		if (!content.trim() || submitting) return;
		submitting = true;
		try {
			await createPostComment(postId, { content: content.trim() });
			content = '';
			showForm = false;
			await loadComments();
		} catch (err) {
			console.error(err);
		} finally {
			submitting = false;
		}
	}
</script>

<section class="comments">
	<header class="comments__header">
		<h3>{comments.length} {comments.length === 1 ? 'Comment' : 'Comments'}</h3>
		<Button variant="outline" size="sm" onclick={() => (showForm = !showForm)}>
			{showForm ? 'Close form' : 'Add comment'}
		</Button>
	</header>

	{#if showForm}
		<div class="comment-form">
			<MarkdownEditor bind:value={content} rows={6} placeholder="What are your thoughts?" />
			<div class="comment-form__actions">
				<Button variant="ghost" type="button" onclick={() => (showForm = false)} disabled={submitting}>
					Cancel
				</Button>
				<Button type="button" onclick={submitComment} loading={submitting}>
					Comment
				</Button>
			</div>
		</div>
	{/if}

	{#if loading}
		<StateBlock icon="spinner" title="Loading comments" message="Gathering community responses" />
	{:else if error}
		<StateBlock icon="error" tone="error" title="Unable to load" message={error} />
	{:else if comments.length === 0}
		<StateBlock icon="chat" title="No comments yet" message="Be the first to start a discussion" />
	{:else}
		<div class="comment-list">
			{#each comments as comment (comment.id)}
				<CommentItem {comment} {postId} onreply={loadComments} />
			{/each}
		</div>
	{/if}
</section>

<style>
	.comments {
		margin-top: 2rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.comments__header {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.comments__header h3 {
		margin: 0;
		font-size: 1.2rem;
	}

	.comment-form {
		border: 1px solid var(--border-color);
		border-radius: 1rem;
		padding: 1rem;
		background: var(--bg-primary);
		box-shadow: 0 12px 26px var(--shadow);
	}

	.comment-form__actions {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
		margin-top: 0.75rem;
	}

	.comment-list {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}
</style>
