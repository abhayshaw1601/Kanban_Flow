'use client';

import { useState, useEffect } from 'react';
import { AlertTriangle, X, Clock, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';

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

interface BlockerNotificationProps {
  blockedTasks: BlockedTask[];
  onDismiss: () => void;
  onViewTask: (taskId: number) => void;
}

export function BlockerNotification({ blockedTasks, onDismiss, onViewTask }: BlockerNotificationProps) {
  const [isVisible, setIsVisible] = useState(true);

  if (!isVisible || blockedTasks.length === 0) {
    return null;
  }

  const handleDismiss = () => {
    setIsVisible(false);
    onDismiss();
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      case 'medium': return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'low': return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl max-h-[80vh] overflow-hidden">
        <CardHeader className="bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-full">
                <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400" />
              </div>
              <div>
                <CardTitle className="text-red-900 dark:text-red-100">
                  🚨 Urgent: Blocked Tasks Require Attention
                </CardTitle>
                <CardDescription className="text-red-700 dark:text-red-300">
                  You have {blockedTasks.length} task{blockedTasks.length > 1 ? 's' : ''} that {blockedTasks.length > 1 ? 'are' : 'is'} marked as blocker{blockedTasks.length > 1 ? 's' : ''} and need immediate action
                </CardDescription>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleDismiss}
              className="text-red-600 hover:text-red-700 hover:bg-red-100 dark:text-red-400 dark:hover:text-red-300 dark:hover:bg-red-900/30"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="p-0 max-h-96 overflow-y-auto">
          <div className="space-y-0">
            {blockedTasks.map((task, index) => (
              <div
                key={task.task_id}
                className={`p-4 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors ${
                  index === blockedTasks.length - 1 ? 'border-b-0' : ''
                }`}
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
                      {task.is_overdue && (
                        <Badge className="bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400">
                          OVERDUE
                        </Badge>
                      )}
                    </div>
                    
                    <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
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
                      
                      {task.blocker_reason && (
                        <div className="flex items-start gap-2 mt-2 p-2 bg-red-50 dark:bg-red-900/20 rounded text-red-800 dark:text-red-400">
                          <Clock className="w-4 h-4 mt-0.5 flex-shrink-0" />
                          <span><strong>Reason:</strong> {task.blocker_reason}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <Button
                    onClick={() => onViewTask(task.task_id)}
                    className="bg-red-600 hover:bg-red-700 text-white"
                  >
                    View Task
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
        
        <div className="p-4 bg-gray-50 dark:bg-gray-800 border-t">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              These tasks require immediate attention to prevent project delays
            </p>
            <Button onClick={handleDismiss} variant="outline">
              I'll Handle These
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}