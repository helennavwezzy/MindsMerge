<script lang="ts">
	import { page } from '$app/stores';
	import PostList from '$lib/components/PostList.svelte';
	import CreatePost from '$lib/components/CreatePost.svelte';
	import PageContainer from '$lib/components/ui/PageContainer.svelte';
	import PageHeader from '$lib/components/ui/PageHeader.svelte';
	import StateBlock from '$lib/components/ui/StateBlock.svelte';
	import { fetchTopics } from '$lib/api/topics';
	import type { Topic } from '$lib/types';
	import { ApiError } from '$lib/api/client';

	let topicId = $state<number | null>(null);
let showCreatePost = $state(false);
let topics = $state<Topic[]>([]);
let loading = $state(true);
let error = $state<string | null>(null);
let topicDescription = $state('');

const topicName = $derived(($page.params.name || '').toLowerCase());

async function resolveTopic(name: string) {
	loading = true;
	error = null;
	try {
		topics = await fetchTopics();
		const match = topics.find((topic) => topic.name.toLowerCase() === name && topic.name !== 'All');
		if (match) {
			topicId = match.id;
			topicDescription = match.description;
		} else {
			topicId = null;
			error = 'Topic not found';
			topicDescription = '';
		}
	} catch (err) {
		if (err instanceof ApiError) {
			error = err.message;
		} else {
			error = 'Unable to load topic';
			console.error(err);
		}
		topicDescription = '';
	} finally {
		loading = false;
	}
}

	$effect(() => {
		const name = topicName;
		resolveTopic(name);
	});

	function handlePostCreated() {
		showCreatePost = false;
		window.dispatchEvent(new CustomEvent('refreshPosts'));
	}
</script>

<PageContainer width="narrow">
	<PageHeader
		title={`r/${topicName}`}
		actionLabel="Create post"
		onAction={() => (showCreatePost = true)}
	/>

	{#if topicDescription}
		<div class="page-description">
			<span class="page-description__label">Introduction</span>
			<p>{topicDescription}</p>
		</div>
	{/if}

	{#if showCreatePost && topicId !== null}
		<CreatePost selectedTopicId={topicId} onClose={() => (showCreatePost = false)} onCreated={handlePostCreated} />
	{/if}

	<div class="page-content">
		{#if loading}
			<StateBlock icon="spinner" title="Loading posts" message="Give us a second to gather the latest conversations." />
		{:else if error}
			<StateBlock icon="error" tone="error" title="r/{topicName}" message={error}>
				<a class="back-link" href="/">Return home</a>
			</StateBlock>
		{:else if topicId !== null}
			<PostList topicId={topicId} />
		{/if}
	</div>
</PageContainer>

<style>
	.page-content {
		margin-top: 1.25rem;
	}

	.page-description {
		margin-top: 1rem;
		padding: 0.85rem 2rem;
		border-radius: 1rem;
		background: var(--bg-primary);
		border: 1px solid var(--border-color);
		box-shadow: 0 8px 18px var(--shadow);
	}

	.page-description__label {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		font-size: 0.7rem;
		letter-spacing: 0.15em;
		text-transform: uppercase;
		color: var(--text-tertiary);
		font-weight: 700;
		margin-bottom: 0.45rem;
	}

	.page-description p {
		margin: 0;
		font-size: 0.98rem;
		color: var(--text-primary);
		line-height: 1.6;
		letter-spacing: 0.01em;
	}

	.back-link {
		display: inline-flex;
		margin-top: 0.75rem;
		color: var(--link-color);
		text-decoration: none;
		font-weight: 700;
	}
</style>
