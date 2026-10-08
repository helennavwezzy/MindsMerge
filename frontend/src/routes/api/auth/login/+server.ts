import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { backendClient } from '$lib/server/backend';

export const POST: RequestHandler = async ({ request, cookies }) => {
	const { username, password } = await request.json();

	if (!username || !password) {
		return json({ error: 'Username and password are required' }, { status: 400 });
	}

	try {
		const api = backendClient();
		const response = await api.post('/auth/login', {
			username: username,
			password
		});

		const payload = response.data?.result ?? response.data;
		const access_token = payload?.access_token;
		const user = payload?.user;

		if (!access_token || !user) {
			return json({ error: 'Invalid response from server' }, { status: 502 });
		}

		// Persist JWT for subsequent API calls
		cookies.set('auth_token', access_token, {
			path: '/',
			httpOnly: true,
			sameSite: 'lax',
			secure: process.env.NODE_ENV === 'production',
			maxAge: 60 * 60 * 24 * 7
		});

		return json({ user: { ...user, username: user.name } });
	} catch (error: any) {
		const status = error.response?.status ?? 500;
		const message =
			error.response?.data?.detail ?? error.response?.data?.message ?? 'Login failed';
		return json({ error: message }, { status });
	}
};
