'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export function useMoveTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ taskId, columnId, order }: { taskId: number; columnId: number; order: number }) => {
      const response = await apiClient.patch(`/api/tasks/${taskId}/move`, {
        column_id: columnId,
        order,
      });
      return response.data;
    },
    onSuccess: (_, { taskId }) => {
      // Invalidate board queries to refresh the data
      queryClient.invalidateQueries({ queryKey: ['board'] });
    },
  });
}

export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ taskId, data }: { taskId: number; data: any }) => {
      const response = await apiClient.patch(`/api/tasks/${taskId}`, data);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate board queries to refresh the data
      queryClient.invalidateQueries({ queryKey: ['board'] });
    },
  });
}

export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (taskId: number) => {
      const response = await apiClient.delete(`/api/tasks/${taskId}`);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate board queries to refresh the data
      queryClient.invalidateQueries({ queryKey: ['board'] });
    },
  });
}

export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: any) => {
      const response = await apiClient.post('/api/tasks', data);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate board queries to refresh the data
      queryClient.invalidateQueries({ queryKey: ['board'] });
    },
  });
}