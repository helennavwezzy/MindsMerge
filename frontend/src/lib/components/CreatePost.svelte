<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import MarkdownEditor from './MarkdownEditor.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import FormField from '$lib/components/ui/FormField.svelte';
	import { fetchTopics } from '$lib/api/topics';
	import { createPost } from '$lib/api/posts';
	import { ApiError } from '$lib/api/client';
	import type { Topic } from '$lib/types';

	interface Props {
		selectedTopicId: number | null;
		onClose: () => void;
		onCreated: () => void;
	}

	let { selectedTopicId, onClose, onCreated }: Props = $props();

	let topics = $state<Topic[]>([]);
	let topicValue = $state(selectedTopicId ? String(selectedTopicId) : '');
	let title = $state('');
	let content = $state('');
	let loadingTopics = $state(true);
	let saving = $state(false);
	let error = $state<string | null>(null);

	const selectedTopic = $derived(topicValue ? Number(topicValue) : null);

	async function loadTopics() {
		loadingTopics = true;
		try {
			topics = await fetchTopics();
		} catch (err) {
			console.error('Failed to load topics', err);
		} finally {
			loadingTopics = false;
		}
	}

	onMount(() => {
		loadTopics();
	});

	function handleFormSubmit(event: Event) {
		event.preventDefault();
		handleSubmit();
	}

	async function handleSubmit() {
		if (!title.trim()) {
			error = 'A descriptive title helps others understand your post.';
			return;
		}
		if (!content.trim()) {
			error = 'Share your thoughts before publishing the post.';
			return;
		}

		saving = true;
		error = null;
		try {
			await createPost({
				title: title.trim(),
				content: content.trim(),
				topic_id: selectedTopic
			});

			toast.success('Post published');
			title = '';
			content = '';
			topicValue = selectedTopicId ? String(selectedTopicId) : '';
			onCreated?.();
		} catch (err) {
			if (err instanceof ApiError) {
				error = err.message;
			} else {
				error = 'Failed to create post. Please try again.';
				console.error(err);
			}
		} finally {
			saving = false;
		}
	}

	function handleClose() {
		error = null;
		onClose();
	}
</script>

<Modal open={true} onClose={handleClose} title="Create a post" width="wide">
	<form class="stack" style="--stack-gap: 1.2rem;" onsubmit={handleFormSubmit}>
		{#if error}
			<div class="form-error">
				{error}
			</div>
		{/if}

		<FormField label="Choose a community" for="topic">
			<select
				id="topic"
				class="input-control"
				bind:value={topicValue}
				disabled={loadingTopics}
			>
				<option value="">
					{loadingTopics ? 'Loading topics...' : 'Select a community'}
				</option>
				{#each topics.filter((topic) => topic.name !== 'All') as topic}
					<option value={topic.id}>r/{topic.name}</option>
				{/each}
			</select>
		</FormField>

		<FormField label="Title" for="title">
			<input
				id="title"
				type="text"
				class="input-control"
				placeholder="What do you want to share?"
				autocomplete="off"
				bind:value={title}
				required
			/>
		</FormField>

		<FormField label="Content" for="content" message="Markdown supported">
			<div class="editor-wrapper">
				<MarkdownEditor
					id="content"
					bind:value={content}
					rows={12}
					placeholder="Write your post content..."
				/>
			</div>
		</FormField>

		<div class="form-actions">
			<Button type="button" variant="outline" onclick={handleClose} disabled={saving}>
				Cancel
			</Button>
			<Button type="submit" loading={saving}>
				{saving ? 'Posting...' : 'Post'}
			</Button>
		</div>
	</form>
</Modal>

<style>
	.form-error {
		padding: 0.85rem 1rem;
		border-radius: 0.9rem;
		background: rgba(228, 87, 46, 0.12);
		border: 1px solid rgba(228, 87, 46, 0.35);
		color: var(--accent);
		font-weight: 600;
	}

	.form-actions {
		display: flex;
		justify-content: flex-end;
		gap: 0.75rem;
	}
</style>
