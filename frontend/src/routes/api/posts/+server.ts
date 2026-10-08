import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { backendClient, mapPost } from '$lib/server/backend';

async function resolveTopicName(topicId: number | null | undefined) {
	if (topicId === null || topicId === undefined) return null;
	const api = backendClient();
	const res = await api.get('/topics/');
	const topics = (res.data ?? []) as Array<{ name: string }>;
	const sorted = topics.sort((a, b) => a.name.localeCompare(b.name));
	const topic = sorted[topicId - 1];
	return topic?.name ?? null;
}

export const GET: RequestHandler = async ({ url }) => {
	try {
		const api = backendClient();
		const topicIdParam = url.searchParams.get('topic_id');
		const topicId = topicIdParam ? Number(topicIdParam) : null;

		const topicName = await resolveTopicName(topicId);

		const response = await api.get('/posts/', {
			params: topicName ? { topic_name: topicName } : {}
		});

		const posts = (response.data ?? []).map(mapPost);
		return json(posts);
	} catch (error: any) {
		const status = error.response?.status ?? 500;
		const message = error.response?.data?.detail ?? 'Failed to load posts';
		return json({ error: message }, { status });
	}
};

export const POST: RequestHandler = async ({ request, cookies }) => {
	const { title, content, topic_id } = await request.json();

	const topic_name = await resolveTopicName(topic_id);
	const api = backendClient(cookies);

	try {
		const response = await api.post(
			'/posts/',
			{
				title,
				content,
				topic_name
			},
			{
				headers: { Authorization: `Bearer ${cookies.get('auth_token')}` }
			}
		);

		const post = mapPost(response.data?.result ?? response.data);
		return json(post, { status: 201 });
	} catch (error: any) {
		const status = error.response?.status ?? 500;
		const message = error.response?.data?.detail ?? 'Failed to create post';
		return json({ error: message }, { status });
	}
};
