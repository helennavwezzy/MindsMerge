import type { RecentComment, UserProfile } from '$lib/types';
import { apiFetch } from './client';
import { fetchPosts } from './posts';
import { fetchRecentComments } from './comments';

const USERS_ENDPOINT = '/api/users';

export function fetchUserProfile(username: string) {
	return apiFetch<UserProfile>(`${USERS_ENDPOINT}/${username}`);
}

export function updateUserProfile(
	username: string,
	payload: Partial<{ bio: string | null; avatar_url: string | null }>
) {
	return apiFetch<UserProfile>(`${USERS_ENDPOINT}/${username}`, {
		method: 'PATCH',
		body: JSON.stringify(payload)
	});
}

export async function fetchUserPosts(username: string) {
	const posts = await fetchPosts(null);
	return posts.filter((post) => post.author?.username === username);
}

export async function fetchUserRecentComments(username: string, limit = 50) {
	const comments = await fetchRecentComments(limit);
	return comments.filter((comment) => comment.username === username);
}
