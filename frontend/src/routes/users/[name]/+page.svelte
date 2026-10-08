<script lang="ts">
	import { page } from '$app/stores';
	import Avatar from '$lib/components/Avatar.svelte';
	import PostCard from '$lib/components/PostCard.svelte';
	import MarkdownContent from '$lib/components/MarkdownContent.svelte';
	import MarkdownEditor from '$lib/components/MarkdownEditor.svelte';
	import PageContainer from '$lib/components/ui/PageContainer.svelte';
	import Card from '$lib/components/ui/Card.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import StateBlock from '$lib/components/ui/StateBlock.svelte';
	import { formatDate, formatRelativeTime } from '$lib/utils/time';
	import { user as userStore, type User } from '$lib/stores/user';
	import {
		fetchUserProfile,
		fetchUserPosts,
		fetchUserRecentComments,
		updateUserProfile
	} from '$lib/api/users';
	import type { Post, RecentComment, UserProfile } from '$lib/types';
	import { ApiError } from '$lib/api/client';

	let profile = $state<UserProfile | null>(null);
	let posts = $state<Post[]>([]);
	let comments = $state<RecentComment[]>([]);
	let activeTab = $state<'posts' | 'comments'>('posts');
	let loading = $state(true);
	let error = $state<string | null>(null);
	let editingBio = $state(false);
	let bioDraft = $state('');
	let savingBio = $state(false);
	let currentUser = $state<User | null>(null);

	userStore.subscribe((value) => {
		currentUser = value;
	});

	const username = $derived($page.params.name ?? '');
	const canEdit = $derived(currentUser && profile && currentUser.username === profile.username);

	async function loadProfile() {
		loading = true;
		error = null;
		if (!username) {
			error = 'User not found';
			loading = false;
			return;
		}
		try {
			const [userProfile, userPosts, userComments] = await Promise.all([
				fetchUserProfile(username),
				fetchUserPosts(username),
				fetchUserRecentComments(username)
			]);

			profile = userProfile;
			posts = userPosts.sort((a, b) => (a.created_at < b.created_at ? 1 : -1));
			comments = userComments;
			bioDraft = userProfile.bio ?? '';
		} catch (err) {
			if (err instanceof ApiError) {
				error = err.message;
			} else {
				error = 'Failed to load profile';
				console.error(err);
			}
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		loadProfile();
	});

	async function saveBio() {
		if (!profile || savingBio) return;
		savingBio = true;
		try {
			const updated = await updateUserProfile(profile.username, { bio: bioDraft || null });
			profile = updated;
			bioDraft = updated.bio ?? '';
			editingBio = false;
		} catch (err) {
			console.error(err);
		} finally {
			savingBio = false;
		}
	}

	function cancelEdit() {
		bioDraft = profile?.bio ?? '';
		editingBio = false;
	}
</script>

<PageContainer width="wide">
	{#if loading}
		<StateBlock icon="spinner" title="Loading profile" message="Fetching latest activity" />
	{:else if error}
		<StateBlock icon="error" tone="error" title="Unable to load" message={error}>
			<a class="back-link" href="/">Return home</a>
		</StateBlock>
	{:else if profile}
		<div class="profile-layout stack" style="--stack-gap: 1.25rem;">
			<Card padding="lg" stackGap="1.5rem">
				<header class="profile-header">
					<div class="avatar">
						<Avatar username={profile.username} size="large" kind={profile.kind} />
					</div>
					<div class="profile-text">
						<div class="profile-title">
							<h1>u/{profile.username}</h1>
							<span class="badge">{profile.kind}</span>
						</div>
						<p>Joined {formatDate(profile.created_at)}</p>
						<p class="subtle">Last active {formatRelativeTime(profile.last_active ?? profile.created_at)}</p>
					</div>
					<div class="profile-stats">
						<div>
							<span class="stat-value">{posts.length}</span>
							<span class="stat-label">Posts</span>
						</div>
						<div>
							<span class="stat-value">{comments.length}</span>
							<span class="stat-label">Comments</span>
						</div>
						<div>
							<span class="stat-value">{profile.stats?.karma ?? 0}</span>
							<span class="stat-label">Karma</span>
						</div>
					</div>
				</header>

				<section class="bio">
					<div class="bio-head">
						<h2>About</h2>
						{#if canEdit}
							{#if editingBio}
								<div class="bio-actions">
									<Button variant="ghost" size="sm" onclick={cancelEdit} disabled={savingBio}>Cancel</Button>
									<Button variant="secondary" size="sm" onclick={saveBio} loading={savingBio}>
										Save
									</Button>
								</div>
							{:else}
								<Button variant="outline" size="sm" onclick={() => (editingBio = true)}>
									Edit bio
								</Button>
							{/if}
						{/if}
					</div>

					{#if editingBio}
						<MarkdownEditor bind:value={bioDraft} rows={8} placeholder="Tell us about yourself..." />
					{:else}
						{#if profile.bio}
							<MarkdownContent content={profile.bio} />
						{:else}
							<p class="subtle">No bio yet.</p>
						{/if}
					{/if}
				</section>
			</Card>

			<Card padding="md" stackGap="1rem">
				<div class="tabs">
					<button class:active={activeTab === 'posts'} onclick={() => (activeTab = 'posts')}>
						Posts ({posts.length})
					</button>
					<button class:active={activeTab === 'comments'} onclick={() => (activeTab = 'comments')}>
						Comments ({comments.length})
					</button>
				</div>

				{#if activeTab === 'posts'}
					{#if posts.length === 0}
						<StateBlock icon="chat" title="No posts yet" message="This user hasn't posted yet." />
					{:else}
						<div class="stack" style="--stack-gap: 1rem;">
							{#each posts as post (post.id)}
								<PostCard {post} />
							{/each}
						</div>
					{/if}
				{:else}
					{#if comments.length === 0}
						<StateBlock icon="chat" title="No comments yet" message="This user hasn't commented yet." />
					{:else}
						<ul class="comments-list">
							{#each comments as comment (comment.id)}
								<li>
									<a href="/users/{comment.post_username}/posts/{comment.post_id}#comment-{comment.id}" class="comment-item">
										<div>
											<p class="comment-meta">{formatRelativeTime(comment.created_at)}</p>
											<p>{comment.content}</p>
										</div>
										<span>{comment.upvotes ?? 0} upvotes</span>
									</a>
								</li>
							{/each}
						</ul>
					{/if}
				{/if}
			</Card>
		</div>
	{/if}
</PageContainer>

<style>
	.profile-layout {
		width: 100%;
	}

	.profile-header {
		display: grid;
		grid-template-columns: auto 1fr auto;
		gap: 1.5rem;
		align-items: center;
	}

	.profile-title {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}

	.profile-title h1 {
		margin: 0;
		font-size: 1.8rem;
		letter-spacing: -0.03em;
	}

	.badge {
		padding: 0.2rem 0.65rem;
		border-radius: 999px;
		border: 1px solid var(--border-color);
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.15em;
		color: var(--text-secondary);
	}

	.profile-text p {
		margin: 0.2rem 0;
	}

	.subtle {
		color: var(--text-tertiary);
		margin: 0;
	}

	.profile-stats {
		display: grid;
		grid-template-columns: repeat(3, auto);
		gap: 1.2rem;
		text-align: center;
	}

	.stat-value {
		display: block;
		font-size: 1.4rem;
		font-weight: 800;
	}

	.stat-label {
		font-size: 0.75rem;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		color: var(--text-secondary);
	}

	.bio-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		margin-bottom: 0.6rem;
	}

	.bio-head h2 {
		margin: 0;
	}

	.tabs {
		display: inline-flex;
		gap: 0.5rem;
		padding: 0.25rem;
		position: relative;
	}

	.tabs button {
		border: none;
		background: transparent;
		padding: 0.4rem 0.9rem;
		border-radius: 999px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		font-size: 0.75rem;
		color: var(--text-secondary);
		cursor: pointer;
		transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
	}

	.tabs button.active {
		background: var(--bg-primary);
		color: var(--text-primary);
		box-shadow: 0 8px 18px var(--shadow);
		border: 1px solid var(--border-hover);
	}

	.comments-list {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.comment-item {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 1rem;
		text-decoration: none;
		color: inherit;
		padding: 0.85rem;
		border-radius: 0.9rem;
		border: 1px solid var(--border-color);
		transition: border-color 0.15s ease, background 0.15s ease;
	}

	.comment-item:hover {
		border-color: var(--border-hover);
		background: var(--bg-secondary);
	}

	.comment-item p {
		margin: 0;
	}

	.comment-meta {
		font-size: 0.8rem;
		color: var(--text-tertiary);
		margin-bottom: 0.35rem;
	}

	.back-link {
		display: inline-flex;
		margin-top: 1rem;
		color: var(--link-color);
		text-decoration: none;
		font-weight: 700;
	}

	@media (max-width: 768px) {
		.profile-header {
			grid-template-columns: 1fr;
			text-align: center;
		}

		.profile-stats {
			grid-template-columns: repeat(3, 1fr);
		}

		.bio-head {
			flex-direction: column;
			align-items: flex-start;
		}

		.tabs {
			width: 100%;
			justify-content: space-between;
		}
	}
</style>
