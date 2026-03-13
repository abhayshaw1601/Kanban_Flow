'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export interface TaskComment {
  id: number;
  content: string;
  is_ai_generated: boolean;
  author: {
    id: number | null;
    name: string;
    email: string;
  };
  created_at: string;
  updated_at: string;
}

export interface TaskCommentsResponse {
  comments: TaskComment[];
  total_comments: number;
  ai_comments: number;
}

/**
 * Hook to get comments for a specific task
 */
export function useTaskComments(taskId: number | null) {
  return useQuery<TaskCommentsResponse>({
    queryKey: ['task-comments', taskId],
    queryFn: async () => {
      if (!taskId) throw new Error('Task ID is required');
      const response = await apiClient.get(`/api/comments/task/${taskId}`);
      return response.data;
    },
    enabled: !!taskId,
    staleTime: 30 * 1000, // 30 seconds
  });
}

/**
 * Hook to get the latest AI comment for a task (for display on task cards)
 */
export function useLatestAIComment(taskId: number | null) {
  const { data: commentsData } = useTaskComments(taskId);
  
  const latestAIComment = commentsData?.comments
    .filter(comment => comment.is_ai_generated)
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0];
  
  return {
    latestAIComment,
    hasAIComments: (commentsData?.ai_comments || 0) > 0
  };
}