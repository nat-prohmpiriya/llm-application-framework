import { projectsApi, type Project, type ProjectCreate, type ProjectUpdate } from '$lib/api';

const STORAGE_KEY = 'currentProjectId';

// Project state using Svelte 5 runes
let projects = $state<Project[]>([]);
let currentProjectId = $state<string | null>(null);
let loading = $state(false);
let error = $state<string | null>(null);

// Derived state
let currentProject = $derived(
	currentProjectId ? projects.find((p) => p.id === currentProjectId) ?? null : null
);

// Initialize from localStorage
function initialize(): void {
	if (typeof window === 'undefined') return;

	const storedId = localStorage.getItem(STORAGE_KEY);
	if (storedId) {
		currentProjectId = storedId;
	}
}

// Load all projects
async function loadProjects(): Promise<void> {
	loading = true;
	error = null;

	try {
		const response = await projectsApi.list(1, 100);
		projects = response.items;

		// Validate currentProjectId still exists
		if (currentProjectId && !projects.find((p) => p.id === currentProjectId)) {
			currentProjectId = null;
			localStorage.removeItem(STORAGE_KEY);
		}
	} catch (e) {
		error = e instanceof Error ? e.message : 'Failed to load projects';
		projects = [];
	} finally {
		loading = false;
	}
}

// Select a project (or null to clear)
function selectProject(id: string | null): void {
	currentProjectId = id;

	if (typeof window !== 'undefined') {
		if (id) {
			localStorage.setItem(STORAGE_KEY, id);
		} else {
			localStorage.removeItem(STORAGE_KEY);
		}
	}
}

// Create a new project
async function createProject(data: ProjectCreate): Promise<Project> {
	loading = true;
	error = null;

	try {
		const project = await projectsApi.create(data);
		projects = [...projects, project];
		return project;
	} catch (e) {
		error = e instanceof Error ? e.message : 'Failed to create project';
		throw e;
	} finally {
		loading = false;
	}
}

// Update a project
async function updateProject(id: string, data: ProjectUpdate): Promise<Project> {
	loading = true;
	error = null;

	try {
		const updated = await projectsApi.update(id, data);
		projects = projects.map((p) => (p.id === id ? updated : p));
		return updated;
	} catch (e) {
		error = e instanceof Error ? e.message : 'Failed to update project';
		throw e;
	} finally {
		loading = false;
	}
}

// Delete a project
async function deleteProject(id: string): Promise<void> {
	loading = true;
	error = null;

	try {
		await projectsApi.delete(id);
		projects = projects.filter((p) => p.id !== id);

		// Clear selection if deleted project was selected
		if (currentProjectId === id) {
			selectProject(null);
		}
	} catch (e) {
		error = e instanceof Error ? e.message : 'Failed to delete project';
		throw e;
	} finally {
		loading = false;
	}
}

// Clear all state (e.g., on logout)
function clear(): void {
	projects = [];
	currentProjectId = null;
	error = null;

	if (typeof window !== 'undefined') {
		localStorage.removeItem(STORAGE_KEY);
	}
}

// Export projects store
export function useProjects() {
	return {
		get projects() {
			return projects;
		},
		get currentProject() {
			return currentProject;
		},
		get currentProjectId() {
			return currentProjectId;
		},
		get loading() {
			return loading;
		},
		get error() {
			return error;
		},
		initialize,
		loadProjects,
		selectProject,
		createProject,
		updateProject,
		deleteProject,
		clear,
	};
}

// Create singleton instance
export const projectStore = useProjects();
