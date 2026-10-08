export class ApiError extends Error {
	status: number;
	constructor(message: string, status: number) {
		super(message);
		this.name = 'ApiError';
		this.status = status;
	}
}

export async function apiFetch<T>(input: string, init: RequestInit = {}): Promise<T> {
	const response = await fetch(input, {
		headers: {
			'Content-Type': 'application/json',
			...init.headers
		},
		...init
	});

	if (!response.ok) {
		let message = 'Request failed';
		try {
			const data = await response.json();
			message = data.error || data.detail || message;
		} catch (error) {
			// swallow
		}
		throw new ApiError(message, response.status);
	}

	if (response.status === 204) {
		return undefined as T;
	}

	let r = await response.json();
	return r as T;
}

export async function safeApiFetch<T>(input: string, init?: RequestInit): Promise<T | null> {
	try {
		return await apiFetch<T>(input, init);
	} catch (error) {
		console.error('API error:', error);
		return null;
	}
}
