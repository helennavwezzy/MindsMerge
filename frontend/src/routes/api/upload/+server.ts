import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { writeFile, mkdir } from 'fs/promises';
import { join } from 'path';
import { existsSync } from 'fs';
import { backendClient } from '$lib/server/backend';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
const ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/webm', 'video/ogg'];

export const POST: RequestHandler = async ({ request, cookies }) => {
	try {
		// Ensure user is authenticated
		const api = backendClient(cookies);
		await api.get('/users/me', {
			headers: { Authorization: `Bearer ${cookies.get('auth_token')}` }
		});
	} catch {
		return json({ error: 'Unauthorized' }, { status: 401 });
	}

	try {
		const formData = await request.formData();
		const file = formData.get('file') as File;

		if (!file) {
			return json({ error: 'No file provided' }, { status: 400 });
		}

		// Validate file size
		if (file.size > MAX_FILE_SIZE) {
			return json({ error: 'File size exceeds 10MB limit' }, { status: 400 });
		}

		// Validate file type
		const isImage = ALLOWED_IMAGE_TYPES.includes(file.type);
		const isVideo = ALLOWED_VIDEO_TYPES.includes(file.type);

		if (!isImage && !isVideo) {
			return json(
				{
					error: 'Invalid file type. Allowed: images (JPEG, PNG, GIF, WebP) and videos (MP4, WebM, OGG)'
				},
				{ status: 400 }
			);
		}

		// Create uploads directory if it doesn't exist
		const uploadsDir = join(process.cwd(), 'static', 'uploads');
		if (!existsSync(uploadsDir)) {
			await mkdir(uploadsDir, { recursive: true });
		}

		// Generate unique filename
		const timestamp = Date.now();
		const randomStr = Math.random().toString(36).substring(2, 15);
		const extension = file.name.split('.').pop() || '';
		const filename = `${timestamp}-${randomStr}.${extension}`;
		const filepath = join(uploadsDir, filename);

		// Save file
		const arrayBuffer = await file.arrayBuffer();
		const buffer = Buffer.from(arrayBuffer);
		await writeFile(filepath, buffer);

		// Return the URL path
		const url = `/uploads/${filename}`;
		const fileType = isImage ? 'image' : 'video';

		return json({
			url,
			filename,
			type: fileType,
			size: file.size
		});
	} catch (error) {
		console.error('Upload error:', error);
		return json({ error: 'Failed to upload file' }, { status: 500 });
	}
};
