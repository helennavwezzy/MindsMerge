import type { CommentNode, Post } from '$lib/types';
import { apiFetch } from './client';

export interface CreatePostPayload {
	title: string;
	content: string;
	topic_id: number | null;
}

export interface CreateCommentPayload {
	content: string;
	parent_comment_id?: string | null;
}

const POSTS_ENDPOINT = '/api/posts';

export async function fetchPosts(topicId: number | null = null) {
	const url = topicId !== null ? `${POSTS_ENDPOINT}?topic_id=${topicId}` : POSTS_ENDPOINT;
	return apiFetch<Post[]>(url);
}

export async function fetchPost(postId: string) {
	return apiFetch<Post>(`${POSTS_ENDPOINT}/${postId}`);
}

export async function createPost(payload: CreatePostPayload) {
	return apiFetch<Post>(POSTS_ENDPOINT, {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}

export async function fetchPostComments(postId: string) {
	let res = apiFetch<CommentNode[]>(`${POSTS_ENDPOINT}/${postId}/comments`);
	return res;
}

export async function createPostComment(postId: string, payload: CreateCommentPayload) {
	return apiFetch(`${POSTS_ENDPOINT}/${postId}/comments`, {
		method: 'POST',
		body: JSON.stringify(payload)
	});
}
