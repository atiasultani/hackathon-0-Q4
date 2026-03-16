'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/store';

interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
}

interface ToastContextType {
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}

interface ToastProviderProps {
  children: React.ReactNode;
}

export function ToastProvider({ children }: ToastProviderProps) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substring(2);
    const newToast = { ...toast, id };

    setToasts(prev => [...prev, newToast]);

    // Auto remove toast
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, toast.duration || 5000);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} removeToast={removeToast} />
    </ToastContext.Provider>
  );
}

interface ToastContainerProps {
  toasts: Toast[];
  removeToast: (id: string) => void;
}

function ToastContainer({ toasts, removeToast }: ToastContainerProps) {
  if (typeof window === 'undefined') return null;

  return createPortal(
    <div className="fixed top-4 right-4 z-50 space-y-2">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onRemove={removeToast} />
      ))}
    </div>,
    document.body
  );
}

interface ToastItemProps {
  toast: Toast;
  onRemove: (id: string) => void;
}

function ToastItem({ toast, onRemove }: ToastItemProps) {
  const typeStyles = {
    success: 'bg-success-50 border-success-200 text-success-800 dark:bg-success-900/20 dark:border-success-800 dark:text-success-200',
    error: 'bg-danger-50 border-danger-200 text-danger-800 dark:bg-danger-900/20 dark:border-danger-800 dark:text-danger-200',
    warning: 'bg-warning-50 border-warning-200 text-warning-800 dark:bg-warning-900/20 dark:border-warning-800 dark:text-warning-200',
    info: 'bg-primary-50 border-primary-200 text-primary-800 dark:bg-primary-900/20 dark:border-primary-800 dark:text-primary-200',
  };

  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️',
  };

  return (
    <div
      className={cn(
        'flex items-start p-4 border rounded-lg shadow-lg max-w-sm animate-slide-up',
        typeStyles[toast.type]
      )}
    >
      <span className="text-lg mr-3">{icons[toast.type]}</span>
      <div className="flex-1">
        <h4 className="font-medium">{toast.title}</h4>
        <p className="text-sm opacity-90">{toast.message}</p>
      </div>
      <button
        onClick={() => onRemove(toast.id)}
        className="ml-3 opacity-70 hover:opacity-100 transition-opacity"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}