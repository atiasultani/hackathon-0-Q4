import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: Date | string): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    'needs-action': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    'pending-approval': 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
    'approved': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    'done': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    'rejected': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    'in-progress': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
    'completed': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    'failed': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    'active': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    'inactive': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
  };
  return colors[status] || colors['inactive'];
}

export function getStatusIcon(status: string): string {
  const icons: Record<string, string> = {
    'needs-action': '⚡',
    'pending-approval': '⏳',
    'approved': '✅',
    'done': '🎉',
    'rejected': '❌',
    'in-progress': '🔄',
    'completed': '✅',
    'failed': '💥',
    'active': '🟢',
    'inactive': '⚪',
  };
  return icons[status] || '❓';
}

export function generateId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength) + '...';
}