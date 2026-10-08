<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import favicon from '$lib/assets/favicon.svg';
	import Topbar from '$lib/components/Topbar.svelte';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import { user } from '$lib/stores/user';
	import { Toaster } from 'svelte-sonner';

	let { children } = $props();

	let currentUser = $state<any>(null);
	let checkingSession = $state(true);

	user.subscribe((u) => {
		currentUser = u;
		if (browser && !checkingSession) {
			handleAuthRedirect();
		}
	});

	function handleAuthRedirect() {
		const path = $page.url.pathname;
		const publicRoutes = ['/login', '/signup', '/welcome'];
		const isPublicRoute = publicRoutes.includes(path);

		if (!currentUser) {
			// Redirect to welcome if not on a public route
			if (!isPublicRoute && path !== '/') {
				goto('/welcome');
			} else if (path === '/') {
				goto('/welcome');
			}
		} else if (currentUser && path === '/welcome') {
			// Redirect logged-in users away from welcome page
			goto('/');
		}
	}

	onMount(() => {
		if (browser) {
			document.documentElement.setAttribute('data-theme', 'light');
			user.checkSession().then(() => {
				checkingSession = false;
				handleAuthRedirect();
			});
		} else {
			checkingSession = false;
		}
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{#if checkingSession}
	<div class="loading-screen">
		<div class="spinner"></div>
	</div>
{:else if !currentUser}
	{@render children()}
{:else}
<div class="app-container">
	<Topbar />
	<div class="main-content">
		<Sidebar />
		<main class="content-area">
			{@render children()}
		</main>
	</div>
</div>
{/if}

<Toaster />

<style>
	@import '$lib/styles/utilities.css';

	:global(:root) {
		--topbar-height: 64px;
		--font-sans: 'Bricolage Grotesque', 'Helvetica Neue', Arial, sans-serif;
		--font-mono: 'IBM Plex Mono', 'SFMono-Regular', Menlo, monospace;
		--bg-primary: #f7f4ec;
		--bg-secondary: #fcfbf7;
		--bg-tertiary: #ebe4d5;
		--bg-hover: #f2ecdf;
		--bg-active: #dfd3be;
		--border-color: #ded3c1;
		--border-hover: #c7b299;
		--text-primary: #1f1b16;
		--text-secondary: #544a3d;
		--text-tertiary: #857866;
		--text-inverse: #fcfbf7;
		--link-color: #1f6f9c;
		--link-hover: #124c6c;
		--accent: #e4572e;
		--accent-hover: #f0703f;
		--upvote: #e4572e;
		--downvote: #3d82b8;
		--shadow: rgba(50, 40, 25, 0.13);
		--shadow-hover: rgba(50, 40, 25, 0.24);
	}

	:global(body) {
		margin: 0;
		padding: 0;
		font-family: var(--font-sans);
		background:
			radial-gradient(circle at 15% 20%, rgba(255, 194, 150, 0.3), transparent 45%),
			radial-gradient(circle at 85% 15%, rgba(143, 210, 255, 0.32), transparent 50%),
			radial-gradient(circle at 65% 85%, rgba(203, 207, 255, 0.22), transparent 60%),
			radial-gradient(circle at 35% 85%, rgba(255, 236, 190, 0.25), transparent 55%),
			linear-gradient(180deg, #fff9f3 0%, #f4ead7 55%, #e6dcc8 100%);
		min-height: 100vh;
		color: var(--text-primary);
		transition: background-color 0.25s ease, color 0.25s ease;
		letter-spacing: -0.01em;
		-webkit-font-smoothing: antialiased;
	}

	:global(a) {
		color: var(--link-color);
		transition: color 0.2s ease;
	}

	:global(a:hover) {
		color: var(--link-hover);
	}

	.app-container {
		display: flex;
		flex-direction: column;
		min-height: 100vh;
	}

	.main-content {
		display: flex;
		flex: 1;
		margin-top: var(--topbar-height);
	}

	.content-area {
		flex: 1;
		padding: 44px;
		margin-left: 260px;
		max-width: calc(100% - 260px);
		min-height: calc(100vh - var(--topbar-height));
	}

	@media (max-width: 1024px) {
		.content-area {
			margin-left: 0;
			max-width: 100%;
			padding: 20px;
		}

	}

	.loading-screen {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 100vh;
		background-color: var(--bg-secondary);
	}

	.spinner {
		width: 40px;
		height: 40px;
		border: 3px solid rgba(0, 0, 0, 0.08);
		border-top-color: var(--link-color);
		border-radius: 999px;
		animation: spin 0.8s linear infinite;
		box-shadow: 0 10px 40px var(--shadow);
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
</style>
