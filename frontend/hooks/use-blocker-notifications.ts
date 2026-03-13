'use client';

import { useQuery } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import { useCurrentUser } from './use-current-user';

interface BlockedTask {
  task_id: number;
  title: string;
  board_name: string;
  column_name: string;
  priority: string;
  due_date: string | null;
  days_until_due: number | null;
  blocker_reason: string | null;
  is_overdue: boolean;
}

interface UserBlockedTasksResponse {
  blocked_tasks: BlockedTask[];
  total_blocked: number;
  last_checked: string;
}

/**
 * Hook to get blocked tasks for the current user
 */
export function useUserBlockedTasks() {
  const { data: currentUser } = useCurrentUser();
  
  return useQuery<UserBlockedTasksResponse>({
    queryKey: ['user-blocked-tasks', currentUser?.id],
    queryFn: async () => {
      if (!currentUser) throw new Error('User not authenticated');
      const response = await apiClient.get(`/api/analytics/user/${currentUser.id}/blocked-tasks`);
      return response.data;
    },
    enabled: !!currentUser && currentUser.role !== 'admin', // Only for non-admin users
    refetchInterval: 30 * 1000, // Check every 30 seconds
    staleTime: 15 * 1000, // Consider data stale after 15 seconds
  });
}

/**
 * Hook to manage blocker notification state
 */
export function useBlockerNotifications() {
  const [dismissedBlockers, setDismissedBlockers] = useState<Set<number>>(new Set());
  const [lastNotificationTime, setLastNotificationTime] = useState<string | null>(null);
  const { data: blockedTasksData } = useUserBlockedTasks();

  // Load dismissed blockers from localStorage
  useEffect(() => {
    const stored = localStorage.getItem('dismissedBlockers');
    const storedTime = localStorage.getItem('lastNotificationTime');
    
    if (stored) {
      try {
        setDismissedBlockers(new Set(JSON.parse(stored)));
      } catch (e) {
        console.error('Error loading dismissed blockers:', e);
      }
    }
    
    if (storedTime) {
      setLastNotificationTime(storedTime);
    }
  }, []);

  // Save dismissed blockers to localStorage
  useEffect(() => {
    localStorage.setItem('dismissedBlockers', JSON.stringify(Array.from(dismissedBlockers)));
  }, [dismissedBlockers]);

  // Get new blocked tasks (not dismissed and newer than last notification)
  const newBlockedTasks = blockedTasksData?.blocked_tasks.filter(task => {
    // Don't show dismissed tasks
    if (dismissedBlockers.has(task.task_id)) {
      return false;
    }
    
    // If we have a last notification time, only show tasks that are newer
    if (lastNotificationTime && blockedTasksData.last_checked) {
      return new Date(blockedTasksData.last_checked) > new Date(lastNotificationTime);
    }
    
    return true;
  }) || [];

  const dismissBlocker = (taskId: number) => {
    setDismissedBlockers(prev => new Set([...prev, taskId]));
  };

  const dismissAllBlockers = () => {
    if (blockedTasksData?.blocked_tasks) {
      const allTaskIds = blockedTasksData.blocked_tasks.map(task => task.task_id);
      setDismissedBlockers(new Set(allTaskIds));
      setLastNotificationTime(new Date().toISOString());
      localStorage.setItem('lastNotificationTime', new Date().toISOString());
    }
  };

  const resetDismissedBlockers = () => {
    setDismissedBlockers(new Set());
    setLastNotificationTime(null);
    localStorage.removeItem('dismissedBlockers');
    localStorage.removeItem('lastNotificationTime');
  };

  return {
    blockedTasks: blockedTasksData?.blocked_tasks || [],
    newBlockedTasks,
    totalBlocked: blockedTasksData?.total_blocked || 0,
    hasNewBlockers: newBlockedTasks.length > 0,
    dismissBlocker,
    dismissAllBlockers,
    resetDismissedBlockers,
  };
}