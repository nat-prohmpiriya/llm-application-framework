import { notificationsApi } from '$lib/api';
import type {
	Notification,
	NotificationPreference,
	NotificationPreferenceUpdate,
	NotificationListParams
} from '$lib/api';

const POLLING_INTERVAL = 60000; // 60 seconds

class NotificationStore {
	// State
	notifications = $state<Notification[]>([]);
	unreadCount = $state(0);
	loading = $state(false);
	loadingPreferences = $state(false);
	preferences = $state<NotificationPreference | null>(null);
	error = $state<string | null>(null);

	// Pagination state
	currentPage = $state(1);
	totalPages = $state(0);
	total = $state(0);
	perPage = $state(20);

	// Polling state
	private pollingInterval: ReturnType<typeof setInterval> | null = null;
	private isPolling = $state(false);

	// Derived
	hasUnread = $derived(this.unreadCount > 0);

	/**
	 * Fetch notifications with pagination
	 */
	async fetchNotifications(params: NotificationListParams = {}) {
		this.loading = true;
		this.error = null;

		try {
			const response = await notificationsApi.getNotifications({
				page: params.page ?? this.currentPage,
				per_page: params.per_page ?? this.perPage,
				unread_only: params.unread_only
			});

			this.notifications = response.items;
			this.currentPage = response.page;
			this.totalPages = response.pages;
			this.total = response.total;
			this.perPage = response.per_page;
		} catch (err) {
			this.error = err instanceof Error ? err.message : 'Failed to fetch notifications';
			console.error('Failed to fetch notifications:', err);
		} finally {
			this.loading = false;
		}
	}

	/**
	 * Fetch unread count for badge display
	 */
	async fetchUnreadCount() {
		try {
			const response = await notificationsApi.getUnreadCount();
			this.unreadCount = response.count;
		} catch (err) {
			console.error('Failed to fetch unread count:', err);
		}
	}

	/**
	 * Mark a single notification as read
	 */
	async markAsRead(notificationId: string) {
		try {
			await notificationsApi.markAsRead(notificationId);

			// Update local state
			const notification = this.notifications.find((n) => n.id === notificationId);
			if (notification && !notification.read_at) {
				notification.read_at = new Date().toISOString();
				this.unreadCount = Math.max(0, this.unreadCount - 1);
			}

			return true;
		} catch (err) {
			console.error('Failed to mark notification as read:', err);
			return false;
		}
	}

	/**
	 * Mark all notifications as read
	 */
	async markAllAsRead() {
		try {
			const response = await notificationsApi.markAllAsRead();

			// Update local state
			const now = new Date().toISOString();
			this.notifications = this.notifications.map((n) => ({
				...n,
				read_at: n.read_at ?? now
			}));
			this.unreadCount = 0;

			return response.count;
		} catch (err) {
			console.error('Failed to mark all notifications as read:', err);
			return 0;
		}
	}

	/**
	 * Delete a notification
	 */
	async deleteNotification(notificationId: string) {
		try {
			await notificationsApi.deleteNotification(notificationId);

			// Update local state
			const notification = this.notifications.find((n) => n.id === notificationId);
			if (notification && !notification.read_at) {
				this.unreadCount = Math.max(0, this.unreadCount - 1);
			}

			this.notifications = this.notifications.filter((n) => n.id !== notificationId);
			this.total = Math.max(0, this.total - 1);

			return true;
		} catch (err) {
			console.error('Failed to delete notification:', err);
			return false;
		}
	}

	/**
	 * Fetch notification preferences
	 */
	async fetchPreferences() {
		this.loadingPreferences = true;

		try {
			this.preferences = await notificationsApi.getPreferences();
		} catch (err) {
			console.error('Failed to fetch notification preferences:', err);
		} finally {
			this.loadingPreferences = false;
		}
	}

	/**
	 * Update notification preferences
	 */
	async updatePreferences(data: NotificationPreferenceUpdate) {
		this.loadingPreferences = true;

		try {
			this.preferences = await notificationsApi.updatePreferences(data);
			return true;
		} catch (err) {
			console.error('Failed to update notification preferences:', err);
			return false;
		} finally {
			this.loadingPreferences = false;
		}
	}

	/**
	 * Start polling for unread count
	 */
	startPolling() {
		if (this.isPolling || typeof window === 'undefined') return;

		this.isPolling = true;

		// Fetch immediately
		this.fetchUnreadCount();

		// Set up interval
		this.pollingInterval = setInterval(() => {
			this.fetchUnreadCount();
		}, POLLING_INTERVAL);
	}

	/**
	 * Stop polling for unread count
	 */
	stopPolling() {
		if (this.pollingInterval) {
			clearInterval(this.pollingInterval);
			this.pollingInterval = null;
		}
		this.isPolling = false;
	}

	/**
	 * Reset store state (call on logout)
	 */
	reset() {
		this.stopPolling();
		this.notifications = [];
		this.unreadCount = 0;
		this.loading = false;
		this.loadingPreferences = false;
		this.preferences = null;
		this.error = null;
		this.currentPage = 1;
		this.totalPages = 0;
		this.total = 0;
	}

	/**
	 * Load next page of notifications
	 */
	async loadNextPage() {
		if (this.currentPage >= this.totalPages) return;

		await this.fetchNotifications({ page: this.currentPage + 1 });
	}

	/**
	 * Load previous page of notifications
	 */
	async loadPreviousPage() {
		if (this.currentPage <= 1) return;

		await this.fetchNotifications({ page: this.currentPage - 1 });
	}

	/**
	 * Refresh notifications (reload current page)
	 */
	async refresh() {
		await Promise.all([this.fetchNotifications(), this.fetchUnreadCount()]);
	}
}

export const notificationStore = new NotificationStore();
