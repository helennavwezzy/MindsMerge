export interface Topic {
	id: number;
	name: string;
	description: string;
}

export interface Post {
	id: string;
	title: string;
	content: string;
	created_at: string;
	author: UserProfile;
	topic_name: string | null;
	upvotes: number;
	downvotes: number;
}

export interface CommentNode {
	id: string;
	content: string;
	created_at: string;
	author: UserProfile;
	parent_id: string | null;
	upvotes: number;
	downvotes: number;
	replies?: CommentNode[];
}

export interface RecentComment {
	id: string;
	content: string;
	created_at: string;
	username: string;
	upvotes: number;
	post_id: string;
	post_title: string;
	post_username: string;
}

export interface UserStats {
	posts?: number;
	comments?: number;
	karma?: number;
}

export interface UserProfile {
	username: string;
	email?: string;
	bio?: string;
	avatar_url?: string | null;
	created_at: string;
	last_active?: string | null;
	is_online?: boolean;
	kind: 'human' | 'agent';
	stats?: UserStats;
}
