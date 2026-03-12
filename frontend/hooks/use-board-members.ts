'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export interface BoardMember {
  id: number;
  name: string;
  email: string;
  avatar: string | null;
  role: 'admin' | 'employee';
}

export function useBoardMembers(boardId: number) {
  return useQuery<BoardMember[]>({
    queryKey: ['board-members', boardId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/members/${boardId}`);
      return response.data;
    },
    enabled: !!boardId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useAddBoardMember() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ userId, boardId }: { userId: number; boardId: number }) => {
      const response = await apiClient.post('/api/members', {
        user_id: userId,
        board_id: boardId,
      });
      return response.data;
    },
    onSuccess: (_, { boardId }) => {
      // Invalidate board members queries
      queryClient.invalidateQueries({ queryKey: ['board-members', boardId] });
      queryClient.invalidateQueries({ queryKey: ['board', boardId.toString()] });
    },
  });
}

export function useRemoveBoardMember() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ userId, boardId }: { userId: number; boardId: number }) => {
      const response = await apiClient.delete('/api/members', {
        data: {
          user_id: userId,
          board_id: boardId,
        },
      });
      return response.data;
    },
    onSuccess: (_, { boardId }) => {
      // Invalidate board members queries
      queryClient.invalidateQueries({ queryKey: ['board-members', boardId] });
      queryClient.invalidateQueries({ queryKey: ['board', boardId.toString()] });
    },
  });
}