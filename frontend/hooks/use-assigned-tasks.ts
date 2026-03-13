'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { useCurrentUser } from './use-current-user';

export interface AssignedTask {
  task_id: number;
  title: string;
  description: string | null;
  board_name: string;
  board_id: number;
  column_name: string;
  priority: 'low' | 'medium' | 'high';
  due_date: string | null;
  days_until_due: number | null;
  is_blocker: boolean;
  blocker_reason: string | null;
  is_overdue: boolean;
  is_completed: boolean;
  is_in_progress: boolean;
  created_at: string;
  updated_at: string;
}

export interface AssignedTasksResponse {
  assigned_tasks: AssignedTask[];
  statistics: {
    total_tasks: number;
    completed_tasks: number;
    in_progress_tasks: number;
    todo_tasks: number;
    blocked_tasks: number;
    overdue_tasks: number;
    completion_percentage: number;
  };
  last_checked: string;
}

/**
 * Hook to get all assigned tasks for the current user
 */
export function useAssignedTasks() {
  const { data: currentUser } = useCurrentUser();
  
  return useQuery<AssignedTasksResponse>({
    queryKey: ['assigned-tasks', currentUser?.id],
    queryFn: async () => {
      if (!currentUser) throw new Error('User not authenticated');
      const response = await apiClient.get(`/api/analytics/user/${currentUser.id}/assigned-tasks`);
      return response.data;
    },
    enabled: !!currentUser,
    staleTime: 2 * 60 * 1000, // 2 minutes
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });
}