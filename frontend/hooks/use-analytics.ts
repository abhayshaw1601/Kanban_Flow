import { useQuery } from '@tanstack/react-query';
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