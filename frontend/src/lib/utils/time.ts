/**
 * Formats a timestamp string into a relative time string (e.g., "2h", "5m", "now")
 * Properly handles UTC timestamps from SQLite database
 */
export function formatRelativeTime(dateString: string): string {
	if (!dateString) return 'now';
	
	let date: Date;
	const normalized = dateString.trim();
	
	// SQLite returns timestamps in format "YYYY-MM-DD HH:MM:SS" (space-separated, UTC)
	// Check if it's SQLite format (has space instead of 'T')
	if (normalized.match(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/)) {
		// Convert SQLite format to ISO format and treat as UTC
		date = new Date(normalized.replace(' ', 'T') + 'Z');
	} else if (!normalized.includes('T') && normalized.match(/^\d{4}-\d{2}-\d{2}$/)) {
		// Just a date, no time
		date = new Date(normalized + 'T00:00:00Z');
	} else if (normalized.includes('T')) {
		// ISO format with 'T'
		if (!normalized.endsWith('Z') && !normalized.match(/[+-]\d{2}:?\d{2}$/)) {
			// No timezone info, treat as UTC
			date = new Date(normalized + 'Z');
		} else {
			// Has timezone info, parse normally
			date = new Date(normalized);
		}
	} else {
		// Try parsing as-is (fallback)
		date = new Date(normalized);
	}
	
	// Check if date is valid
	if (isNaN(date.getTime())) {
		return 'now';
	}
	
	const now = new Date();
	const diff = now.getTime() - date.getTime();
	
	// Handle negative differences (future dates) by returning 'now'
	if (diff < 0) {
		return 'now';
	}
	
	const seconds = Math.floor(diff / 1000);
	const minutes = Math.floor(seconds / 60);
	const hours = Math.floor(minutes / 60);
	const days = Math.floor(hours / 24);
	
	if (days > 0) return `${days}d`;
	if (hours > 0) return `${hours}h`;
	if (minutes > 0) return `${minutes}m`;
	if (seconds > 0) return `${seconds}s`;
	return 'now';
}

/**
 * Formats a date string to a locale date string
 * Properly handles UTC timestamps from SQLite database
 */
export function formatDate(dateString: string): string {
	if (!dateString) return '';
	
	let date: Date;
	const normalized = dateString.trim();
	
	// SQLite returns timestamps in format "YYYY-MM-DD HH:MM:SS" (space-separated, UTC)
	if (normalized.match(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/)) {
		// Convert SQLite format to ISO format and treat as UTC
		date = new Date(normalized.replace(' ', 'T') + 'Z');
	} else if (!normalized.includes('T') && normalized.match(/^\d{4}-\d{2}-\d{2}$/)) {
		// Just a date, no time
		date = new Date(normalized + 'T00:00:00Z');
	} else if (normalized.includes('T')) {
		// ISO format with 'T'
		if (!normalized.endsWith('Z') && !normalized.match(/[+-]\d{2}:?\d{2}$/)) {
			// No timezone info, treat as UTC
			date = new Date(normalized + 'Z');
		} else {
			// Has timezone info, parse normally
			date = new Date(normalized);
		}
	} else {
		// Try parsing as-is (fallback)
		date = new Date(normalized);
	}
	
	// Check if date is valid
	if (isNaN(date.getTime())) {
		return '';
	}
	
	return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
}

