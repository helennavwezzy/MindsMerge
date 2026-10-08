import type { Topic } from '$lib/types';
import { apiFetch } from './client';

const TOPICS_ENDPOINT = '/api/topics';

export function fetchTopics() {
	return apiFetch<Topic[]>(TOPICS_ENDPOINT);
}
