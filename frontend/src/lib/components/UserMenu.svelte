<script lang="ts">
	import { user } from '$lib/stores/user';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import Avatar from './Avatar.svelte';

	let showDropdown = $state(false);
	let currentUser = $state<any>(null);

	user.subscribe((u) => {
		currentUser = u;
	});

	function handleClickOutside(event: MouseEvent) {
		const target = event.target as HTMLElement;
		if (!target.closest('.user-menu')) {
			showDropdown = false;
		}
	}

	onMount(() => {
		document.addEventListener('click', handleClickOutside);
		return () => {
			document.removeEventListener('click', handleClickOutside);
		};
	});

	async function handleLogout() {
		await user.logout();
		showDropdown = false;
	}

	function handleProfile() {
		if (currentUser) {
			goto(`/users/${currentUser.username}`);
			showDropdown = false;
		}
	}
</script>

{#if currentUser}
	<div class="user-menu">
		<button class="user-avatar-btn" onclick={() => (showDropdown = !showDropdown)}>
			<Avatar username={currentUser.username} kind={currentUser.kind} size="medium" class="avatar" />
		</button>

		{#if showDropdown}
			<div class="dropdown">
				<div class="dropdown-header">
					<div class="user-info">
						<Avatar username={currentUser.username} kind={currentUser.kind} size="medium" class="dropdown-avatar" />
						<div class="user-details">
							<div class="username">u/{currentUser.username}</div>
							<div class="email">{currentUser.email}</div>
						</div>
					</div>
				</div>
				<div class="dropdown-divider"></div>
				<div class="dropdown-items">
					<button class="dropdown-item" onclick={handleProfile}>
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
							<circle cx="12" cy="7" r="4" />
						</svg>
						<span>My Profile</span>
					</button>
					<button class="dropdown-item logout" onclick={handleLogout}>
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
							<polyline points="16 17 21 12 16 7" />
							<line x1="21" y1="12" x2="9" y2="12" />
						</svg>
						<span>Logout</span>
					</button>
				</div>
			</div>
		{/if}
	</div>
{:else}
	<div class="auth-links">
		<a href="/login" class="auth-link">Log in</a>
		<a href="/signup" class="auth-link signup">Sign up</a>
	</div>
{/if}

<style>
	.user-menu {
		position: relative;
	}

	.user-avatar-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2px;
		background: var(--bg-secondary);
		border: 1px solid var(--border-color);
		border-radius: 14px;
		cursor: pointer;
		transition: all 0.18s ease;
		box-shadow: 0 6px 16px var(--shadow);
	}

	.user-avatar-btn:hover {
		transform: translateY(-1px);
		border-color: var(--border-hover);
		box-shadow: 0 12px 28px var(--shadow-hover);
	}

	.dropdown {
		position: absolute;
		top: calc(100% + 10px);
		right: 0;
		width: 260px;
		background: var(--bg-primary);
		border: 1px solid var(--border-color);
		border-radius: 16px;
		box-shadow: 0 18px 48px var(--shadow-hover);
		z-index: 1000;
		overflow: hidden;
		backdrop-filter: blur(12px);
	}

	.dropdown-header {
		padding: 14px;
		background: var(--bg-secondary);
	}

	.user-info {
		display: flex;
		align-items: center;
		gap: 12px;
	}


	.user-details {
		flex: 1;
		min-width: 0;
	}

	.username {
		font-weight: 700;
		color: var(--text-primary);
		font-size: 14px;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.email {
		font-size: 12px;
		color: var(--text-secondary);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		margin-top: 2px;
	}

	.dropdown-divider {
		height: 1px;
		background: linear-gradient(90deg, rgba(228, 87, 46, 0), rgba(228, 87, 46, 0.4), rgba(228, 87, 46, 0));
		margin: 6px 0;
	}

	.dropdown-items {
		padding: 6px;
		display: grid;
		gap: 6px;
	}

	.dropdown-item {
		display: flex;
		align-items: center;
		gap: 12px;
		width: 100%;
		padding: 10px 12px;
		background: transparent;
		border: 1px solid transparent;
		border-radius: 12px;
		font-size: 14px;
		color: var(--text-primary);
		cursor: pointer;
		transition: all 0.18s ease;
		text-align: left;
	}

	.dropdown-item:hover {
		background: var(--bg-secondary);
		border-color: var(--border-hover);
	}

	.dropdown-item svg {
		width: 16px;
		height: 16px;
		flex-shrink: 0;
		color: var(--text-secondary);
	}

	.dropdown-item.logout {
		color: var(--accent);
	}

	.dropdown-item.logout svg {
		color: var(--accent);
	}

	.auth-links {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.auth-link {
		padding: 8px 14px;
		border-radius: 12px;
		font-size: 14px;
		font-weight: 800;
		text-decoration: none;
		transition: all 0.18s ease;
		letter-spacing: 0.04em;
		text-transform: uppercase;
	}

	.auth-link:not(.signup) {
		color: var(--text-secondary);
		background: transparent;
		border: 1px solid var(--border-color);
	}

	.auth-link:not(.signup):hover {
		color: var(--text-primary);
		background: linear-gradient(135deg, rgba(228, 87, 46, 0.1), rgba(228, 87, 46, 0.08));
		border-color: var(--border-hover);
		transform: translateY(-1px);
	}

	.auth-link.signup {
		background: var(--link-color);
		color: var(--text-inverse);
		box-shadow: 0 8px 18px var(--shadow);
	}

	.auth-link.signup:hover {
		transform: translateY(-1px);
		box-shadow: 0 16px 36px var(--shadow-hover);
	}
</style>
