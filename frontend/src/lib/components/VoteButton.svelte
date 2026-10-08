<script lang="ts">
	type VoteIntent = 'upvote' | 'downvote' | 'novote';

	interface Props {
		postId?: string;
		commentId?: string;
		initialUpvotes?: number;
		initialDownvotes?: number;
		initialUserVote?: number | null;
	}

	let {
		postId,
		commentId,
		initialUpvotes = 0,
		initialDownvotes = 0,
		initialUserVote = null
	}: Props = $props();

	let upvotes = $state(initialUpvotes);
	let downvotes = $state(initialDownvotes);
	let userVote = $state<number | null>(initialUserVote);
	let loading = $state(false);
	let animating = $state(false);

	const score = $derived(upvotes - downvotes);

	async function vote(voteType: number) {
		if (loading) return;

		const targetIdentifier = postId ?? commentId;
		if (!targetIdentifier) return;

		loading = true;
		animating = true;

		const previousVote = userVote;
		const previousUpvotes = upvotes;
		const previousDownvotes = downvotes;

		// Optimistic update
		if (userVote === voteType) {
			userVote = null;
			if (voteType === 1) upvotes = Math.max(0, upvotes - 1);
			else downvotes = Math.max(0, downvotes - 1);
		} else if (userVote === -voteType) {
			userVote = voteType;
			if (voteType === 1) {
				upvotes += 1;
				downvotes = Math.max(0, downvotes - 1);
			} else {
				downvotes += 1;
				upvotes = Math.max(0, upvotes - 1);
			}
		} else {
			userVote = voteType;
			if (voteType === 1) upvotes += 1;
			else downvotes += 1;
		}

		const normalizedIntent: VoteIntent = voteType === 1 ? 'upvote' : 'downvote';
		const payloadVoteType: VoteIntent = previousVote === voteType ? 'novote' : normalizedIntent;

		try {
			const payload: Record<string, string | VoteIntent> = {
				vote_type: payloadVoteType
			};
			if (postId) {
				payload.post_id = postId;
			} else if (commentId) {
				payload.comment_id = commentId;
			}

			const response = await fetch('/api/votes', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload)
			});

			if (!response.ok) {
				userVote = previousVote;
				upvotes = previousUpvotes;
				downvotes = previousDownvotes;
			}
		} catch (error) {
			userVote = previousVote;
			upvotes = previousUpvotes;
			downvotes = previousDownvotes;
		} finally {
			loading = false;
			setTimeout(() => (animating = false), 200);
		}
	}
</script>

<div class="vote-container">
	<button
		class="vote-btn upvote"
		class:active={userVote === 1}
		class:animating={animating && userVote === 1}
		onclick={() => vote(1)}
		disabled={loading}
		aria-label="Upvote"
	>
		<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
			<path d="M12 8l-6 6h12l-6-6z" />
		</svg>
	</button>
	<span class="score" class:positive={score > 0} class:negative={score < 0}>
		{score}
	</span>
	<button
		class="vote-btn downvote"
		class:active={userVote === -1}
		class:animating={animating && userVote === -1}
		onclick={() => vote(-1)}
		disabled={loading}
		aria-label="Downvote"
	>
		<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
			<path d="M12 16l6-6H6l6 6z" />
		</svg>
	</button>
</div>

<style>
	.vote-container {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 4px;
		min-width: 36px;
		padding: 0;
		background: transparent;
	}

	.vote-btn {
		background: transparent;
		border: none;
		border-radius: 8px;
		padding: 4px;
		cursor: pointer;
		transition: all 0.15s ease;
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--text-secondary);
		box-shadow: none;
	}

	.vote-btn:hover:not(:disabled) {
		border-color: var(--border-hover);
		background: var(--bg-hover);
	}

	.vote-btn.upvote:hover:not(:disabled) {
		color: var(--upvote);
	}

	.vote-btn.downvote:hover:not(:disabled) {
		color: var(--downvote);
	}

	.vote-btn.active {
		color: var(--text-primary);
		border-color: currentColor;
		background: var(--bg-secondary);
	}

	.vote-btn.upvote.active {
		color: var(--upvote);
	}

	.vote-btn.downvote.active {
		color: var(--downvote);
	}

	.vote-btn.animating {
		animation: pulse 0.24s ease;
	}

	@keyframes pulse {
		0%,
		100% {
			transform: scale(1);
		}
		50% {
			transform: scale(1.15);
		}
	}

	.vote-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.score {
		font-weight: 800;
		font-size: 13px;
		color: var(--text-primary);
		min-width: 24px;
		text-align: center;
		line-height: 1.2;
	}

	.score.positive {
		color: var(--upvote);
	}

	.score.negative {
		color: var(--downvote);
	}
</style>
