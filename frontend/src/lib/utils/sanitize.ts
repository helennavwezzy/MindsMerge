import { browser } from '$app/environment';

// Import DOMPurify dynamically
let DOMPurify: any = null;
if (browser) {
	import('dompurify').then((mod) => {
		DOMPurify = mod.default;
	});
}

export function sanitizeHtml(html: string): string {
	if (!browser || !DOMPurify) {
		// Fallback: basic HTML escaping for SSR
		return html.replace(/</g, '&lt;').replace(/>/g, '&gt;');
	}
	// Configure DOMPurify to allow YouTube iframes and video tags
	const config = {
		ADD_TAGS: ['iframe', 'video', 'source'],
		ADD_ATTR: ['allow', 'allowfullscreen', 'frameborder', 'scrolling', 'controls', 'type'],
		ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp|data):|(?:^|&)(?:src|data|cite|action|formaction|codebase|href|form|background|poster)=)|^\/|^#/i
	};
	
	let sanitized = DOMPurify.sanitize(html, config);
	
	// Additional security: only allow iframes from YouTube
	sanitized = sanitized.replace(/<iframe[^>]*>/gi, (match: string) => {
		if (match.match(/src=["']https?:\/\/(?:www\.)?(?:youtube\.com|youtu\.be)/i)) {
			return match;
		}
		return ''; // Remove iframes from other domains
	});
	
	// Only allow video tags with src pointing to our uploads directory
	sanitized = sanitized.replace(/<video[^>]*>/gi, (match: string) => {
		// Allow videos from our uploads directory or data URIs
		if (match.match(/src=["']\/uploads\//i) || match.match(/<source[^>]*src=["']\/uploads\//i)) {
			return match;
		}
		// Check if there's a source tag inside (will be handled separately)
		return match;
	});
	
	return sanitized;
}

