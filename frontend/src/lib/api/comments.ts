import type { RecentComment } from '$lib/types';
import { apiFetch } from './client';

const RECENT_COMMENTS_ENDPOINT = '/api/recent-comments';

export function fetchRecentComments(limit?: number) {
	const url = typeof limit === 'number' ? `${RECENT_COMMENTS_ENDPOINT}?limit=${limit}` : RECENT_COMMENTS_ENDPOINT;
	return apiFetch<RecentComment[]>(url);
}
