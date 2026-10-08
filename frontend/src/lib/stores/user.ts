import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { goto } from '$app/navigation';

export interface User {
	username: string;
	email: string;
	bio: string;
	avatar_url: string;
	created_at: string;
}

function createUserStore() {
	const { subscribe, set, update } = writable<User | null>(null);

	return {
		subscribe,
		set,
	checkSession: async () => {
		if (!browser) return Promise.resolve();
		try {
			const response = await fetch('/api/auth/session');
			const data = await response.json();
			set(data.user);
			return Promise.resolve();
		} catch (error) {
			console.error('Error checking session:', error);
			set(null);
			return Promise.resolve();
		}
	},
	login: async (username: string, password: string) => {
		try {
			const response = await fetch('/api/auth/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password })
			});

			const data = await response.json();

			if (response.ok) {
				set(data.user);
					goto('/');
					return { success: true };
				} else {
					return { success: false, error: data.error || 'Login failed' };
				}
			} catch (error) {
				return { success: false, error: 'Network error' };
			}
		},
		signup: async (username: string, email: string, password: string) => {
			try {
				const response = await fetch('/api/auth/signup', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ username, email, password })
				});

				const data = await response.json();

				if (response.ok) {
					// Don't set user or redirect - let the page handle it
					return { success: true };
				} else {
					return { success: false, error: data.error || 'Signup failed' };
				}
			} catch (error) {
				return { success: false, error: 'Network error' };
			}
		},
		logout: async () => {
			try {
				await fetch('/api/auth/logout', { method: 'POST' });
				set(null);
				goto('/');
			} catch (error) {
				console.error('Error logging out:', error);
			}
		}
	};
}

export const user = createUserStore();
