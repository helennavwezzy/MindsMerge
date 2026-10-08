import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { backendClient } from '$lib/server/backend';

export const GET: RequestHandler = async ({ cookies }) => {
	const token = cookies.get('auth_token');

	if (!token) {
		return json({ user: null });
	}

	try {
		const api = backendClient(cookies);
		const response = await api.get('/users/me');
		const user = response.data;
		return json({
			user: {
				...user,
				username: user.name
			}
		});
	} catch (error) {
		cookies.delete('auth_token', { path: '/' });
		return json({ user: null });
	}
};
