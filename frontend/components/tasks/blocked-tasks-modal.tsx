'use client';

import { X, Calendar, AlertTriangle, Clock, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { useBlockerNotifications } from '@/hooks/use-blocker-notifications';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

interface BlockedTasksModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function BlockedTasksModal({ isOpen, onClose }: BlockedTasksModalProps) {
  const { blockedTasks, totalBlocked } = useBlockerNotifications();
  const router = useRouter();

  if (!isOpen) return null;

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  const handleViewTask = async (taskId: number, boardName: string) => {
    try {
      // Get all boards to find the one containing this task
      const response = await fetch('/api/boards', {
        credentials: 'include'
      });
      if (response.ok) {
        const boards = await response.json();
        const board = boards.find((b: any) => b.name === boardName);
        if (board) {
          router.push(`/dashboard/boards/${board.id}`);
          toast.success(`Navigating to ${boardName} board`);
          onClose();
        } else {
          router.push('/dashboard/boards');
          toast.info('Navigating to boards page');
          onClose();
        }
      } else {
        router.push('/dashboard/boards');
        onClose();
      }
    } catch (error) {
      console.error('Error finding board:', error);
      router.push('/dashboard/boards');
      onClose();
    }
  };

  // Get aggressive nagging message
  const nagMessages = [
    "🔥 Your tasks are burning! Time to put out the fire!",
    "⚡ These blockers won't resolve themselves. Get moving!",
    "🚨 URGENT: Your team is waiting on YOU!",
    "💥 Stop procrastinating! These tasks need action NOW!",
    "⏰ Time is money, and you're wasting both!",
    "🎯 Focus up! Your deadlines are screaming at you!",
    "🌪️ Task tornado incoming! Handle these blockers ASAP!",
    "🔔 Wake up call! Your projects are in danger!",
    "💪 Show these tasks who's boss! Take action!",
    "🚀 Launch into action! These blockers need clearing!"
  ];

  const randomNagMessage = nagMessages[Math.floor(Math.random() * nagMessages.length)];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <CardHeader className="bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-full">
                <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400" />
              </div>
              <div>
                <CardTitle className="text-red-900 dark:text-red-100 flex items-center gap-2">
                  🚨 All Blocked Tasks
                  <Badge className="bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400">
                    {totalBlocked} Total
                  </Badge>
                </CardTitle>
                <CardDescription className="text-red-700 dark:text-red-300 font-medium">
                  {randomNagMessage}
                </CardDescription>
                <CardDescription className="text-red-600 dark:text-red-400 text-sm mt-1">
                  These tasks require immediate attention to prevent project delays
                </CardDescription>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="text-red-600 hover:text-red-700 hover:bg-red-100 dark:text-red-400 dark:hover:text-red-300 dark:hover:bg-red-900/30"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </CardHeader>

        {/* Content */}
        <CardContent className="p-0 max-h-96 overflow-y-auto">
          {blockedTasks.length === 0 ? (
            <div className="p-8 text-center">
              <AlertTriangle className="w-12 h-12 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                No Blocked Tasks!
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Great job! You have no blocked tasks at the moment.
              </p>
            </div>
          ) : (
            <div className="space-y-0">
              {blockedTasks.map((task, index) => (
                <div
                  key={task.task_id}
                  className={`p-4 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors cursor-pointer ${
                    index === blockedTasks.length - 1 ? 'border-b-0' : ''
                  }`}
                  onClick={() => handleViewTask(task.task_id, task.board_name)}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-semibold text-gray-900 dark:text-gray-100 truncate">
                          {task.title}
                        </h4>
                        <Badge className={getPriorityColor(task.priority)}>
                          {task.priority.toUpperCase()}
                        </Badge>
                        <Badge className="bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400">
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          BLOCKER
                        </Badge>
                        {task.is_overdue && (
                          <Badge className="bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400">
                            OVERDUE
                          </Badge>
                        )}
                      </div>
                      
                      <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400 mb-2">
                        <div className="flex items-center gap-4">
                          <span><strong>Board:</strong> {task.board_name}</span>
                          <span><strong>Status:</strong> {task.column_name}</span>
                        </div>
                        
                        {task.due_date && (
                          <div className="flex items-center gap-2">
                            <Calendar className="w-4 h-4" />
                            <span className={task.is_overdue ? 'text-red-600 font-medium' : ''}>
                              Due: {format(new Date(task.due_date), 'MMM d, yyyy')}
                              {task.days_until_due !== null && (
                                <span className="ml-1">
                                  ({task.days_until_due < 0 
                                    ? `${Math.abs(task.days_until_due)} days overdue`
                                    : `${task.days_until_due} days left`
                                  })
                                </span>
                              )}
                            </span>
                          </div>
                        )}
                      </div>
                      
                      {task.blocker_reason && (
                        <div className="flex items-start gap-2 p-2 bg-red-50 dark:bg-red-900/20 rounded text-sm text-red-800 dark:text-red-400">
                          <Clock className="w-4 h-4 mt-0.5 flex-shrink-0" />
                          <span><strong>Reason:</strong> {task.blocker_reason}</span>
                        </div>
                      )}
                    </div>
                    
                    <ArrowRight className="w-4 h-4 text-gray-400 flex-shrink-0 mt-1" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
        
        <div className="p-4 bg-red-50 dark:bg-red-800 border-t">
          <div className="flex items-center justify-between">
            <p className="text-sm text-red-700 dark:text-red-300">
              💡 Click on any task to navigate to its board and take action
            </p>
            <Button onClick={onClose} variant="outline" className="border-red-300 text-red-700 hover:bg-red-100">
              I'll Handle These!
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}