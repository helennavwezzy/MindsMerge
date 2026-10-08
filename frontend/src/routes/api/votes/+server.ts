import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { backendClient } from '$lib/server/backend';

function normalizeVoteType(vote: any) {
	if (vote === 'novote') return 'novote';
	if (vote === 'upvote' || vote === 'downvote') return vote;
	if (vote === 1) return 'upvote';
	if (vote === -1) return 'downvote';
	return null;
}

export const POST: RequestHandler = async ({ request, cookies }) => {
	const { post_id, comment_id, vote_type } = await request.json();

	if ((!post_id && !comment_id) || (post_id && comment_id)) {
		return json({ error: 'Must provide either post_id or comment_id' }, { status: 400 });
	}

	const normalized = normalizeVoteType(vote_type);
	if (!normalized) {
		return json({ error: 'Invalid vote_type' }, { status: 400 });
	}

	const target_id = post_id ?? comment_id;
	if (!target_id) {
		return json({ error: 'Invalid target id' }, { status: 400 });
	}
	const api = backendClient(cookies);

	try {
		const response = await api.post(
			'/votes/',
			{
				target_id: String(target_id),
				vote_type: normalized
			},
			{
				headers: { Authorization: `Bearer ${cookies.get('auth_token')}` }
			}
		);

		const payload = response.data?.result ?? response.data;
		return json(payload);
	} catch (error: any) {
		const status = error.response?.status ?? 500;
		const message =
			error.response?.data?.detail ?? error.response?.data?.message ?? 'Failed to vote';
		return json({ error: message }, { status });
	}
};
