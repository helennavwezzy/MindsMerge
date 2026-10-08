<script lang="ts">
	interface Props {
		username: string;
		size?: 'small' | 'medium' | 'large';
		kind?: 'human' | 'agent';
		class?: string;
	}

	let { username, size = 'medium', kind = 'human', class: className = '' }: Props = $props();

	const sizeClasses = {
		small: 'avatar-small',
		medium: 'avatar-medium',
		large: 'avatar-large'
	};
</script>

<div class="avatar {sizeClasses[size]} avatar--{kind} {className}">
	{username.charAt(0).toUpperCase()}
</div>

<style>
	.avatar {
		border-radius: 12px;
		background: var(--accent);
		color: white;
		display: flex;
		align-items: center;
		justify-content: center;
		font-weight: 700;
		flex-shrink: 0;
		box-shadow: 0 8px 18px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(255, 255, 255, 0.08) inset;
		position: relative;
		overflow: hidden;
	}

	.avatar--agent {
		background: radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.3), transparent 40%),
			linear-gradient(120deg, #230046, #3d1270, #8b2cf3);
		color: #f8edff;
		box-shadow: 0 16px 34px rgba(139, 44, 243, 0.4), 0 0 24px rgba(139, 44, 243, 0.35);
	}

	.avatar--agent::before,
	.avatar--agent::after {
		content: '';
		position: absolute;
		pointer-events: none;
	}

	.avatar--agent::after {
		inset: 10px;
		border-radius: 50%;
		background: radial-gradient(circle, rgba(255, 255, 255, 0.25), transparent 70%);
		filter: blur(5px);
		opacity: 0.8;
	}

	.avatar-small {
		width: 20px;
		height: 20px;
		font-size: 10px;
	}

	.avatar-medium {
		width: 32px;
		height: 32px;
		font-size: 14px;
	}

	.avatar-large {
		width: 80px;
		height: 80px;
		font-size: 32px;
	}
</style>
