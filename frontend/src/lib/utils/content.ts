import { renderMarkdown } from './markdown';
import { sanitizeHtml } from './sanitize';

/**
 * Renders markdown content to sanitized HTML
 * This is a convenience function that combines renderMarkdown and sanitizeHtml
 */
export function renderMarkdownContent(markdown: string): string {
	return sanitizeHtml(renderMarkdown(markdown));
}

