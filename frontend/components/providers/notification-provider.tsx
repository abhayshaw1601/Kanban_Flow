'use client';

import { useRouter } from 'next/navigation';
import { useBlockerNotifications } from '@/hooks/use-blocker-notifications';
import { BlockerNotification } from '@/components/notifications/blocker-notification';
import { ReassignmentNotification } from '@/components/notifications/reassignment-notification';
import { useCurrentUser } from '@/hooks/use-current-user';
import { useState } from 'react';

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

  const [showReassignmentNotification, setShowReassignmentNotification] = useState(false);

  // Only show notifications for non-admin users
  const shouldShowNotifications = currentUser && currentUser.role !== 'admin';

  // Check if user has recently reassigned tasks (tasks with reassignment reason in blocker_reason)
  const reassignedTasks = newBlockedTasks.filter(task => 
    task.blocker_reason && task.blocker_reason.includes('Reassigned from')
  );

  const regularBlockedTasks = newBlockedTasks.filter(task => 
    !task.blocker_reason || !task.blocker_reason.includes('Reassigned from')
  );

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

  const handleReassignmentDismiss = () => {
    setShowReassignmentNotification(false);
    dismissAllBlockers();
  };

  return (
    <>
      {children}
      
      {/* Show reassignment notification first if there are reassigned tasks */}
      {shouldShowNotifications && reassignedTasks.length > 0 && (
        <ReassignmentNotification
          reassignedTasks={reassignedTasks.map(task => ({
            ...task,
            previous_assignee: task.blocker_reason?.match(/Reassigned from (.+?) to/)?.[1] || 'Unknown'
          }))}
          onDismiss={handleReassignmentDismiss}
          onViewTask={handleViewTask}
        />
      )}
      
      {/* Show regular blocker notification if there are non-reassigned blocked tasks */}
      {shouldShowNotifications && regularBlockedTasks.length > 0 && reassignedTasks.length === 0 && (
        <BlockerNotification
          blockedTasks={regularBlockedTasks}
          onDismiss={handleDismiss}
          onViewTask={handleViewTask}
        />
      )}
    </>
  );
}