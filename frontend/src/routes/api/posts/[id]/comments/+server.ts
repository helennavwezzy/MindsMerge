import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { backendClient, mapComment } from '$lib/server/backend';

type CommentNode = ReturnType<typeof mapComment> & { replies?: CommentNode[] };

async function hydrateReplies(api: ReturnType<typeof backendClient>, comment: CommentNode) {
	const response = await api.get(`/comments/${comment.id}/replies`);
	const replies = (response.data ?? []).map(mapComment) as CommentNode[];
	const withReplies = await Promise.all(
		replies.map(async (child: CommentNode) => {
			const hydrated: CommentNode = { ...child, replies: [] };
			hydrated.replies = await hydrateReplies(api, hydrated);
			return hydrated;
		})
	);
	return withReplies;
}

export const GET: RequestHandler = async ({ params }) => {
	try {
		const api = backendClient();
		const response = await api.get(`/posts/${params.id}/comments`);
		const comments = (response.data ?? []).map(mapComment) as CommentNode[];

		const roots = await Promise.all(
			comments.map(async (comment: CommentNode) => {
				const node: CommentNode = { ...comment, replies: [] };
				node.replies = await hydrateReplies(api, node);
				return node;
			})
		);

		return json(roots);
	} catch (error: any) {
		const status = error.response?.status ?? 500;
		const message = error.response?.data?.detail ?? 'Failed to load comments';
		return json({ error: message }, { status });
	}
};

export const POST: RequestHandler = async ({ params, request, cookies }) => {
	const { content, parent_comment_id } = await request.json();
	const api = backendClient(cookies);

	const parent_id = String(parent_comment_id ?? params.id);

	try {
		const response = await api.post(
			'/comments/',
			{
				content,
				parent_id
			},
			{
				headers: { Authorization: `Bearer ${cookies.get('auth_token')}` }
			}
		);

		const comment = mapComment(response.data?.result ?? response.data);
		return json(comment, { status: 201 });
	} catch (error: any) {
		const status = error.response?.status ?? 500;
		const message = error.response?.data?.detail ?? 'Failed to add comment';
		return json({ error: message }, { status });
	}
};
