import { writable } from 'svelte/store';
import { browser } from '$app/environment';

type Theme = 'light';

function createThemeStore() {
	const { subscribe, set } = writable<Theme>('light');

	if (browser) {
		document.documentElement.setAttribute('data-theme', 'light');
	}

	return {
		subscribe,
		toggle: () => {
			if (browser) {
				document.documentElement.setAttribute('data-theme', 'light');
			}
			set('light');
		},
		set: (theme: Theme) => {
			if (browser) {
				document.documentElement.setAttribute('data-theme', theme);
			}
			set(theme);
		}
	};
}

export const theme = createThemeStore();
