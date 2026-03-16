import axios, { AxiosInstance, AxiosResponse } from 'axios';
import {
  Task,
  Approval,
  AuditLog,
  DashboardStats,
  SystemStatus,
  FinancialSummary,
  SocialMediaPost,
  ApiResponse,
  PaginatedResponse,
} from '@/types';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.BACKEND_URL || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add any auth tokens here if needed
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  // Dashboard APIs
  async getDashboardStats(): Promise<ApiResponse<DashboardStats>> {
    const response: AxiosResponse<ApiResponse<DashboardStats>> =
      await this.client.get('/api/dashboard/stats');
    return response.data;
  }

  async getSystemStatus(): Promise<ApiResponse<SystemStatus>> {
    const response: AxiosResponse<ApiResponse<SystemStatus>> =
      await this.client.get('/api/system/status');
    return response.data;
  }

  // Task APIs
  async getTasks(page = 1, limit = 10): Promise<PaginatedResponse<Task>> {
    const response: AxiosResponse<PaginatedResponse<Task>> =
      await this.client.get(`/api/tasks?page=${page}&limit=${limit}`);
    return response.data;
  }

  async getTask(id: string): Promise<ApiResponse<Task>> {
    const response: AxiosResponse<ApiResponse<Task>> =
      await this.client.get(`/api/tasks/${id}`);
    return response.data;
  }

  async createTask(task: Partial<Task>): Promise<ApiResponse<Task>> {
    const response: AxiosResponse<ApiResponse<Task>> =
      await this.client.post('/api/tasks', task);
    return response.data;
  }

  async updateTask(id: string, updates: Partial<Task>): Promise<ApiResponse<Task>> {
    const response: AxiosResponse<ApiResponse<Task>> =
      await this.client.put(`/api/tasks/${id}`, updates);
    return response.data;
  }

  async deleteTask(id: string): Promise<ApiResponse<void>> {
    const response: AxiosResponse<ApiResponse<void>> =
      await this.client.delete(`/api/tasks/${id}`);
    return response.data;
  }

  // Approval APIs
  async getApprovals(page = 1, limit = 10): Promise<PaginatedResponse<Approval>> {
    const response: AxiosResponse<PaginatedResponse<Approval>> =
      await this.client.get(`/api/approvals?page=${page}&limit=${limit}`);
    return response.data;
  }

  async approveRequest(id: string, reason?: string): Promise<ApiResponse<Approval>> {
    const response: AxiosResponse<ApiResponse<Approval>> =
      await this.client.post(`/api/approvals/${id}/approve`, { reason });
    return response.data;
  }

  async rejectRequest(id: string, reason: string): Promise<ApiResponse<Approval>> {
    const response: AxiosResponse<ApiResponse<Approval>> =
      await this.client.post(`/api/approvals/${id}/reject`, { reason });
    return response.data;
  }

  // Financial APIs
  async getFinancialSummary(): Promise<ApiResponse<FinancialSummary>> {
    const response: AxiosResponse<ApiResponse<FinancialSummary>> =
      await this.client.get('/api/finance/summary');
    return response.data;
  }

  // Audit Log APIs
  async getAuditLogs(page = 1, limit = 20): Promise<PaginatedResponse<AuditLog>> {
    const response: AxiosResponse<PaginatedResponse<AuditLog>> =
      await this.client.get(`/api/logs?page=${page}&limit=${limit}`);
    return response.data;
  }

  // Social Media APIs
  async getSocialPosts(page = 1, limit = 10): Promise<PaginatedResponse<SocialMediaPost>> {
    const response: AxiosResponse<PaginatedResponse<SocialMediaPost>> =
      await this.client.get(`/api/social/posts?page=${page}&limit=${limit}`);
    return response.data;
  }

  async scheduleSocialPost(post: Partial<SocialMediaPost>): Promise<ApiResponse<SocialMediaPost>> {
    const response: AxiosResponse<ApiResponse<SocialMediaPost>> =
      await this.client.post('/api/social/posts', post);
    return response.data;
  }

  // System Control APIs
  async startSystem(): Promise<ApiResponse<void>> {
    const response: AxiosResponse<ApiResponse<void>> =
      await this.client.post('/api/system/start');
    return response.data;
  }

  async stopSystem(): Promise<ApiResponse<void>> {
    const response: AxiosResponse<ApiResponse<void>> =
      await this.client.post('/api/system/stop');
    return response.data;
  }

  async restartSystem(): Promise<ApiResponse<void>> {
    const response: AxiosResponse<ApiResponse<void>> =
      await this.client.post('/api/system/restart');
    return response.data;
  }
}

export const api = new ApiClient();
export default api;