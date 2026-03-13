'use client';

import { useState } from 'react';
import { ArrowRight, X, Clock, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';

interface ReassignedTask {
  task_id: number;
  title: string;
  board_name: string;
  column_name: string;
  priority: string;
  due_date: string | null;
  days_until_due: number | null;
  blocker_reason: string | null;
  is_overdue: boolean;
  previous_assignee?: string;
}

interface ReassignmentNotificationProps {
  reassignedTasks: ReassignedTask[];
  onDismiss: () => void;
  onViewTask: (taskId: number) => void;
}

export function ReassignmentNotification({ reassignedTasks, onDismiss, onViewTask }: ReassignmentNotificationProps) {
  const [isVisible, setIsVisible] = useState(true);

  // Encouraging messages for high performers getting reassigned tasks
  const encouragementMessages = [
    "🌟 You're our top performer! We're counting on you!",
    "💪 Your excellent track record makes you perfect for these critical tasks!",
    "🎯 These urgent tasks need someone reliable - that's you!",
    "🚀 Your skills are needed to save the day!",
    "⭐ We trust you to handle these important assignments!",
    "🏆 You're the MVP - time to show your expertise!",
    "💎 These tasks require a diamond-level performer like you!",
    "🔥 Your success rate speaks for itself - take charge!",
    "⚡ Lightning-fast delivery expected from our star player!",
    "🎪 The spotlight is on you - time to perform!"
  ];

  const getRandomEncouragementMessage = () => {
    return encouragementMessages[Math.floor(Math.random() * encouragementMessages.length)];
  };

  const [encouragementMessage] = useState(getRandomEncouragementMessage());

  if (!isVisible || reassignedTasks.length === 0) {
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
        <CardHeader className="bg-green-50 dark:bg-green-900/20 border-b border-green-200 dark:border-green-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-full">
                <Star className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <CardTitle className="text-green-900 dark:text-green-100">
                  🌟 New High-Priority Tasks Assigned
                </CardTitle>
                <CardDescription className="text-green-700 dark:text-green-300 font-medium">
                  {encouragementMessage}
                </CardDescription>
                <CardDescription className="text-green-600 dark:text-green-400 text-sm mt-1">
                  {reassignedTasks.length} urgent task{reassignedTasks.length > 1 ? 's have' : ' has'} been reassigned to you due to your excellent performance
                </CardDescription>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleDismiss}
              className="text-green-600 hover:text-green-700 hover:bg-green-100 dark:text-green-400 dark:hover:text-green-300 dark:hover:bg-green-900/30"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="p-0 max-h-96 overflow-y-auto">
          <div className="space-y-0">
            {reassignedTasks.map((task, index) => (
              <div
                key={task.task_id}
                className={`p-4 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors ${
                  index === reassignedTasks.length - 1 ? 'border-b-0' : ''
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
                      
                      {task.previous_assignee && (
                        <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                          <ArrowRight className="w-4 h-4" />
                          <span>Reassigned from: <strong>{task.previous_assignee}</strong></span>
                        </div>
                      )}
                      
                      {task.due_date && (
                        <div className="flex items-center gap-2">
                          <Clock className="w-4 h-4" />
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
                        <div className="flex items-start gap-2 mt-2 p-2 bg-orange-50 dark:bg-orange-900/20 rounded text-orange-800 dark:text-orange-400">
                          <Clock className="w-4 h-4 mt-0.5 flex-shrink-0" />
                          <span><strong>Reason:</strong> {task.blocker_reason}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <Button
                    onClick={() => onViewTask(task.task_id)}
                    className="bg-green-600 hover:bg-green-700 text-white"
                  >
                    Take Action
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
        
        <div className="p-4 bg-green-50 dark:bg-green-800 border-t">
          <div className="flex items-center justify-between">
            <p className="text-sm text-green-700 dark:text-green-300">
              🏆 You were chosen for these tasks because of your outstanding performance record!
            </p>
            <Button onClick={handleDismiss} variant="outline" className="border-green-300 text-green-700 hover:bg-green-100">
              Let's Do This!
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}