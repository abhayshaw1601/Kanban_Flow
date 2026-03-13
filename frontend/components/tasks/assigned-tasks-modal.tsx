'use client';

import { useState } from 'react';
import { X, Calendar, AlertTriangle, CheckCircle, Clock, ArrowRight, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { useAssignedTasks, type AssignedTask } from '@/hooks/use-assigned-tasks';
import { Loading } from '@/components/ui/loading';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

interface AssignedTasksModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type FilterType = 'all' | 'todo' | 'in_progress' | 'completed' | 'blocked' | 'overdue';

export function AssignedTasksModal({ isOpen, onClose }: AssignedTasksModalProps) {
  const { data: assignedTasksData, isLoading, error } = useAssignedTasks();
  const [filter, setFilter] = useState<FilterType>('all');
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

  const getStatusIcon = (task: AssignedTask) => {
    if (task.is_completed) return <CheckCircle className="w-4 h-4 text-green-600" />;
    if (task.is_in_progress) return <Clock className="w-4 h-4 text-blue-600" />;
    return <div className="w-4 h-4 rounded-full border-2 border-gray-400" />;
  };

  const getStatusColor = (task: AssignedTask) => {
    if (task.is_completed) return 'text-green-600 dark:text-green-400';
    if (task.is_in_progress) return 'text-blue-600 dark:text-blue-400';
    return 'text-gray-600 dark:text-gray-400';
  };

  const filterTasks = (tasks: AssignedTask[]) => {
    switch (filter) {
      case 'todo': return tasks.filter(t => !t.is_completed && !t.is_in_progress);
      case 'in_progress': return tasks.filter(t => t.is_in_progress);
      case 'completed': return tasks.filter(t => t.is_completed);
      case 'blocked': return tasks.filter(t => t.is_blocker);
      case 'overdue': return tasks.filter(t => t.is_overdue && !t.is_completed);
      default: return tasks;
    }
  };

  const handleViewTask = async (task: AssignedTask) => {
    try {
      router.push(`/dashboard/boards/${task.board_id}`);
      toast.success(`Navigating to ${task.board_name} board`);
      onClose();
    } catch (error) {
      console.error('Error navigating to board:', error);
      toast.error('Failed to navigate to board');
    }
  };

  const filteredTasks = assignedTasksData ? filterTasks(assignedTasksData.assigned_tasks) : [];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl max-h-[90vh] overflow-hidden">
        <CardHeader className="bg-blue-50 dark:bg-blue-900/20 border-b border-blue-200 dark:border-blue-800">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-blue-900 dark:text-blue-100 flex items-center gap-2">
                📋 My Assigned Tasks
                {assignedTasksData && (
                  <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                    {assignedTasksData.statistics.total_tasks} Total
                  </Badge>
                )}
              </CardTitle>
              <CardDescription className="text-blue-700 dark:text-blue-300">
                View and manage all your assigned tasks across all boards
              </CardDescription>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="text-blue-600 hover:text-blue-700 hover:bg-blue-100 dark:text-blue-400 dark:hover:text-blue-300 dark:hover:bg-blue-900/30"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </CardHeader>

        {/* Statistics */}
        {assignedTasksData && (
          <div className="p-4 bg-gray-50 dark:bg-gray-800 border-b">
            <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
              <div className="text-center">
                <div className="text-lg font-bold text-gray-900 dark:text-gray-100">
                  {assignedTasksData.statistics.todo_tasks}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">To Do</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-blue-600">
                  {assignedTasksData.statistics.in_progress_tasks}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">In Progress</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-green-600">
                  {assignedTasksData.statistics.completed_tasks}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Completed</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-red-600">
                  {assignedTasksData.statistics.blocked_tasks}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Blocked</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-orange-600">
                  {assignedTasksData.statistics.overdue_tasks}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Overdue</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-purple-600">
                  {assignedTasksData.statistics.completion_percentage}%
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">Complete</div>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="p-4 border-b bg-white dark:bg-gray-900">
          <div className="flex items-center gap-2 flex-wrap">
            <Filter className="w-4 h-4 text-gray-600" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filter:</span>
            {[
              { key: 'all', label: 'All Tasks', count: assignedTasksData?.statistics.total_tasks },
              { key: 'todo', label: 'To Do', count: assignedTasksData?.statistics.todo_tasks },
              { key: 'in_progress', label: 'In Progress', count: assignedTasksData?.statistics.in_progress_tasks },
              { key: 'completed', label: 'Completed', count: assignedTasksData?.statistics.completed_tasks },
              { key: 'blocked', label: 'Blocked', count: assignedTasksData?.statistics.blocked_tasks },
              { key: 'overdue', label: 'Overdue', count: assignedTasksData?.statistics.overdue_tasks },
            ].map(({ key, label, count }) => (
              <Button
                key={key}
                variant={filter === key ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter(key as FilterType)}
                className="text-xs"
              >
                {label} {count !== undefined && count > 0 && `(${count})`}
              </Button>
            ))}
          </div>
        </div>

        {/* Content */}
        <CardContent className="p-0 max-h-96 overflow-y-auto">
          {isLoading && (
            <div className="flex items-center justify-center p-8">
              <Loading size="lg" />
              <span className="ml-2 text-gray-600 dark:text-gray-400">Loading your tasks...</span>
            </div>
          )}

          {error && (
            <div className="p-8 text-center">
              <div className="text-red-600 dark:text-red-400 mb-2">Failed to load tasks</div>
              <Button onClick={() => window.location.reload()} variant="outline" size="sm">
                Retry
              </Button>
            </div>
          )}

          {assignedTasksData && filteredTasks.length === 0 && (
            <div className="p-8 text-center">
              <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                {filter === 'all' ? 'No tasks assigned' : `No ${filter.replace('_', ' ')} tasks`}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                {filter === 'all' 
                  ? 'You have no tasks assigned to you at the moment.'
                  : `You have no ${filter.replace('_', ' ')} tasks.`
                }
              </p>
            </div>
          )}

          {assignedTasksData && filteredTasks.length > 0 && (
            <div className="space-y-0">
              {filteredTasks.map((task, index) => (
                <div
                  key={task.task_id}
                  className={`p-4 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors cursor-pointer ${
                    index === filteredTasks.length - 1 ? 'border-b-0' : ''
                  }`}
                  onClick={() => handleViewTask(task)}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      {getStatusIcon(task)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium text-gray-900 dark:text-gray-100 truncate">
                            {task.title}
                          </h4>
                          <Badge className={getPriorityColor(task.priority)}>
                            {task.priority.toUpperCase()}
                          </Badge>
                          {task.is_blocker && (
                            <Badge className="bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400">
                              <AlertTriangle className="w-3 h-3 mr-1" />
                              BLOCKER
                            </Badge>
                          )}
                          {task.is_overdue && !task.is_completed && (
                            <Badge className="bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400">
                              OVERDUE
                            </Badge>
                          )}
                        </div>
                        
                        <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-2">
                          <span><strong>Board:</strong> {task.board_name}</span>
                          <span><strong>Status:</strong> <span className={getStatusColor(task)}>{task.column_name}</span></span>
                        </div>
                        
                        {task.due_date && (
                          <div className="flex items-center gap-2 text-sm">
                            <Calendar className="w-4 h-4" />
                            <span className={task.is_overdue && !task.is_completed ? 'text-red-600 font-medium' : 'text-gray-600 dark:text-gray-400'}>
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
                          <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 rounded text-sm text-red-800 dark:text-red-400">
                            <strong>Blocker Reason:</strong> {task.blocker_reason}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <ArrowRight className="w-4 h-4 text-gray-400 flex-shrink-0 mt-1" />
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
        
        <div className="p-4 bg-gray-50 dark:bg-gray-800 border-t">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Click on any task to navigate to its board
            </p>
            <Button onClick={onClose} variant="outline">
              Close
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}