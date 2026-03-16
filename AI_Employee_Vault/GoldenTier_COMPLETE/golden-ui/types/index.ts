// AI Employee Vault Types

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: Priority;
  domain: Domain;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
  amount?: number;
  assignee?: string;
  tags?: string[];
  plan?: Plan;
}

export type TaskStatus =
  | 'needs-action'
  | 'pending-approval'
  | 'approved'
  | 'in-progress'
  | 'done'
  | 'rejected'
  | 'failed';

export type Priority = 'low' | 'medium' | 'high' | 'urgent';

export type Domain =
  | 'finance'
  | 'social'
  | 'email'
  | 'calendar'
  | 'business'
  | 'system'
  | 'communication';

export interface Plan {
  id: string;
  taskId: string;
  objective: string;
  steps: PlanStep[];
  status: PlanStatus;
  createdAt: string;
  updatedAt: string;
}

export interface PlanStep {
  id: string;
  description: string;
  completed: boolean;
  order: number;
}

export type PlanStatus = 'pending' | 'in-progress' | 'completed' | 'failed';

export interface Approval {
  id: string;
  taskId: string;
  type: ApprovalType;
  amount?: number;
  description: string;
  requestedAt: string;
  requestedBy: string;
  status: ApprovalStatus;
  approvedAt?: string;
  approvedBy?: string;
  rejectedAt?: string;
  rejectedBy?: string;
  reason?: string;
}

export type ApprovalType =
  | 'payment'
  | 'social-post'
  | 'new-contact'
  | 'financial-change'
  | 'invoice'
  | 'email';

export type ApprovalStatus = 'pending' | 'approved' | 'rejected';

export interface AuditLog {
  id: string;
  timestamp: string;
  actionType: string;
  target: string;
  approvalStatus: 'auto' | 'required' | 'pending';
  result: string;
  userId?: string;
  details?: Record<string, unknown>;
}

export interface DashboardStats {
  totalTasks: number;
  pendingApprovals: number;
  completedTasks: number;
  needsAction: number;
  totalRevenue: number;
  monthlyRevenue: number;
  activeProjects: number;
  systemHealth: 'healthy' | 'warning' | 'error';
}

export interface SystemStatus {
  overall: 'running' | 'stopped' | 'error';
  watchers: {
    gmail: 'active' | 'inactive' | 'error';
    whatsapp: 'active' | 'inactive' | 'error';
    calendar: 'active' | 'inactive' | 'error';
  };
  mcpServers: {
    email: 'active' | 'inactive' | 'error';
    odoo: 'active' | 'inactive' | 'error';
    social: 'active' | 'inactive' | 'error';
    browser: 'active' | 'inactive' | 'error';
  };
  lastUpdated: string;
}

export interface FinancialSummary {
  totalRevenue: number;
  monthlyRevenue: number;
  outstandingInvoices: number;
  overduePayments: number;
  recentTransactions: Transaction[];
}

export interface Transaction {
  id: string;
  type: 'income' | 'expense';
  amount: number;
  description: string;
  date: string;
  category: string;
  status: 'completed' | 'pending' | 'failed';
}

export interface SocialMediaPost {
  id: string;
  platform: 'linkedin' | 'facebook' | 'instagram' | 'x';
  content: string;
  scheduledAt?: string;
  postedAt?: string;
  status: 'draft' | 'pending-approval' | 'approved' | 'posted' | 'failed';
  engagement?: {
    likes: number;
    comments: number;
    shares: number;
  };
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}