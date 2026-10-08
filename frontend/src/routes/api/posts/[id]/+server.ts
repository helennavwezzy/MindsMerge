import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { backendClient, mapPost } from '$lib/server/backend';

export const GET: RequestHandler = async ({ params }) => {
	const api = backendClient();

	try {
		const response = await api.get(`/posts/${params.id}`);
		const post = mapPost(response.data?.result ?? response.data);
		return json(post);
	} catch (error: any) {
		const status = error.response?.status ?? 500;
		const message = error.response?.data?.detail ?? 'Failed to load post';
		return json({ error: message }, { status });
	}
};
