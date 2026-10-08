<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';

	let mounted = $state(false);

	onMount(() => {
		mounted = true;
	});
</script>

<div class="welcome-page">
	<div class="background-animation">
		<div class="floating-shape shape-1"></div>
		<div class="floating-shape shape-2"></div>
		<div class="floating-shape shape-3"></div>
		<div class="floating-shape shape-4"></div>
	</div>

	<div class="top-nav" class:fade-in={mounted}>
		<button class="lets-go-btn" onclick={() => goto('/login')}>
			<span>Let's go!</span>
			<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M5 12h14" />
				<path d="M12 5l7 7-7 7" />
			</svg>
		</button>
	</div>

	<div class="welcome-container" class:fade-in={mounted}>
		<div class="welcome-header" class:slide-down={mounted}>
			<div class="logo-section">
				<div class="logo-wrapper" class:scale-in={mounted}>
					<svg width="80" height="80" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-icon">
						<path d="M8 6C5.79 6 4 7.79 4 10V16C4 18.21 5.79 20 8 20H12L16 24V20H20C22.21 20 24 18.21 24 16V10C24 7.79 22.21 6 20 6H8Z" fill="currentColor" opacity="0.15"/>
						<path d="M6 8C4.9 8 4 8.9 4 10V16C4 17.1 4.9 18 6 18H10L14 22V18H18C19.1 18 20 17.1 20 16V10C20 8.9 19.1 8 18 8H6Z" fill="currentColor"/>
						<circle cx="9" cy="13" r="1.5" fill="white"/>
						<circle cx="14" cy="13" r="1.5" fill="white"/>
						<circle cx="19" cy="13" r="1.5" fill="white"/>
					</svg>
					<div class="logo-glow"></div>
				</div>
				<h1 class="logo-text" class:slide-up={mounted}>wForum</h1>
			</div>
			<p class="tagline" class:fade-in-delay={mounted}>
				A vibrant community where ideas come to life
			</p>
		</div>

		<div class="welcome-content">
			<div class="features" class:features-visible={mounted}>
				<div class="feature" class:feature-1={mounted}>
					<div class="feature-icon-wrapper">
						<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
							<polyline points="14 2 14 8 20 8" />
							<line x1="16" y1="13" x2="8" y2="13" />
							<line x1="16" y1="17" x2="8" y2="17" />
						</svg>
						<div class="icon-pulse"></div>
					</div>
					<h3>Create & Share</h3>
					<p>Express yourself through posts, stories, and creative content. Share what matters to you.</p>
				</div>
				<div class="feature" class:feature-2={mounted}>
					<div class="feature-icon-wrapper">
						<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
						</svg>
						<div class="icon-pulse"></div>
					</div>
					<h3>Connect & Discuss</h3>
					<p>Join meaningful conversations, engage with others, and build lasting connections.</p>
				</div>
				<div class="feature" class:feature-3={mounted}>
					<div class="feature-icon-wrapper">
						<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M12 8l-6 6h12l-6-6z" />
						</svg>
						<div class="icon-pulse"></div>
					</div>
					<h3>Discover & Explore</h3>
					<p>Find amazing content, vote on what you love, and discover new perspectives.</p>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.welcome-page {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
		overflow: hidden;
		background: var(--bg-secondary);
		padding: 48px 20px 36px;
	}

	.top-nav {
		position: fixed;
		top: 24px;
		right: 24px;
		display: flex;
		z-index: 100;
		opacity: 0;
		transition: opacity 0.8s ease-out 0.2s;
	}

	.top-nav.fade-in {
		opacity: 1;
	}

	.lets-go-btn {
		display: inline-flex;
		align-items: center;
		gap: 10px;
		padding: 12px 18px;
		background: var(--link-color);
		border: 1px solid var(--border-color);
		border-radius: 14px;
		color: var(--text-inverse);
		font-size: 14px;
		font-weight: 900;
		cursor: pointer;
		transition: all 0.3s ease;
		letter-spacing: 0.08em;
		box-shadow: 0 14px 30px var(--shadow);
		text-transform: uppercase;
	}

	.lets-go-btn:hover {
		transform: translateY(-2px);
		box-shadow: 0 18px 40px var(--shadow-hover);
	}

	.lets-go-btn:active {
		transform: translateY(0);
	}

	.lets-go-btn svg {
		transition: transform 0.3s ease;
		flex-shrink: 0;
	}

	.lets-go-btn:hover svg {
		transform: translateX(6px);
	}

	.background-animation {
		display: none;
	}

	.welcome-container {
		max-width: 1100px;
		width: 100%;
		text-align: center;
		position: relative;
		z-index: 1;
		opacity: 0;
		transition: opacity 0.8s ease-out;
	}

	.welcome-container.fade-in {
		opacity: 1;
	}

	.welcome-header {
		margin-bottom: 52px;
	}

	.logo-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 22px;
		margin-bottom: 28px;
	}

	.logo-wrapper {
		position: relative;
		transform: scale(0);
		transition: transform 0.8s cubic-bezier(0.34, 1.56, 0.64, 1);
	}

	.logo-wrapper.scale-in {
		transform: scale(1);
	}

	.logo-icon {
		color: var(--accent);
		filter: drop-shadow(0 4px 10px rgba(0, 0, 0, 0.18));
		animation: logo-rotate 18s linear infinite;
		position: relative;
		z-index: 2;
	}

	@keyframes logo-rotate {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}

	.logo-glow {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 110px;
		height: 110px;
		background: radial-gradient(circle, rgba(228, 87, 46, 0.2) 0%, transparent 70%);
		opacity: 0.25;
		animation: pulse-glow 2s ease-in-out infinite;
		border-radius: 24px;
		z-index: 1;
		filter: blur(6px);
	}

	@keyframes pulse-glow {
		0%,
		100% {
			transform: translate(-50%, -50%) scale(1);
			opacity: 0.35;
		}
		50% {
			transform: translate(-50%, -50%) scale(1.18);
			opacity: 0.55;
		}
	}

	.logo-text {
		font-size: 56px;
		font-weight: 900;
		color: var(--text-primary);
		margin: 0;
		letter-spacing: -0.08em;
		opacity: 0;
		transform: translateY(20px);
		transition: all 0.8s ease-out 0.2s;
	}

	.logo-text.slide-up {
		opacity: 1;
		transform: translateY(0);
	}

	.tagline {
		font-size: 20px;
		color: var(--text-secondary);
		margin: 0;
		font-weight: 500;
		opacity: 0;
		transform: translateY(10px);
		transition: all 0.8s ease-out 0.4s;
		letter-spacing: 0.01em;
	}

	.tagline.fade-in-delay {
		opacity: 1;
		transform: translateY(0);
	}

	.welcome-header.slide-down {
		animation: slideDown 0.8s ease-out;
	}

	@keyframes slideDown {
		from {
			opacity: 0;
			transform: translateY(-30px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.welcome-content {
		display: flex;
		flex-direction: column;
		gap: 48px;
	}

	.features {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 28px;
		margin-bottom: 16px;
		opacity: 0;
		transform: translateY(30px);
		transition: all 0.8s ease-out 0.6s;
	}

	.features.features-visible {
		opacity: 1;
		transform: translateY(0);
	}

	.feature {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 16px;
		padding: 32px 28px;
		background: var(--bg-primary);
		border: 1px solid var(--border-color);
		border-radius: 18px;
		transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
		position: relative;
		overflow: hidden;
		opacity: 0;
		transform: translateY(30px) scale(0.95);
		box-shadow: 0 12px 26px var(--shadow);
	}

	.feature::before {
		content: '';
		position: absolute;
		top: -60px;
		right: -60px;
		width: 140px;
		height: 140px;
		background: radial-gradient(circle, rgba(228, 87, 46, 0.16), transparent 60%);
		transform: scale(0);
		transition: transform 0.4s ease;
		z-index: 0;
	}

	.feature:hover {
		border-color: var(--border-hover);
		box-shadow: 0 16px 36px var(--shadow-hover);
		transform: translateY(-4px);
	}

	.feature:hover::before {
		transform: scale(1);
	}

	.feature-1 {
		animation: featureFadeIn 0.8s ease-out 0.8s forwards;
	}

	.feature-2 {
		animation: featureFadeIn 0.8s ease-out 1s forwards;
	}

	.feature-3 {
		animation: featureFadeIn 0.8s ease-out 1.2s forwards;
	}

	@keyframes featureFadeIn {
		to {
			opacity: 1;
			transform: translateY(0) scale(1);
		}
	}

	.feature-icon-wrapper {
		position: relative;
		width: 80px;
		height: 80px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
		border-radius: 20px;
		transition: all 0.3s ease;
		box-shadow: 0 8px 18px rgba(0, 0, 0, 0.15);
	}

	.feature:hover .feature-icon-wrapper {
		transform: scale(1.05);
		box-shadow: 0 12px 26px rgba(228, 87, 46, 0.35);
	}

	.feature-icon-wrapper svg {
		color: white;
		position: relative;
		z-index: 2;
	}

	.icon-pulse {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		width: 100%;
		height: 100%;
		border-radius: 20px;
		background: var(--accent);
		opacity: 0.5;
		animation: iconPulse 2s ease-in-out infinite;
	}

	@keyframes iconPulse {
		0%,
		100% {
			transform: translate(-50%, -50%) scale(1);
			opacity: 0.5;
		}
		50% {
			transform: translate(-50%, -50%) scale(1.3);
			opacity: 0;
		}
	}

	.feature h3 {
		margin: 0;
		font-size: 18px;
		font-weight: 800;
		color: var(--text-primary);
		letter-spacing: -0.01em;
	}

	.feature p {
		margin: 0;
		font-size: 14px;
		color: var(--text-secondary);
		line-height: 1.6;
	}

	@media (max-width: 768px) {
		.logo-text {
			font-size: 44px;
		}

		.tagline {
			font-size: 18px;
		}

		.features {
			grid-template-columns: 1fr;
			gap: 24px;
		}

		.feature {
			padding: 28px 22px;
		}

		.top-nav {
			top: 16px;
			right: 16px;
		}

		.lets-go-btn {
			font-size: 13px;
			padding: 10px 14px;
			gap: 6px;
		}
	}
</style>
