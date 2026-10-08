<script lang="ts">
	import { renderMarkdown } from '$lib/utils/markdown';
	import { sanitizeHtml } from '$lib/utils/sanitize';
	import { browser } from '$app/environment';

	interface Props {
		value: string;
		placeholder?: string;
		rows?: number;
		required?: boolean;
		id?: string;
	}

	let { value = $bindable(), placeholder = 'Write your content...', rows = 6, required = false, id }: Props = $props();
	let editorTab = $state<'edit' | 'preview'>('edit');
	let textareaElement: HTMLTextAreaElement | null = $state(null);
	let fileInputElement: HTMLInputElement | null = $state(null);
	let isDragging = $state(false);
	let isUploading = $state(false);
	let uploadProgress = $state(0);
	let dragCounter = $state(0);

	function insertTextAtCursor(text: string) {
		if (!textareaElement) return;

		const start = textareaElement.selectionStart;
		const end = textareaElement.selectionEnd;
		const before = value.substring(0, start);
		const after = value.substring(end);

		value = before + text + after;

		// Set cursor position after inserted text
		setTimeout(() => {
			if (textareaElement) {
				const newPosition = start + text.length;
				textareaElement.setSelectionRange(newPosition, newPosition);
				textareaElement.focus();
			}
		}, 0);
	}

	async function uploadFile(file: File) {
		if (isUploading) return;

		isUploading = true;
		uploadProgress = 0;

		try {
			const formData = new FormData();
			formData.append('file', file);

			const xhr = new XMLHttpRequest();

			// Track upload progress
			xhr.upload.addEventListener('progress', (e) => {
				if (e.lengthComputable) {
					uploadProgress = Math.round((e.loaded / e.total) * 100);
				}
			});

			const response = await new Promise<{ url: string; type: string }>((resolve, reject) => {
				xhr.addEventListener('load', () => {
					if (xhr.status === 200) {
						resolve(JSON.parse(xhr.responseText));
					} else {
						reject(new Error(JSON.parse(xhr.responseText).error || 'Upload failed'));
					}
				});

				xhr.addEventListener('error', () => reject(new Error('Upload failed')));
				xhr.open('POST', '/api/upload');
				xhr.send(formData);
			});

			// Insert markdown based on file type
			if (response.type === 'image') {
				insertTextAtCursor(`\n![${file.name}](${response.url})\n`);
			} else if (response.type === 'video') {
				insertTextAtCursor(`\n<video controls>\n  <source src="${response.url}" type="${file.type}">\n  Your browser does not support the video tag.\n</video>\n`);
			}
		} catch (error) {
			console.error('Upload error:', error);
			alert(error instanceof Error ? error.message : 'Failed to upload file');
		} finally {
			isUploading = false;
			uploadProgress = 0;
		}
	}

	function handleFileSelect(event: Event) {
		const input = event.target as HTMLInputElement;
		const file = input.files?.[0];
		if (file) {
			uploadFile(file);
		}
		// Reset input so same file can be selected again
		if (fileInputElement) {
			fileInputElement.value = '';
		}
	}

	function handleDragEnter(e: DragEvent) {
		e.preventDefault();
		e.stopPropagation();
		dragCounter++;
		if (e.dataTransfer?.items && e.dataTransfer.items.length > 0) {
			isDragging = true;
		}
	}

	function handleDragLeave(e: DragEvent) {
		e.preventDefault();
		e.stopPropagation();
		dragCounter--;
		if (dragCounter === 0) {
			isDragging = false;
		}
	}

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		e.stopPropagation();
	}

	function handleDrop(e: DragEvent) {
		e.preventDefault();
		e.stopPropagation();
		isDragging = false;
		dragCounter = 0;

		const files = e.dataTransfer?.files;
		if (files && files.length > 0) {
			const file = files[0];
			uploadFile(file);
		}
	}
</script>

<div class="editor-tabs">
	<button
		type="button"
		class="editor-tab"
		class:active={editorTab === 'edit'}
		onclick={() => (editorTab = 'edit')}
	>
		<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
			<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
			<path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
		</svg>
		Edit
	</button>
	<button
		type="button"
		class="editor-tab"
		class:active={editorTab === 'preview'}
		onclick={() => (editorTab = 'preview')}
	>
		<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
			<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
			<circle cx="12" cy="12" r="3" />
		</svg>
		Preview
	</button>
	{#if editorTab === 'edit' && browser}
		<div class="editor-tabs-spacer"></div>
		<button
			type="button"
			class="upload-btn"
			onclick={() => fileInputElement?.click()}
			disabled={isUploading}
			title="Upload image or video"
		>
			{#if isUploading}
				<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<circle cx="12" cy="12" r="10" />
					<path d="M12 6v6l4 2" />
				</svg>
				<span class="upload-progress-text">{uploadProgress}%</span>
			{:else}
				<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
					<polyline points="17 8 12 3 7 8" />
					<line x1="12" y1="3" x2="12" y2="15" />
				</svg>
				Attach
			{/if}
		</button>
		<input
			bind:this={fileInputElement}
			type="file"
			accept="image/*,video/*"
			class="file-input"
			onchange={handleFileSelect}
		/>
	{/if}
</div>
<div
	class="editor-content"
	class:dragging={isDragging}
	role="textbox"
	tabindex="-1"
	ondragenter={handleDragEnter}
	ondragleave={handleDragLeave}
	ondragover={handleDragOver}
	ondrop={handleDrop}
>
	{#if editorTab === 'edit'}
		<textarea
			bind:this={textareaElement}
			{id}
			bind:value={value}
			{placeholder}
			{rows}
			{required}
			class="content-textarea"
		></textarea>
		{#if isDragging}
			<div class="drag-overlay">
				<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
					<polyline points="17 8 12 3 7 8" />
					<line x1="12" y1="3" x2="12" y2="15" />
				</svg>
				<p>Drop image or video here</p>
			</div>
		{/if}
	{:else}
		<div class="preview-content">
			{@html sanitizeHtml(renderMarkdown(value || '*No content yet.*'))}
		</div>
	{/if}
</div>

<style>
	.editor-tabs {
		display: flex;
		gap: 8px;
		border: none;
		background: var(--bg-primary);
		padding: 8px 12px 6px;
		align-items: center;
	}

	.editor-tab {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		padding: 10px 14px;
		background: var(--bg-secondary);
		border: 1px solid transparent;
		color: var(--text-secondary);
		cursor: pointer;
		transition: all 0.18s ease;
		font-size: 14px;
		font-weight: 700;
		border-radius: 12px;
		letter-spacing: 0.06em;
	}

	.editor-tab:hover {
		color: var(--text-primary);
		border-color: var(--border-hover);
		transform: translateY(-1px);
	}

	.editor-tab.active {
		color: var(--text-primary);
		border-color: var(--link-color);
		background: var(--bg-secondary);
		box-shadow: 0 6px 14px var(--shadow);
	}

	.editor-tab svg {
		width: 14px;
		height: 14px;
		flex-shrink: 0;
	}

	.editor-tabs-spacer {
		flex: 1;
	}

	.upload-btn {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		padding: 10px 14px;
		background: var(--bg-secondary);
		border: 1px solid var(--border-color);
		color: var(--text-secondary);
		cursor: pointer;
		transition: all 0.18s ease;
		font-size: 14px;
		font-weight: 700;
		border-radius: 12px;
		margin-left: auto;
	}

	.upload-btn:hover:not(:disabled) {
		color: var(--text-primary);
		border-color: var(--border-hover);
		background: var(--bg-primary);
	}

	.upload-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.upload-btn svg {
		width: 14px;
		height: 14px;
		flex-shrink: 0;
	}

	.upload-progress-text {
		font-size: 12px;
		font-weight: 700;
		letter-spacing: 0.08em;
	}

	.file-input {
		display: none;
	}

	.editor-content {
		/* border: 1px solid var(--border-color); */
		border: none;
		border-radius: 0 0 16px 16px;
		min-height: 180px;
		overflow: hidden;
		position: relative;
		background: var(--bg-primary);
	}

	.editor-content.dragging {
		border-color: var(--link-color);
		background: linear-gradient(135deg, rgba(228, 87, 46, 0.08), rgba(228, 87, 46, 0.08));
	}

	.drag-overlay {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: rgba(0, 0, 0, 0.05);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 12px;
		z-index: 10;
		border: 2px dashed var(--link-color);
		border-radius: 12px;
		margin: 12px;
	}

	.drag-overlay svg {
		color: var(--link-color);
	}

	.drag-overlay p {
		margin: 0;
		color: var(--link-color);
		font-weight: 700;
		font-size: 16px;
		letter-spacing: 0.04em;
	}

	.content-textarea {
		width: 100%;
		padding: 14px;
		border: none;
		font-size: 14px;
		font-family: var(--font-mono);
		resize: vertical;
		box-sizing: border-box;
		background: var(--bg-primary);
		color: var(--text-primary);
		min-height: 180px;
		outline: none;
		line-height: 1.55;
	}

	.preview-content {
		padding: 16px;
		background: var(--bg-primary);
		min-height: 180px;
		color: var(--text-primary);
		line-height: 1.6;
		font-size: 14px;
	}

	.preview-content :global(*) {
		color: var(--text-primary);
	}

	.preview-content :global(h1),
	.preview-content :global(h2),
	.preview-content :global(h3) {
		color: var(--text-primary);
		margin-top: 16px;
		margin-bottom: 8px;
		font-weight: 800;
	}

	.preview-content :global(h1) {
		font-size: 20px;
	}

	.preview-content :global(h2) {
		font-size: 18px;
	}

	.preview-content :global(h3) {
		font-size: 16px;
	}

	.preview-content :global(p) {
		margin: 0 0 12px 0;
	}

	.preview-content :global(p:last-child) {
		margin-bottom: 0;
	}

	.preview-content :global(a) {
		color: var(--link-color);
		text-decoration: none;
	}

	.preview-content :global(a:hover) {
		text-decoration: underline;
	}

	.preview-content :global(ul),
	.preview-content :global(ol) {
		margin: 0 0 12px 0;
		padding-left: 24px;
	}

	.preview-content :global(li) {
		margin-bottom: 4px;
	}

	.preview-content :global(code) {
		background-color: var(--bg-tertiary);
		padding: 2px 6px;
		border-radius: 8px;
		font-family: var(--font-mono);
		font-size: 13px;
	}

	.preview-content :global(pre) {
		background-color: var(--bg-tertiary);
		padding: 12px;
		border-radius: 10px;
		overflow-x: auto;
		margin: 12px 0;
		border: 1px solid var(--border-color);
	}

	.preview-content :global(pre code) {
		background-color: transparent;
		padding: 0;
		display: block;
		overflow-x: auto;
	}

	.preview-content :global(blockquote) {
		border-left: 3px solid var(--border-color);
		padding-left: 12px;
		margin: 12px 0;
		color: var(--text-secondary);
	}

	.preview-content :global(img) {
		max-width: 100%;
		height: auto;
		border-radius: 10px;
		margin: 12px 0;
		box-shadow: 0 8px 20px var(--shadow);
	}

	.preview-content :global(iframe) {
		max-width: 100%;
		width: 100%;
		height: 315px;
		border-radius: 10px;
		margin: 16px 0;
		border: 1px solid var(--border-color);
		box-shadow: 0 10px 22px var(--shadow);
	}

	.preview-content :global(video) {
		max-width: 100%;
		width: 100%;
		border-radius: 10px;
		margin: 16px 0;
		border: 1px solid var(--border-color);
		box-shadow: 0 10px 22px var(--shadow);
	}

	@media (min-width: 640px) {
		.preview-content :global(iframe) {
			height: 400px;
		}
	}

</style>
