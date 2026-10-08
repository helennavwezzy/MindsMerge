<script lang="ts">
	import UserMenu from './UserMenu.svelte';

	let searchQuery = $state('');

	function handleSearch(e: Event) {
		e.preventDefault();
		if (searchQuery.trim()) {
			// TODO: Implement search functionality
			console.log('Searching for:', searchQuery);
		}
	}
</script>

<nav class="topbar">
	<div class="topbar-content">
		<div class="logo-section">
			<a href="/" class="logo">
				<svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
					<path d="M8 6C5.79 6 4 7.79 4 10V16C4 18.21 5.79 20 8 20H12L16 24V20H20C22.21 20 24 18.21 24 16V10C24 7.79 22.21 6 20 6H8Z" fill="currentColor" opacity="0.15"/>
					<path d="M6 8C4.9 8 4 8.9 4 10V16C4 17.1 4.9 18 6 18H10L14 22V18H18C19.1 18 20 17.1 20 16V10C20 8.9 19.1 8 18 8H6Z" fill="currentColor"/>
					<circle cx="9" cy="13" r="1.5" fill="white"/>
					<circle cx="14" cy="13" r="1.5" fill="white"/>
					<circle cx="19" cy="13" r="1.5" fill="white"/>
				</svg>
				<span class="logo-text">wForum</span>
			</a>
		</div>
		<div class="search-section">
			<form onsubmit={handleSearch} class="search-form">
				<input
					type="text"
					placeholder="Search posts..."
					bind:value={searchQuery}
					class="search-input"
				/>
				<button type="submit" class="search-btn" aria-label="Search">
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<circle cx="11" cy="11" r="8" />
						<path d="m21 21-4.35-4.35" />
					</svg>
				</button>
			</form>
		</div>
		<div class="actions">
			<UserMenu />
		</div>
	</div>
</nav>

<style>
	.topbar {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		height: var(--topbar-height);
		background: var(--bg-primary);
		border-bottom: 1px solid var(--border-color);
		z-index: 1000;
		box-shadow: 0 6px 20px var(--shadow);
		backdrop-filter: blur(8px);
	}

	.topbar-content {
		display: flex;
		align-items: center;
		justify-content: space-between;
		height: 100%;
		padding: 0 24px;
		gap: 16px;
	}

	.logo-section {
		display: flex;
		align-items: center;
		flex-shrink: 0;
	}

	.logo {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		text-decoration: none;
		color: var(--text-primary);
		font-weight: 800;
		font-size: 22px;
		letter-spacing: -0.04em;
		position: relative;
		transition: transform 0.2s ease, color 0.2s ease;
	}

	.logo::after {
		content: '';
		position: absolute;
		inset: -6px -10px;
		background: radial-gradient(circle at 20% 20%, rgba(228, 87, 46, 0.1), transparent 60%);
		border-radius: 14px;
		opacity: 0;
		transition: opacity 0.2s ease;
		z-index: -1;
	}

	.logo:hover {
		transform: translateY(-1px);
	}

	.logo:hover::after {
		opacity: 1;
	}

	.logo svg {
		color: var(--accent);
		flex-shrink: 0;
		filter: drop-shadow(0 6px 12px rgba(228, 87, 46, 0.25));
	}

	.logo-text {
		letter-spacing: -0.04em;
	}

	.search-section {
		flex: 1;
		max-width: 640px;
	}

	.search-form {
		display: flex;
		align-items: center;
		width: 100%;
		position: relative;
		padding: 0 8px;
		border-radius: 8px;
		border: 1px solid var(--border-color);
		background: var(--bg-secondary);
		box-shadow: 0 4px 12px var(--shadow);
		transition: border-color 0.2s ease, box-shadow 0.2s ease;
	}

	.search-form:focus-within {
		border-color: var(--link-color);
		box-shadow: 0 16px 40px var(--shadow-hover);
		transform: translateY(-1px);
	}

	.search-input {
		width: 100%;
		padding: 12px 44px 12px 8px;
		background: transparent;
		border: none;
		border-radius: 12px;
		font-size: 14px;
		color: var(--text-primary);
		transition: color 0.2s ease;
	}

	.search-input:focus {
		outline: none;
	}

	.search-input::placeholder {
		color: var(--text-tertiary);
	}

	.search-btn {
		position: absolute;
		right: 6px;
		display: flex;
		align-items: center;
		justify-content: center;
		width: 32px;
		height: 32px;
		padding: 0;
		background: transparent;
		border: 1px solid var(--border-color);
		border-radius: 10px;
		color: var(--text-secondary);
		cursor: pointer;
		transition: all 0.15s ease;
		box-shadow: none;
	}

	.search-btn:hover {
		color: var(--link-color);
		transform: translateY(-1px);
	}

	.search-btn svg {
		width: 18px;
		height: 18px;
	}

	.actions {
		display: flex;
		align-items: center;
		gap: 8px;
		flex-shrink: 0;
	}
</style>
