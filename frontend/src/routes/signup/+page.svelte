<script lang="ts">
	import { user } from '$lib/stores/user';
	import { goto } from '$app/navigation';
	import { toast } from 'svelte-sonner';
	import AuthShell from '$lib/components/AuthShell.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	let username = $state('');
	let email = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let loading = $state(false);
	let error = $state('');
	let showPassword = $state(false);
	let showConfirmPassword = $state(false);

	$effect(() => {
		const unsubscribe = user.subscribe((currentUser) => {
			if (currentUser) goto('/');
		});
		return unsubscribe;
	});

	async function handleSignup(event: Event) {
		event.preventDefault();
		error = '';

		if (username.length < 3) {
			error = 'Username must be at least 3 characters';
			return;
		}

		if (password.length < 6) {
			error = 'Password must be at least 6 characters';
			return;
		}

		if (password !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}

		loading = true;

		const result = await user.signup(username, email, password);

		if (result.success) {
			toast.success('Sign up complete! Please log in.');
			goto('/login');
		} else {
			error = result.error || 'Signup failed';
			loading = false;
		}
	}
</script>

<AuthShell title="Sign up" subtitle="Create a new account to join the community.">
	<form class="auth-form" onsubmit={handleSignup}>
		{#if error}
			<p class="form-error">{error}</p>
		{/if}

		<label class="form-label" for="username">Username</label>
		<input
			id="username"
			class="input-control"
			type="text"
			placeholder="Choose a username"
			bind:value={username}
			required
			minlength="3"
			disabled={loading}
		/>

		<label class="form-label" for="email">Email</label>
		<input
			id="email"
			class="input-control"
			type="email"
			placeholder="Enter your email"
			bind:value={email}
			required
			disabled={loading}
		/>

		<label class="form-label" for="password">Password</label>
		<div class="password-field">
			<input
				id="password"
				class="input-control"
				type={showPassword ? 'text' : 'password'}
				placeholder="Create a password (min. 6 characters)"
				bind:value={password}
				required
				minlength={6}
				disabled={loading}
			/>
			<button type="button" onclick={() => (showPassword = !showPassword)}>
				{showPassword ? 'Hide' : 'Show'}
			</button>
		</div>

		<label class="form-label" for="confirmPassword">Confirm Password</label>
		<div class="password-field">
			<input
				id="confirmPassword"
				class="input-control"
				type={showConfirmPassword ? 'text' : 'password'}
				placeholder="Confirm your password"
				bind:value={confirmPassword}
				required
				disabled={loading}
			/>
			<button type="button" onclick={() => (showConfirmPassword = !showConfirmPassword)}>
				{showConfirmPassword ? 'Hide' : 'Show'}
			</button>
		</div>

		<Button type="submit" fullWidth loading={loading}>
			{loading ? 'Creating account...' : 'Sign up'}
		</Button>
	</form>

	<p class="auth-footer">
		Already have an account?
		<a href="/login">Log in</a>
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
