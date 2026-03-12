'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

export interface Task {
  id: number;
  title: string;
  description: string | null;
  due_date: string | null;  // Backend uses snake_case
  priority: 'low' | 'medium' | 'high';
  order: number;
  column_id: number;        // Backend uses snake_case
  assignee_id: number | null; // Backend uses snake_case
  created_at: string;       // Backend uses snake_case
  updated_at: string;       // Backend uses snake_case
  assignee?: {
    id: number;
    name: string;
    email: string;
    avatar: string | null;
  };
}

export interface Column {
  id: number;
  name: string;
  order: number;
  board_id: number;         // Backend uses snake_case
  tasks: Task[];
}

export interface BoardDetail {
  id: number;
  name: string;
  description: string | null;
  created_at: string;       // Backend uses snake_case
  created_by: number;       // Backend uses snake_case
  columns: Column[];
}

export function useBoard(boardId: string) {
  return useQuery<BoardDetail>({
    queryKey: ['board', boardId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/boards/${boardId}`);
      return response.data;
    },
    enabled: !!boardId,
    staleTime: 30 * 1000, // 30 seconds
  });
}