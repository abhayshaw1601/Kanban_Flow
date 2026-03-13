'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';
import { toast } from 'sonner';

export function useDeleteUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const response = await apiClient.delete('/api/users/me');
      return response.data;
    },
    onSuccess: () => {
      // Clear all cached data
      queryClient.clear();
      toast.success('Account deleted successfully');
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || 'Failed to delete account';
      toast.error(errorMessage);
    },
  });
}