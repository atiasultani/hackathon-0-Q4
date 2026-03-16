'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useAppStore } from '@/store';
import { getStatusColor, getStatusIcon, formatCurrency, formatDate, cn } from '@/lib/utils';
import { Task, TaskStatus, Priority, Domain } from '@/types';

// Mock data
const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Process quarterly invoice for Client A',
    description: 'Generate and send Q4 invoice for consulting services including detailed breakdown of hours and expenses.',
    status: 'pending-approval',
    priority: 'high',
    domain: 'finance',
    createdAt: '2026-03-12T10:30:00Z',
    updatedAt: '2026-03-12T10:30:00Z',
    amount: 5500,
    tags: ['invoice', 'quarterly', 'client-a'],
  },
  {
    id: '2',
    title: 'Schedule LinkedIn post about product launch',
    description: 'Create and schedule social media content for new feature announcement across all platforms.',
    status: 'needs-action',
    priority: 'medium',
    domain: 'social',
    createdAt: '2026-03-12T09:15:00Z',
    updatedAt: '2026-03-12T09:15:00Z',
    tags: ['social', 'product-launch'],
  },
  {
    id: '3',
    title: 'Respond to vendor inquiry about contract renewal',
    description: 'Review terms and prepare response for SoftwareCorp renewal including negotiation points.',
    status: 'done',
    priority: 'low',
    domain: 'email',
    createdAt: '2026-03-11T16:45:00Z',
    updatedAt: '2026-03-12T08:20:00Z',
    completedAt: '2026-03-12T08:20:00Z',
    tags: ['vendor', 'contract', 'renewal'],
  },
  {
    id: '4',
    title: 'Process expense report for team lunch',
    description: 'Approve and record team building lunch expense with receipt verification.',
    status: 'approved',
    priority: 'low',
    domain: 'finance',
    createdAt: '2026-03-11T14:20:00Z',
    updatedAt: '2026-03-12T07:45:00Z',
    amount: 285,
    tags: ['expense', 'team', 'lunch'],
  },
  {
    id: '5',
    title: 'Schedule quarterly business review meeting',
    description: 'Coordinate with stakeholders for Q1 business review and send calendar invites.',
    status: 'in-progress',
    priority: 'medium',
    domain: 'calendar',
    createdAt: '2026-03-12T08:00:00Z',
    updatedAt: '2026-03-12T15:30:00Z',
    tags: ['meeting', 'quarterly', 'business-review'],
  },
];

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>(mockTasks);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>(mockTasks);
  const [selectedStatus, setSelectedStatus] = useState<TaskStatus | 'all'>('all');
  const [selectedPriority, setSelectedPriority] = useState<Priority | 'all'>('all');
  const [selectedDomain, setSelectedDomain] = useState<Domain | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading
    setTimeout(() => setIsLoading(false), 800);
  }, []);

  useEffect(() => {
    let filtered = tasks;

    if (selectedStatus !== 'all') {
      filtered = filtered.filter(task => task.status === selectedStatus);
    }

    if (selectedPriority !== 'all') {
      filtered = filtered.filter(task => task.priority === selectedPriority);
    }

    if (selectedDomain !== 'all') {
      filtered = filtered.filter(task => task.domain === selectedDomain);
    }

    if (searchTerm) {
      filtered = filtered.filter(task =>
        task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        task.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredTasks(filtered);
  }, [tasks, selectedStatus, selectedPriority, selectedDomain, searchTerm]);

  const getPriorityColor = (priority: Priority) => {
    const colors = {
      low: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
      medium: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      high: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
      urgent: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    };
    return colors[priority];
  };

  const getDomainIcon = (domain: Domain) => {
    const icons = {
      finance: '💰',
      social: '📱',
      email: '📧',
      calendar: '📅',
      business: '💼',
      system: '⚙️',
      communication: '💬',
    };
    return icons[domain] || '📋';
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
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
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Tasks</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Manage and track all AI Employee tasks
          </p>
        </div>
        <Button>
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Create Task
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            {/* Search */}
            <div className="flex-1 min-w-64">
              <input
                type="text"
                placeholder="Search tasks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
              />
            </div>

            {/* Status Filter */}
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value as TaskStatus | 'all')}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="all">All Statuses</option>
              <option value="needs-action">Needs Action</option>
              <option value="pending-approval">Pending Approval</option>
              <option value="approved">Approved</option>
              <option value="in-progress">In Progress</option>
              <option value="done">Done</option>
              <option value="rejected">Rejected</option>
            </select>

            {/* Priority Filter */}
            <select
              value={selectedPriority}
              onChange={(e) => setSelectedPriority(e.target.value as Priority | 'all')}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="all">All Priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>

            {/* Domain Filter */}
            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value as Domain | 'all')}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="all">All Domains</option>
              <option value="finance">Finance</option>
              <option value="social">Social</option>
              <option value="email">Email</option>
              <option value="calendar">Calendar</option>
              <option value="business">Business</option>
              <option value="system">System</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Tasks List */}
      <div className="space-y-4">
        {filteredTasks.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <div className="text-gray-500 dark:text-gray-400">
                <svg className="w-12 h-12 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <p className="text-lg font-medium">No tasks found</p>
                <p className="text-sm">Try adjusting your filters or create a new task.</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          filteredTasks.map((task) => (
            <Card key={task.id} hover className="card-hover">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-lg">{getDomainIcon(task.domain)}</span>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{task.title}</h3>
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 mb-3">{task.description}</p>
                    <div className="flex items-center space-x-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                        {getStatusIcon(task.status)} {task.status.replace('-', ' ')}
                      </span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(task.priority)}`}>
                        {task.priority}
                      </span>
                      {task.amount && (
                        <span className="text-sm font-medium text-success-600 dark:text-success-400">
                          {formatCurrency(task.amount)}
                        </span>
                      )}
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {formatDate(task.createdAt)}
                      </span>
                    </div>
                    {task.tags && (
                      <div className="flex items-center space-x-1 mt-3">
                        {task.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded"
                          >
                            #{tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    <Button variant="outline" size="sm">View</Button>
                    <Button variant="ghost" size="sm">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                      </svg>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}