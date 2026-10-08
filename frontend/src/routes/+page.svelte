<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { user } from '$lib/stores/user';
	import PostList from '$lib/components/PostList.svelte';
	import CreatePost from '$lib/components/CreatePost.svelte';
	import PageContainer from '$lib/components/ui/PageContainer.svelte';
	import PageHeader from '$lib/components/ui/PageHeader.svelte';

	let showCreatePost = $state(false);
	let currentUser = $state<any>(null);

	user.subscribe((u) => {
		currentUser = u;
	});

	onMount(() => {
		if (browser && !currentUser) {
			setTimeout(() => {
				if (!currentUser) {
					goto('/welcome');
				}
			}, 100);
		}
	});

	function handlePostCreated() {
		showCreatePost = false;
		window.dispatchEvent(new CustomEvent('refreshPosts'));
	}
</script>

{#if currentUser}
	<PageContainer width="narrow">
	<PageHeader
		title="Home"
		subtitle="Your personalized feed"
		actionLabel="Create Post"
		onAction={() => (showCreatePost = true)}
	/>

		{#if showCreatePost}
			<CreatePost selectedTopicId={null} onClose={() => (showCreatePost = false)} onCreated={handlePostCreated} />
		{/if}

		<section class="page-content">
			<PostList topicId={null} />
		</section>
	</PageContainer>
{/if}

<style>
	.page-content {
		margin-top: 1.25rem;
	}
</style>
