import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { backendClient } from '$lib/server/backend';

export const GET: RequestHandler = async () => {
	try {
		const api = backendClient();
		const response = await api.get('/comments/', {
			params: { page: 0, limit: 20 }
		});

		const comments = (response.data ?? []).map((item: any) => {
			const parentPost = item.parent;
			const comment = item.comment;
			return {
				id: String(comment.id ?? ''),
				content: comment.content,
				created_at: comment.created_at,
				username: comment.author?.name,
				upvotes: comment.stats?.upvotes ?? 0,
				post_id: String(parentPost.id ?? ''),
				post_title: parentPost.title,
				post_username: parentPost.author?.name
			};
		});

		return json(comments);
	} catch (error: any) {
		const status = error.response?.status ?? 500;
		const message = error.response?.data?.detail ?? 'Failed to load comments';
		return json({ error: message }, { status });
	}
};
