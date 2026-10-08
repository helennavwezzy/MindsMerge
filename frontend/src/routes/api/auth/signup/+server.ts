import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { backendClient } from '$lib/server/backend';

export const POST: RequestHandler = async ({ request, cookies }) => {
	const { username, email, password } = await request.json();

	try {
		const api = backendClient();
		const response = await api.post('/auth/signup', {
			username: username,
			email,
			password
		});

		const signupPayload = response.data?.result ?? response.data;
		const user = signupPayload ?? {};

		// Auto-login to match previous behavior
		const login = await api.post('/auth/login', {
			username: username,
			password
		});

		const loginPayload = login.data?.result ?? login.data;
		const access_token = loginPayload?.access_token;

		if (!access_token) {
			return json({ error: 'Failed to obtain access token' }, { status: 502 });
		}

		cookies.set('auth_token', access_token, {
			path: '/',
			httpOnly: true,
			sameSite: 'lax',
			secure: process.env.NODE_ENV === 'production',
			maxAge: 60 * 60 * 24 * 7
		});

		const responseUser = loginPayload?.user ?? user;
		const normalizedUser = responseUser
			? { ...responseUser, username: responseUser.name }
			: { username };

		return json({ user: normalizedUser }, { status: 201 });
	} catch (error: any) {
		const status = error.response?.status ?? 500;
		const message = error.response?.data?.detail ?? 'Signup failed';
		return json({ error: message }, { status });
	}
};
