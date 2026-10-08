<script lang="ts">
	import PostCard from '$lib/components/PostCard.svelte';
	import PostComments from '$lib/components/PostComments.svelte';
	import PageContainer from '$lib/components/ui/PageContainer.svelte';
	import StateBlock from '$lib/components/ui/StateBlock.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { fetchPost } from '$lib/api/posts';
	import type { Post } from '$lib/types';
	import { ApiError } from '$lib/api/client';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	let post = $state<Post | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function loadPost() {
		loading = true;
		error = null;
		try {
		const postId = $page.params.id;
		const username = $page.params.name ?? '';
		if (!postId) {
			error = 'Post not found';
			loading = false;
			return;
		}
		const data = await fetchPost(postId);
		if (data.author?.username !== username) {
			goto(`/users/${data.author?.username ?? 'unknown'}/posts/${postId}`);
			return;
		}
		post = data;
		} catch (err) {
			if (err instanceof ApiError) {
				error = err.message;
			} else {
				error = 'Failed to load post';
				console.error(err);
			}
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		loadPost();
	});
</script>

<PageContainer>
	{#if loading}
		<StateBlock icon="spinner" title="Loading post" message="Grabbing this thread for you" />
	{:else if error}
		<StateBlock icon="error" tone="error" title="Unable to load" message={error}>
			<Button href="/" variant="outline">Go back home</Button>
		</StateBlock>
	{:else if post}
		<div class="stack" style="--stack-gap: 1.5rem;">
		<PostCard {post} variant="detail" />
			<PostComments postId={post.id} />
		</div>
	{/if}
</PageContainer>
