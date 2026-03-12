'use client';

import { useState } from 'react';
import { Draggable } from '@hello-pangea/dnd';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Calendar, ChevronRight, ArrowRight } from 'lucide-react';
import { format, isPast } from 'date-fns';
import { TaskModal } from './task-modal';
import { useMoveTask } from '@/hooks/use-tasks';
import { toast } from 'sonner';
import type { Task, Column } from '@/hooks/use-board';

interface TaskCardProps {
  task: Task;
  index: number;
  boardId: number;
  columns: Column[];
}

export function TaskCard({ task, index, boardId, columns }: TaskCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const moveTaskMutation = useMoveTask();

  // Get priority badge color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400';
      case 'low':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
    }
  };

  // Check if due date is overdue
  const isOverdue = task.due_date ? isPast(new Date(task.due_date)) : false;

  // Get assignee initials
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  // Get next column for quick progression
  const getNextColumn = () => {
    const currentColumnIndex = columns.findIndex(col => col.id === task.column_id);
    if (currentColumnIndex < columns.length - 1) {
      return columns[currentColumnIndex + 1];
    }
    return null;
  };

  const handleQuickMove = async (e: React.MouseEvent) => {
    e.stopPropagation();
    const nextColumn = getNextColumn();
    if (!nextColumn) return;

    try {
      await moveTaskMutation.mutateAsync({
        taskId: task.id,
        columnId: nextColumn.id,
        order: 0, // Move to top of next column
      });
      toast.success(`Task moved to ${nextColumn.name}`);
    } catch (error) {
      toast.error('Failed to move task');
    }
  };

  const handleClick = () => {
    setIsModalOpen(true);
  };

  const nextColumn = getNextColumn();

  return (
    <>
      <Draggable draggableId={task.id.toString()} index={index}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.draggableProps}
            {...provided.dragHandleProps}
            onClick={handleClick}
            className={`bg-white dark:bg-gray-700 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-600 cursor-pointer hover:shadow-md transition-shadow group ${
              snapshot.isDragging ? 'rotate-2 shadow-lg' : ''
            }`}
          >
            {/* Task Title */}
            <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2 line-clamp-2">
              {task.title}
            </h4>

            {/* Priority Badge */}
            <div className="flex items-center justify-between mb-3">
              <Badge
                variant="secondary"
                className={`text-xs ${getPriorityColor(task.priority)}`}
              >
                {task.priority.toUpperCase()}
              </Badge>
            </div>

            {/* Due Date */}
            {task.due_date && (
              <div className="flex items-center gap-2 mb-3">
                <Calendar className="w-4 h-4 text-gray-400" />
                <span
                  className={`text-sm ${
                    isOverdue
                      ? 'text-red-600 dark:text-red-400 font-medium'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}
                >
                  {format(new Date(task.due_date), 'MMM d, yyyy')}
                </span>
              </div>
            )}

            {/* Assignee and Quick Move */}
            <div className="flex items-center justify-between">
              {task.assignee && (
                <div className="flex items-center gap-2">
                  <Avatar className="w-6 h-6">
                    <AvatarFallback className="text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                      {getInitials(task.assignee.name)}
                    </AvatarFallback>
                  </Avatar>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {task.assignee.name}
                  </span>
                </div>
              )}
              
              {/* Quick Move Button */}
              {nextColumn && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleQuickMove}
                  disabled={moveTaskMutation.isPending}
                  className="h-6 px-2 text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                  title={`Move to ${nextColumn.name}`}
                >
                  <ArrowRight className="h-3 w-3" />
                </Button>
              )}
            </div>
          </div>
        )}
      </Draggable>

      {/* Task Modal */}
      <TaskModal
        task={task}
        boardId={boardId}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </>
  );
}