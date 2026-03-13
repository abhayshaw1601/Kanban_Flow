'use client';

import { useRouter } from 'next/navigation';
import { useBlockerNotifications } from '@/hooks/use-blocker-notifications';
import { BlockerNotification } from '@/components/notifications/blocker-notification';
import { useCurrentUser } from '@/hooks/use-current-user';

interface NotificationProviderProps {
  children: React.ReactNode;
}

export function NotificationProvider({ children }: NotificationProviderProps) {
  const router = useRouter();
  const { data: currentUser } = useCurrentUser();
  const {
    newBlockedTasks,
    hasNewBlockers,
    dismissAllBlockers,
  } = useBlockerNotifications();

  // Only show notifications for non-admin users
  const shouldShowNotifications = currentUser && currentUser.role !== 'admin';

  const handleViewTask = async (taskId: number) => {
    // Find the task to get board information
    const task = newBlockedTasks.find(t => t.task_id === taskId);
    if (task) {
      try {
        // Get all boards to find the one containing this task
        const response = await fetch('/api/boards', {
          credentials: 'include'
        });
        if (response.ok) {
          const boards = await response.json();
          // Find board by name (since we have board_name in the task)
          const board = boards.find((b: any) => b.name === task.board_name);
          if (board) {
            router.push(`/dashboard/boards/${board.id}`);
          } else {
            router.push('/dashboard/boards');
          }
        } else {
          router.push('/dashboard/boards');
        }
      } catch (error) {
        console.error('Error finding board:', error);
        router.push('/dashboard/boards');
      }
    }
    dismissAllBlockers();
  };

  const handleDismiss = () => {
    dismissAllBlockers();
  };

  return (
    <>
      {children}
      {shouldShowNotifications && hasNewBlockers && (
        <BlockerNotification
          blockedTasks={newBlockedTasks}
          onDismiss={handleDismiss}
          onViewTask={handleViewTask}
        />
      )}
    </>
  );
}