import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { backendClient } from '$lib/server/backend';

export const GET: RequestHandler = async ({ params }) => {
	const api = backendClient();
	try {
		const response = await api.get(`/users/${params.name}`);
		const user = response.data;
		return json({
			...user,
			username: user.name,
			stats: user.stats ?? {}
		});
	} catch (error: any) {
		const status = error.response?.status ?? 500;
		const message = error.response?.data?.detail ?? 'User not found';
		return json({ error: message }, { status });
	}
};

export const PATCH: RequestHandler = async ({ params, request, cookies }) => {
	const api = backendClient(cookies);
	const body = await request.json();

	try {
		const response = await api.patch(
			'/users/me',
			{
				bio: body.bio,
				avatar_url: body.avatar_url,
				remove_avatar: body.avatar_url === null
			},
			{
				headers: { Authorization: `Bearer ${cookies.get('auth_token')}` }
			}
		);
		const user = response.data?.result ?? response.data;
		return json({ ...user, username: user.name });
	} catch (error: any) {
		const status = error.response?.status ?? 500;
		const message = error.response?.data?.detail ?? 'Failed to update profile';
		return json({ error: message }, { status });
	}
};
