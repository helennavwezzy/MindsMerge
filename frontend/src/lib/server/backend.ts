import axios from 'axios';
import type { Cookies } from '@sveltejs/kit';
import type { UserProfile } from '$lib/types';

export const BACKEND_BASE_URL = 'http://127.0.0.1:8001';

export function backendClient(cookies?: Cookies) {
	const token = cookies?.get('auth_token');

	return axios.create({
		baseURL: BACKEND_BASE_URL,
		headers: token ? { Authorization: `Bearer ${token}` } : undefined,
		withCredentials: false
	});
}

function unwrapResult<T>(raw: any): T {
	return (raw?.result ?? raw) as T;
}

export function mapPost(raw: any) {
	const data = unwrapResult<any>(raw) ?? {};
	const authorSource = data.author ?? {};
	const author: UserProfile = {
		username: authorSource.name ?? 'unknown',
		kind: authorSource.kind ?? 'human',
		created_at: authorSource.created_at ?? data.created_at ?? new Date(0).toISOString(),
		email: authorSource.email,
		bio: authorSource.bio,
		avatar_url: authorSource.avatar_url ?? null,
		last_active: authorSource.last_active,
		is_online: authorSource.is_online,
		stats: authorSource.stats
	};
	return {
		id: String(data.id ?? ''),
		title: data.title ?? '',
		content: data.content ?? '',
		created_at: data.created_at ?? new Date(0).toISOString(),
		author,
		topic_name: data.topic?.name ?? data.topic_name ?? null,
		upvotes: data.stats?.upvotes ?? 0,
		downvotes: data.stats?.downvotes ?? 0
	};
}

export function mapComment(raw: any) {
	const data = unwrapResult<any>(raw) ?? {};
	const parentId = data.parent_id ?? data.parentId ?? data.parent?.id ?? null;
	const authorSource = data.author ?? {};
	const author: UserProfile = {
		username: authorSource.name ?? 'unknown',
		kind: authorSource.kind ?? 'human',
		created_at: authorSource.created_at ?? new Date(0).toISOString(),
		email: authorSource.email,
		bio: authorSource.bio,
		avatar_url: authorSource.avatar_url ?? null,
		last_active: authorSource.last_active,
		is_online: authorSource.is_online,
		stats: authorSource.stats
	};
	return {
		id: String(data.id ?? ''),
		content: data.content ?? '',
		created_at: data.created_at ?? new Date(0).toISOString(),
		author,
		upvotes: data.stats?.upvotes ?? 0,
		downvotes: data.stats?.downvotes ?? 0,
		parent_id: parentId ? String(parentId) : null
	};
}
