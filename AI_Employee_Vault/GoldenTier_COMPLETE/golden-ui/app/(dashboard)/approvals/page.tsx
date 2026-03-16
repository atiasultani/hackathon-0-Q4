'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useAppStore } from '@/store';
import { formatCurrency, formatDate, cn } from '@/lib/utils';
import { Approval, ApprovalType, ApprovalStatus } from '@/types';

// Mock data
const mockApprovals: Approval[] = [
  {
    id: '1',
    taskId: 'task-1',
    type: 'payment',
    amount: 5500,
    description: 'Quarterly invoice payment for Client A consulting services',
    requestedAt: '2026-03-12T10:30:00Z',
    requestedBy: 'AI Employee',
    status: 'pending',
  },
  {
    id: '2',
    taskId: 'task-2',
    type: 'social-post',
    description: 'LinkedIn post about new product feature announcement',
    requestedAt: '2026-03-12T09:15:00Z',
    requestedBy: 'AI Employee',
    status: 'pending',
  },
  {
    id: '3',
    taskId: 'task-3',
    type: 'new-contact',
    description: 'Add new vendor contact: TechSolutions Inc.',
    requestedAt: '2026-03-11T16:45:00Z',
    requestedBy: 'AI Employee',
    status: 'approved',
    approvedAt: '2026-03-12T08:20:00Z',
    approvedBy: 'Admin User',
  },
  {
    id: '4',
    taskId: 'task-4',
    type: 'payment',
    amount: 285,
    description: 'Team lunch expense reimbursement',
    requestedAt: '2026-03-11T14:20:00Z',
    requestedBy: 'AI Employee',
    status: 'approved',
    approvedAt: '2026-03-12T07:45:00Z',
    approvedBy: 'Admin User',
  },
  {
    id: '5',
    taskId: 'task-5',
    type: 'email',
    description: 'Send contract renewal proposal to SoftwareCorp',
    requestedAt: '2026-03-10T11:30:00Z',
    requestedBy: 'AI Employee',
    status: 'rejected',
    rejectedAt: '2026-03-11T09:15:00Z',
    rejectedBy: 'Admin User',
    reason: 'Contract terms need revision before sending',
  },
];

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<Approval[]>(mockApprovals);
  const [filteredApprovals, setFilteredApprovals] = useState<Approval[]>(mockApprovals);
  const [selectedStatus, setSelectedStatus] = useState<ApprovalStatus | 'all'>('all');
  const [selectedType, setSelectedType] = useState<ApprovalType | 'all'>('all');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setTimeout(() => setIsLoading(false), 800);
  }, []);

  useEffect(() => {
    let filtered = approvals;

    if (selectedStatus !== 'all') {
      filtered = filtered.filter(approval => approval.status === selectedStatus);
    }

    if (selectedType !== 'all') {
      filtered = filtered.filter(approval => approval.type === selectedType);
    }

    setFilteredApprovals(filtered);
  }, [approvals, selectedStatus, selectedType]);

  const handleApprove = (id: string) => {
    setApprovals(prev => prev.map(approval =>
      approval.id === id
        ? {
            ...approval,
            status: 'approved' as const,
            approvedAt: new Date().toISOString(),
            approvedBy: 'Current User',
          }
        : approval
    ));
  };

  const handleReject = (id: string, reason: string) => {
    setApprovals(prev => prev.map(approval =>
      approval.id === id
        ? {
            ...approval,
            status: 'rejected' as const,
            rejectedAt: new Date().toISOString(),
            rejectedBy: 'Current User',
            reason,
          }
        : approval
    ));
  };

  const getStatusColor = (status: ApprovalStatus) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
      approved: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      rejected: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    };
    return colors[status];
  };

  const getTypeIcon = (type: ApprovalType) => {
    const icons = {
      payment: '💰',
      'social-post': '📱',
      'new-contact': '👤',
      'financial-change': '📊',
      invoice: '📄',
      email: '📧',
    };
    return icons[type] || '❓';
  };

  const getTypeLabel = (type: ApprovalType) => {
    const labels = {
      payment: 'Payment',
      'social-post': 'Social Post',
      'new-contact': 'New Contact',
      'financial-change': 'Financial Change',
      invoice: 'Invoice',
      email: 'Email',
    };
    return labels[type] || type;
  };

  const pendingCount = approvals.filter(a => a.status === 'pending').length;

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
          <div className="space-y-4">
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
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Approvals</h1>
          <p className="text-gray-600 dark:text-gray-400">
            Review and approve AI Employee actions
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="px-3 py-1 bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300 rounded-full text-sm font-medium">
            {pendingCount} pending
          </span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-yellow-100 dark:bg-yellow-900/30">
                <span className="text-yellow-600 dark:text-yellow-300 text-xl">⏳</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Pending</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {approvals.filter(a => a.status === 'pending').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-green-100 dark:bg-green-900/30">
                <span className="text-green-600 dark:text-green-300 text-xl">✅</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Approved</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {approvals.filter(a => a.status === 'approved').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-red-100 dark:bg-red-900/30">
                <span className="text-red-600 dark:text-red-300 text-xl">❌</span>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Rejected</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {approvals.filter(a => a.status === 'rejected').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value as ApprovalStatus | 'all')}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="all">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>

            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value as ApprovalType | 'all')}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="all">All Types</option>
              <option value="payment">Payment</option>
              <option value="social-post">Social Post</option>
              <option value="new-contact">New Contact</option>
              <option value="email">Email</option>
              <option value="invoice">Invoice</option>
              <option value="financial-change">Financial Change</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Approvals List */}
      <div className="space-y-4">
        {filteredApprovals.length === 0 ? (
          <Card>
            <CardContent className="p-8 text-center">
              <div className="text-gray-500 dark:text-gray-400">
                <svg className="w-12 h-12 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-lg font-medium">No approvals found</p>
                <p className="text-sm">All caught up! No items need your attention.</p>
              </div>
            </CardContent>
          </Card>
        ) : (
          filteredApprovals.map((approval) => (
            <Card key={approval.id} hover className="card-hover">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-lg">{getTypeIcon(approval.type)}</span>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {getTypeLabel(approval.type)}
                      </h3>
                      {approval.amount && (
                        <span className="text-lg font-bold text-success-600 dark:text-success-400">
                          {formatCurrency(approval.amount)}
                        </span>
                      )}
                    </div>
                    <p className="text-gray-600 dark:text-gray-400 mb-3">{approval.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500 dark:text-gray-400">
                      <span>Requested by: {approval.requestedBy}</span>
                      <span>•</span>
                      <span>{formatDate(approval.requestedAt)}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(approval.status)}`}>
                        {approval.status}
                      </span>
                    </div>
                    {approval.status === 'rejected' && approval.reason && (
                      <div className="mt-3 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                        <p className="text-sm text-red-700 dark:text-red-300">
                          <strong>Rejection reason:</strong> {approval.reason}
                        </p>
                      </div>
                    )}
                    {approval.status === 'approved' && approval.approvedBy && (
                      <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                        <p className="text-sm text-green-700 dark:text-green-300">
                          <strong>Approved by:</strong> {approval.approvedBy} on {approval.approvedAt && formatDate(approval.approvedAt)}
                        </p>
                      </div>
                    )}
                  </div>
                  {approval.status === 'pending' && (
                    <div className="flex items-center space-x-2 ml-4">
                      <Button
                        variant="success"
                        size="sm"
                        onClick={() => handleApprove(approval.id)}
                      >
                        Approve
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleReject(approval.id, 'Manual rejection')}
                      >
                        Reject
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}