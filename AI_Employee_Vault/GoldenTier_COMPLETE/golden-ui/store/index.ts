import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import {
  Task,
  Approval,
  DashboardStats,
  SystemStatus,
  FinancialSummary,
  AuditLog,
} from '@/types';

interface AppState {
  // UI State
  sidebarCollapsed: boolean;
  theme: 'light' | 'dark' | 'system';
  notifications: Notification[];

  // Data State
  tasks: Task[];
  approvals: Approval[];
  dashboardStats: DashboardStats | null;
  systemStatus: SystemStatus | null;
  financialSummary: FinancialSummary | null;
  auditLogs: AuditLog[];

  // Loading States
  loading: {
    tasks: boolean;
    approvals: boolean;
    dashboard: boolean;
    system: boolean;
    financial: boolean;
    logs: boolean;
  };

  // Error States
  errors: {
    tasks: string | null;
    approvals: string | null;
    dashboard: string | null;
    system: string | null;
    financial: string | null;
    logs: string | null;
  };
}

interface AppActions {
  // UI Actions
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;

  // Data Actions
  setTasks: (tasks: Task[]) => void;
  addTask: (task: Task) => void;
  updateTask: (id: string, updates: Partial<Task>) => void;
  removeTask: (id: string) => void;

  setApprovals: (approvals: Approval[]) => void;
  updateApproval: (id: string, updates: Partial<Approval>) => void;

  setDashboardStats: (stats: DashboardStats) => void;
  setSystemStatus: (status: SystemStatus) => void;
  setFinancialSummary: (summary: FinancialSummary) => void;
  setAuditLogs: (logs: AuditLog[]) => void;

  // Loading Actions
  setLoading: (key: keyof AppState['loading'], loading: boolean) => void;

  // Error Actions
  setError: (key: keyof AppState['errors'], error: string | null) => void;
  clearErrors: () => void;
}

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const initialState: AppState = {
  sidebarCollapsed: false,
  theme: 'system',
  notifications: [],
  tasks: [],
  approvals: [],
  dashboardStats: null,
  systemStatus: null,
  financialSummary: null,
  auditLogs: [],
  loading: {
    tasks: false,
    approvals: false,
    dashboard: false,
    system: false,
    financial: false,
    logs: false,
  },
  errors: {
    tasks: null,
    approvals: null,
    dashboard: null,
    system: null,
    financial: null,
    logs: null,
  },
};

export const useAppStore = create<AppState & AppActions>()(
  devtools(
    persist(
      (set, get) => ({
        ...initialState,

        // UI Actions
        toggleSidebar: () => {
          set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
        },

        setSidebarCollapsed: (collapsed) => {
          set({ sidebarCollapsed: collapsed });
        },

        setTheme: (theme) => {
          set({ theme });
        },

        addNotification: (notification) => {
          const id = Math.random().toString(36).substring(2);
          set((state) => ({
            notifications: [...state.notifications, { ...notification, id }],
          }));

          // Auto-remove notification after duration
          if (notification.duration !== 0) {
            setTimeout(() => {
              get().removeNotification(id);
            }, notification.duration || 5000);
          }
        },

        removeNotification: (id) => {
          set((state) => ({
            notifications: state.notifications.filter((n) => n.id !== id),
          }));
        },

        clearNotifications: () => {
          set({ notifications: [] });
        },

        // Data Actions
        setTasks: (tasks) => {
          set({ tasks });
        },

        addTask: (task) => {
          set((state) => ({ tasks: [task, ...state.tasks] }));
        },

        updateTask: (id, updates) => {
          set((state) => ({
            tasks: state.tasks.map((task) =>
              task.id === id ? { ...task, ...updates } : task
            ),
          }));
        },

        removeTask: (id) => {
          set((state) => ({
            tasks: state.tasks.filter((task) => task.id !== id),
          }));
        },

        setApprovals: (approvals) => {
          set({ approvals });
        },

        updateApproval: (id, updates) => {
          set((state) => ({
            approvals: state.approvals.map((approval) =>
              approval.id === id ? { ...approval, ...updates } : approval
            ),
          }));
        },

        setDashboardStats: (dashboardStats) => {
          set({ dashboardStats });
        },

        setSystemStatus: (systemStatus) => {
          set({ systemStatus });
        },

        setFinancialSummary: (financialSummary) => {
          set({ financialSummary });
        },

        setAuditLogs: (auditLogs) => {
          set({ auditLogs });
        },

        // Loading Actions
        setLoading: (key, loading) => {
          set((state) => ({
            loading: { ...state.loading, [key]: loading },
          }));
        },

        // Error Actions
        setError: (key, error) => {
          set((state) => ({
            errors: { ...state.errors, [key]: error },
          }));
        },

        clearErrors: () => {
          set({ errors: initialState.errors });
        },
      }),
      {
        name: 'ai-employee-store',
        partialize: (state) => ({
          sidebarCollapsed: state.sidebarCollapsed,
          theme: state.theme,
        }),
      }
    ),
    { name: 'AI Employee Store' }
  )
);