'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useAppStore } from '@/store';
import { getStatusColor, getStatusIcon, formatCurrency, formatDate } from '@/lib/utils';

// Mock data for demonstration
const mockStats = {
  totalTasks: 24,
  pendingApprovals: 5,
  completedTasks: 18,
  needsAction: 3,
  totalRevenue: 45750,
  monthlyRevenue: 12500,
  activeProjects: 8,
  systemHealth: 'healthy' as const,
};

const mockTasks = [
  {
    id: '1',
    title: 'Process quarterly invoice for Client A',
    description: 'Generate and send Q4 invoice for consulting services',
    status: 'pending-approval' as const,
    priority: 'high' as const,
    domain: 'finance' as const,
    createdAt: '2026-03-12T10:30:00Z',
    updatedAt: '2026-03-12T10:30:00Z',
    amount: 5500,
  },
  {
    id: '2',
    title: 'Schedule LinkedIn post about product launch',
    description: 'Create and schedule social media content for new feature announcement',
    status: 'needs-action' as const,
    priority: 'medium' as const,
    domain: 'social' as const,
    createdAt: '2026-03-12T09:15:00Z',
    updatedAt: '2026-03-12T09:15:00Z',
  },
  {
    id: '3',
    title: 'Respond to vendor inquiry about contract renewal',
    description: 'Review terms and prepare response for SoftwareCorp renewal',
    status: 'done' as const,
    priority: 'low' as const,
    domain: 'email' as const,
    createdAt: '2026-03-11T16:45:00Z',
    updatedAt: '2026-03-12T08:20:00Z',
  },
  {
    id: '4',
    title: 'Process expense report for team lunch',
    description: 'Approve and record team building lunch expense',
    status: 'approved' as const,
    priority: 'low' as const,
    domain: 'finance' as const,
    createdAt: '2026-03-11T14:20:00Z',
    updatedAt: '2026-03-12T07:45:00Z',
    amount: 285,
  },
];

const mockSystemStatus = {
  overall: 'running' as const,
  watchers: {
    gmail: 'active' as const,
    whatsapp: 'active' as const,
    calendar: 'active' as const,
  },
  mcpServers: {
    email: 'active' as const,
    odoo: 'active' as const,
    social: 'active' as const,
    browser: 'active' as const,
  },
  lastUpdated: '2026-03-12T16:30:00Z',
};

export default function Dashboard() {
  const { setDashboardStats, addNotification } = useAppStore();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading dashboard data
    const loadDashboard = async () => {
      setIsLoading(true);
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      setDashboardStats(mockStats);
      setIsLoading(false);
    };

    loadDashboard();
  }, [setDashboardStats]);

  const handleCreateTask = () => {
    addNotification({
      type: 'info',
      title: 'Create Task',
      message: 'Task creation modal would open here',
    });
  };

  const handleQuickAction = (action: string) => {
    addNotification({
      type: 'info',
      title: 'Quick Action',
      message: `${action} feature coming soon`,
    });
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Welcome back! Here's what's happening with your AI Employee.
          </p>
        </div>
        <Button onClick={handleCreateTask} className="animate-pulse-gold">
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Create Task
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card hover className="card-hover">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-primary-100 dark:bg-primary-900/30">
                <span className="text-primary-600 dark:text-primary-300 text-xl">📋</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Tasks</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{mockStats.totalTasks}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card hover className="card-hover">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-warning-100 dark:bg-warning-900/30">
                <span className="text-warning-600 dark:text-warning-300 text-xl">⏳</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Pending Approval</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{mockStats.pendingApprovals}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card hover className="card-hover">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-success-100 dark:bg-success-900/30">
                <span className="text-success-600 dark:text-success-300 text-xl">✅</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Completed</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{mockStats.completedTasks}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card hover className="card-hover">
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-secondary-100 dark:bg-secondary-900/30">
                <span className="text-secondary-600 dark:text-secondary-300 text-xl">🔔</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Needs Action</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{mockStats.needsAction}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Revenue Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card hover className="card-hover">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Revenue</p>
                <p className="text-3xl font-bold text-gradient-gold">{formatCurrency(mockStats.totalRevenue)}</p>
              </div>
              <div className="p-3 rounded-full bg-primary-100 dark:bg-primary-900/30">
                <span className="text-primary-600 dark:text-primary-300 text-2xl">💰</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card hover className="card-hover">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">This Month</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatCurrency(mockStats.monthlyRevenue)}</p>
              </div>
              <div className="p-3 rounded-full bg-success-100 dark:bg-success-900/30">
                <span className="text-success-600 dark:text-success-300 text-2xl">📈</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Tasks */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle>Recent Tasks</CardTitle>
            <Button variant="outline" size="sm">
              View All
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockTasks.map((task) => (
                <div
                  key={task.id}
                  className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
                >
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 dark:text-white">{task.title}</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{task.description}</p>
                    {task.amount && (
                      <p className="text-sm font-medium text-success-600 dark:text-success-400 mt-1">
                        {formatCurrency(task.amount)}
                      </p>
                    )}
                  </div>
                  <div className="ml-4 flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                      {getStatusIcon(task.status)} {task.status.replace('-', ' ')}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* System Status & Quick Actions */}
        <div className="space-y-6">
          {/* System Status */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <div className="w-2 h-2 bg-success-500 rounded-full mr-2 animate-status-online"></div>
                System Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Watchers</h4>
                  <div className="space-y-2">
                    {Object.entries(mockSystemStatus.watchers).map(([service, status]) => (
                      <div key={service} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">{service}</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
                          {status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">MCP Servers</h4>
                  <div className="space-y-2">
                    {Object.entries(mockSystemStatus.mcpServers).map(([service, status]) => (
                      <div key={service} className="flex items-center justify-between">
                        <span className="text-sm text-gray-600 dark:text-gray-400 capitalize">{service}</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(status)}`}>
                          {status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                <Button
                  variant="outline"
                  onClick={() => handleQuickAction('Process Pending Approvals')}
                  className="h-auto p-4 flex flex-col items-center space-y-2"
                >
                  <span className="text-lg">✅</span>
                  <span className="text-sm">Process Approvals</span>
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleQuickAction('Generate Report')}
                  className="h-auto p-4 flex flex-col items-center space-y-2"
                >
                  <span className="text-lg">📊</span>
                  <span className="text-sm">Generate Report</span>
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleQuickAction('View Financial Summary')}
                  className="h-auto p-4 flex flex-col items-center space-y-2"
                >
                  <span className="text-lg">💰</span>
                  <span className="text-sm">Financial Summary</span>
                </Button>
                <Button
                  variant="outline"
                  onClick={() => handleQuickAction('View Audit Trail')}
                  className="h-auto p-4 flex flex-col items-center space-y-2"
                >
                  <span className="text-lg">📋</span>
                  <span className="text-sm">Audit Trail</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}