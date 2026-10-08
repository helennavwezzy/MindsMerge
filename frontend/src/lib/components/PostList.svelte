<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { browser } from '$app/environment';
	import PostCard from './PostCard.svelte';
	import StateBlock from '$lib/components/ui/StateBlock.svelte';
	import type { Post } from '$lib/types';
	import { ApiError } from '$lib/api/client';
	import { fetchPosts } from '$lib/api/posts';

	interface Props {
		topicId: number | null;
	}

	let { topicId }: Props = $props();

	let posts = $state<Post[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function loadPosts() {
		loading = true;
		error = null;
		try {
			posts = await fetchPosts(topicId);
		} catch (err) {
			if (err instanceof ApiError) {
				error = err.message;
			} else {
				error = 'Failed to load posts';
				console.error(err);
			}
		} finally {
			loading = false;
		}
	}

	const handleRefresh = () => loadPosts();

	$effect(() => {
		loadPosts();
	});

	onMount(() => {
		if (browser) {
			window.addEventListener('refreshPosts', handleRefresh);
		}
	});

	onDestroy(() => {
		if (browser) {
			window.removeEventListener('refreshPosts', handleRefresh);
		}
	});
</script>

<div class="post-list stack" style="--stack-gap: 0.75rem;">
	{#if loading}
		<StateBlock icon="spinner" title="Loading posts" message="Fetching the latest threads..." />
	{:else if error}
		<StateBlock icon="error" tone="error" title="Unable to load posts" message={error} />
	{:else if posts.length === 0}
		<StateBlock icon="chat" title="No posts yet" message="Be the first to share something with the community" />
	{:else}
		{#each posts as post (post.id)}
			<PostCard {post} />
		{/each}
	{/if}
</div>

<style>
	.post-list {
		width: 100%;
	}
</style>
