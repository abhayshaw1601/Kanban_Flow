import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export interface MemberStatistics {
  user_id: number;
  user_name: string;
  user_email: string;
  statistics: {
    total_tasks: number;
    todo_tasks: number;
    in_progress_tasks: number;
    done_tasks: number;
    completion_percentage: number;
  };
  performance: {
    status: 'excellent' | 'good' | 'needs_improvement';
    color: 'green' | 'yellow' | 'red';
    description: string;
  };
  board_breakdown: Array<{
    board_id: number;
    board_name: string;
    total_tasks: number;
    completed_tasks: number;
    completion_percentage: number;
  }>;
}

export interface TeamOverview {
  team_members: Array<{
    user_id: number;
    name: string;
    email: string;
    role: string;
    total_tasks: number;
    completed_tasks: number;
    completion_percentage: number;
    performance_color: 'green' | 'yellow' | 'red';
  }>;
  total_members: number;
}

export interface PendingProject {
  task_id: number;
  title: string;
  board_name: string;
  column_name: string;
  assignee: string;
  priority: string;
  due_date: string | null;
  days_until_due: number | null;
  is_blocker: boolean;
  blocker_reason: string | null;
  is_overdue: boolean;
}

export interface AuditResults {
  success: boolean;
  message: string;
  results: {
    audit_completed_at: string;
    tasks_marked_as_blockers: number;
    blocked_tasks: Array<{
      task_id: number;
      title: string;
      assignee: string;
      due_date: string;
      days_until_due: number;
      reason: string;
    }>;
    reassigned_tasks?: Array<{
      task_id: number;
      title: string;
      old_assignee: string;
      new_assignee: string;
      days_overdue: number;
    }>;
    statistics: {
      total_tasks: number;
      tasks_with_due_dates: number;
      overdue_tasks: number;
      due_soon_tasks: number;
      blocked_tasks: number;
      completed_tasks: number;
      pending_tasks: number;
    };
  };
}

/**
 * Hook to get detailed statistics for a specific member
 */
export function useMemberStatistics(userId: number | null) {
  return useQuery<MemberStatistics>({
    queryKey: ['member-statistics', userId],
    queryFn: async () => {
      if (!userId) throw new Error('User ID is required');
      const response = await apiClient.get(`/api/analytics/member/${userId}/stats`);
      return response.data;
    },
    enabled: !!userId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to get team overview with performance indicators
 */
export function useTeamOverview() {
  return useQuery<TeamOverview>({
    queryKey: ['team-overview'],
    queryFn: async () => {
      const response = await apiClient.get('/api/analytics/team/overview');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Hook to run audit and mark overdue tasks as blockers
 */
export function useRunAudit() {
  const queryClient = useQueryClient();
  
  return useMutation<AuditResults, Error>({
    mutationFn: async () => {
      const response = await apiClient.post('/api/analytics/audit/run');
      return response.data;
    },
    onSuccess: () => {
      // Invalidate related queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['pending-projects'] });
      queryClient.invalidateQueries({ queryKey: ['boards'] });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}

/**
 * Hook to get pending projects
 */
export function usePendingProjects() {
  return useQuery<{ pending_projects: PendingProject[]; total_pending: number }>({
    queryKey: ['pending-projects'],
    queryFn: async () => {
      const response = await apiClient.get('/api/analytics/audit/pending-projects');
      return response.data;
    },
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

/**
 * Hook to clear all blocker flags
 */
export function useClearBlockers() {
  const queryClient = useQueryClient();
  
  return useMutation<{ success: boolean; message: string; tasks_cleared: number }, Error>({
    mutationFn: async () => {
      const response = await apiClient.post('/api/analytics/audit/clear-blockers');
      return response.data;
    },
    onSuccess: () => {
      // Invalidate related queries to refresh data
      queryClient.invalidateQueries({ queryKey: ['pending-projects'] });
      queryClient.invalidateQueries({ queryKey: ['boards'] });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}