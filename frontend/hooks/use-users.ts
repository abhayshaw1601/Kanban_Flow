'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export interface User {
  id: number;
  name: string;
  email: string;
  avatar: string | null;
  role: 'admin' | 'employee';
  created_at: string;
}

export function useUsers() {
  return useQuery<User[]>({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await apiClient.get('/api/users');
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}