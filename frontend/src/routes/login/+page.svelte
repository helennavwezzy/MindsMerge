<script lang="ts">
	import { user } from '$lib/stores/user';
	import { goto } from '$app/navigation';
	import AuthShell from '$lib/components/AuthShell.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	let username = $state('');
	let password = $state('');
	let loading = $state(false);
	let error = $state('');
	let showPassword = $state(false);

	$effect(() => {
		const unsubscribe = user.subscribe((currentUser) => {
			if (currentUser) {
				goto('/');
			}
		});
		return unsubscribe;
	});

	async function handleLogin(event: Event) {
		event.preventDefault();
		error = '';
		loading = true;
		const result = await user.login(username, password);
		if (!result.success) {
			error = result.error || 'Login failed';
			loading = false;
		}
	}
</script>

<AuthShell title="Log in" subtitle="Welcome back! Please log in to your account.">
	<form class="auth-form" onsubmit={handleLogin}>
		{#if error}
			<p class="form-error">{error}</p>
		{/if}

		<label class="form-label" for="username">Username</label>
		<input
			id="username"
			class="input-control"
			type="text"
			placeholder="Enter your username"
			autocomplete="username"
			bind:value={username}
			required
			disabled={loading}
		/>

		<label class="form-label" for="password">Password</label>
		<div class="password-field">
			<input
				id="password"
				class="input-control"
				type={showPassword ? 'text' : 'password'}
				placeholder="Enter your password"
				autocomplete="current-password"
				bind:value={password}
				required
				disabled={loading}
			/>
			<button type="button" onclick={() => (showPassword = !showPassword)}>
				{showPassword ? 'Hide' : 'Show'}
			</button>
		</div>

		<Button type="submit" fullWidth loading={loading}>
			{loading ? 'Logging in...' : 'Log in'}
		</Button>
	</form>

	<p class="auth-footer">
		Don't have an account?
		<a href="/signup">Sign up</a>
	</p>
</AuthShell>

<style>
	.auth-form {
		display: flex;
		flex-direction: column;
		gap: 0.9rem;
	}

	.form-label {
		font-size: 0.8rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--text-secondary);
	}

	.password-field {
		display: flex;
		gap: 0.5rem;
	}

	.auth-form .input-control {
		width: 100%;
		box-sizing: border-box;
	}

	.password-field .input-control {
		flex: 1;
		min-width: 0;
	}

	.password-field button {
		border: 1px solid var(--border-color);
		border-radius: 0.9rem;
		padding: 0 1rem;
		background: var(--bg-secondary);
		color: var(--text-secondary);
		cursor: pointer;
	}

	.form-error {
		padding: 0.75rem 1rem;
		border-radius: 0.9rem;
		background: rgba(228, 87, 46, 0.12);
		border: 1px solid rgba(228, 87, 46, 0.4);
		color: var(--accent);
		font-weight: 600;
	}

	.auth-footer {
		text-align: center;
		margin-top: 1rem;
		color: var(--text-secondary);
	}

	.auth-footer a {
		color: var(--link-color);
		text-decoration: none;
		font-weight: 700;
	}
</style>
