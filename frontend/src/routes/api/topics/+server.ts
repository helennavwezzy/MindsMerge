import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { backendClient } from '$lib/server/backend';

export const GET: RequestHandler = async () => {
	const api = backendClient();
	const response = await api.get('/topics/');
	const topics = (response.data ?? []) as Array<{ name: string; description: string }>;

	// Provide stable numeric IDs for the existing UI by sorting by name
	const mapped = topics
		.sort((a, b) => a.name.localeCompare(b.name))
		.map((topic, idx) => ({
			id: idx + 1,
			name: topic.name,
			description: topic.description
		}));

	return json(mapped);
};
