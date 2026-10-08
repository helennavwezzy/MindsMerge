import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';

// Helper function to convert YouTube URLs to embed format
function convertYouTubeUrl(url: string): string {
	const patterns = [
		/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
		/youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})/
	];
	
	for (const pattern of patterns) {
		const match = url.match(pattern);
		if (match) {
			return `https://www.youtube.com/embed/${match[1]}`;
		}
	}
	return url;
}

// Configure marked with syntax highlighting
marked.setOptions({
	breaks: true,
	gfm: true
});

// Configure custom renderer for code blocks with syntax highlighting
marked.use({
	renderer: {
		code(token: any) {
			const text = token.text || '';
			const lang = token.lang || '';
			
			if (!text) {
				return `<pre><code></code></pre>`;
			}
			
			let highlighted = text;
			if (lang && hljs.getLanguage(lang)) {
				try {
					highlighted = hljs.highlight(text, { language: lang }).value;
				} catch (err) {
					console.error('Highlight error:', err);
					highlighted = text;
				}
			} else if (text.trim()) {
				// Auto-detect language if not specified
				try {
					highlighted = hljs.highlightAuto(text).value;
				} catch (err) {
					// Use text as-is if highlighting fails
					highlighted = text;
				}
			}
			
			const langClass = lang ? ` language-${lang}` : '';
			return `<pre><code class="hljs${langClass}">${highlighted}</code></pre>`;
		}
	}
});

// Function to convert YouTube links in HTML to embeds
export function convertYouTubeLinks(html: string): string {
	// Match YouTube links in anchor tags
	const youtubeLinkRegex = /<a[^>]+href=["'](https?:\/\/(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})[^"']*)["'][^>]*>([^<]*)<\/a>/gi;
	
	return html.replace(youtubeLinkRegex, (match, url) => {
		const embedUrl = convertYouTubeUrl(url);
		return `<iframe width="560" height="315" src="${embedUrl}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>`;
	});
}

// Function to render markdown to HTML
export function renderMarkdown(markdown: string): string {
	const html = marked.parse(markdown) as string;
	return convertYouTubeLinks(html);
}

