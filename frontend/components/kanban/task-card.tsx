'use client';

import { useState } from 'react';
import { Draggable } from '@hello-pangea/dnd';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Calendar, ArrowRight, Brain, Sparkles, AlertTriangle, MessageCircle, Zap, ChevronDown, ChevronUp } from 'lucide-react';
import { format, isPast } from 'date-fns';
import { TaskModal } from './task-modal';
import { useMoveTask } from '@/hooks/use-tasks';
import { useAnalyzeTask, useAIAnalyzerHealth } from '@/hooks/use-ai-analyzer';
import { useLatestAIComment } from '@/hooks/use-task-comments';
import { aiAnalyzer } from '@/lib/ai-analyzer';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
import type { Task, Column } from '@/hooks/use-board';

interface TaskCardProps {
  task: Task;
  index: number;
  boardId: number;
  columns: Column[];
}

export function TaskCard({ task, index, boardId, columns }: TaskCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const moveTaskMutation = useMoveTask();
  const analyzeTask = useAnalyzeTask();
  const { data: isAIHealthy = false } = useAIAnalyzerHealth();
  const { latestAIComment, hasAIComments } = useLatestAIComment(task.id);

  // Content truncation logic
  const MAX_TITLE_LENGTH = 50;
  const MAX_COMMENT_LENGTH = 80;
  const MAX_BLOCKER_LENGTH = 60;

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const shouldShowReadMore = (text: string, maxLength: number) => {
    return text.length > maxLength;
  };

  // Get priority badge color and glow effect
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'medium':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'low':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getPriorityGlow = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'priority-high';
      case 'medium':
        return 'priority-medium';
      case 'low':
        return 'priority-low';
      default:
        return '';
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

  const handleAIAnalysis = async (e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!isAIHealthy) {
      toast.error('AI service is not available');
      return;
    }

    try {
      const context = `Kanban board task management system. Board has columns: ${columns.map(c => c.name).join(', ')}`;
      
      // Use the backend enhance endpoint directly
      await aiAnalyzer.enhanceTask(task.id, {
        prompt: task.title,
        context: context
      });

      toast.success('Task enhanced with AI analysis!');
      
      // Refresh the page to show updated description
      window.location.reload();
      
    } catch (error: any) {
      console.error('AI Analysis failed:', error);
      
      // Handle specific error types
      if (error.response?.status === 401) {
        toast.error('Please log in to use AI features');
      } else if (error.response?.status === 403) {
        toast.error('You do not have permission to use AI features');
      } else {
        toast.error('AI analysis failed. Please try again.');
      }
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
            className={cn(
              'task-card group relative h-[280px] flex flex-col',
              getPriorityGlow(task.priority),
              snapshot.isDragging && 'dragging'
            )}
          >
            {/* Gradient border for AI-enhanced tasks */}
            {task.description?.includes('Generated by AI Task Analyzer') && (
              <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-ai-violet-500/20 to-electric-blue-500/20 p-[1px]">
                <div className="h-full w-full rounded-xl bg-card" />
              </div>
            )}

            <div className="relative z-10 p-4 flex flex-col h-full">
              {/* Task Title with controls - Fixed height */}
              <div className="flex items-start justify-between mb-3 min-h-[50px]">
                <div className="flex-1 pr-2">
                  <h4 className="font-semibold text-foreground tracking-tight text-sm leading-tight">
                    {isExpanded || !shouldShowReadMore(task.title, MAX_TITLE_LENGTH) 
                      ? task.title 
                      : truncateText(task.title, MAX_TITLE_LENGTH)
                    }
                  </h4>
                  {shouldShowReadMore(task.title, MAX_TITLE_LENGTH) && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        setIsExpanded(!isExpanded);
                      }}
                      className="h-auto p-0 text-xs text-ai-violet-400 hover:text-ai-violet-300 mt-1"
                    >
                      {isExpanded ? (
                        <span className="flex items-center gap-1">
                          <ChevronUp className="h-3 w-3" />
                          Show less
                        </span>
                      ) : (
                        <span className="flex items-center gap-1">
                          <ChevronDown className="h-3 w-3" />
                          Read more
                        </span>
                      )}
                    </Button>
                  )}
                </div>
                
                {/* Action buttons - Fixed width */}
                <div className="flex items-start gap-1 ml-2 flex-shrink-0">
                  {/* Blocker Indicator */}
                  {task.is_blocker && (
                    <div 
                      className="flex items-center gap-1 px-2 py-1 bg-red-500/20 border border-red-500/30 rounded-full backdrop-blur-sm"
                      title={task.blocker_reason || 'Task marked as blocker'}
                    >
                      <AlertTriangle className="h-3 w-3 text-red-400" />
                    </div>
                  )}
                  
                  {/* AI Comment Indicator */}
                  {hasAIComments && (
                    <div 
                      className="flex items-center gap-1 px-2 py-1 bg-orange-500/20 border border-orange-500/30 rounded-full backdrop-blur-sm"
                      title="AI has left a comment on this task"
                    >
                      <MessageCircle className="h-3 w-3 text-orange-400" />
                    </div>
                  )}
                  
                  {/* AI Button */}
                  {isAIHealthy && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleAIAnalysis}
                      disabled={analyzeTask.isPending}
                      className="h-7 w-7 p-0 opacity-70 hover:opacity-100 transition-all duration-300 bg-gradient-to-r from-ai-violet-500/20 to-electric-blue-500/20 hover:from-ai-violet-500/30 hover:to-electric-blue-500/30 border border-ai-violet-500/30 rounded-lg backdrop-blur-sm flex-shrink-0"
                      title="Analyze with AI"
                    >
                      {analyzeTask.isPending ? (
                        <Brain className="h-3 w-3 animate-pulse text-ai-violet-400" />
                      ) : (
                        <Sparkles className="h-3 w-3 text-ai-violet-400" />
                      )}
                    </Button>
                  )}
                </div>
              </div>

              {/* Scrollable content area - Flexible height */}
              <div className="flex-1 overflow-y-auto space-y-3 min-h-0 pr-1">
                {/* AI Nag Message */}
                {latestAIComment && (
                  <div className="p-2 bg-orange-500/10 border border-orange-500/20 rounded-lg backdrop-blur-sm">
                    <div className="flex items-start gap-2">
                      <MessageCircle className="w-3 h-3 text-orange-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-xs font-semibold text-orange-300 mb-1 tracking-tight">
                          🤖 AI PM:
                        </div>
                        <div className="text-xs text-orange-400 italic">
                          "{isExpanded || !shouldShowReadMore(latestAIComment.content, MAX_COMMENT_LENGTH)
                            ? latestAIComment.content
                            : truncateText(latestAIComment.content, MAX_COMMENT_LENGTH)
                          }"
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Blocker Reason */}
                {task.is_blocker && task.blocker_reason && (
                  <div className="p-2 bg-red-500/10 border border-red-500/20 rounded-lg backdrop-blur-sm">
                    <div className="flex items-start gap-2">
                      <AlertTriangle className="w-3 h-3 text-red-400 mt-0.5 flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <div className="text-xs font-semibold text-red-300 mb-1 tracking-tight">
                          BLOCKER:
                        </div>
                        <div className="text-xs text-red-400">
                          {isExpanded || !shouldShowReadMore(task.blocker_reason, MAX_BLOCKER_LENGTH)
                            ? task.blocker_reason
                            : truncateText(task.blocker_reason, MAX_BLOCKER_LENGTH)
                          }
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Due Date */}
                {task.due_date && (
                  <div className="flex items-center gap-2">
                    <Calendar className="w-3 h-3 text-muted-foreground flex-shrink-0" />
                    <span
                      className={cn(
                        'text-xs',
                        isOverdue
                          ? 'text-red-400 font-medium'
                          : 'text-muted-foreground'
                      )}
                    >
                      {format(new Date(task.due_date), 'MMM d, yyyy')}
                    </span>
                  </div>
                )}
              </div>

              {/* Fixed bottom section */}
              <div className="mt-3 pt-3 border-t border-white/10 space-y-2 flex-shrink-0">
                <div className="flex items-center justify-between">
                  <Badge
                    variant="secondary"
                    className={cn(
                      'text-xs font-medium border backdrop-blur-sm',
                      getPriorityColor(task.priority)
                    )}
                  >
                    {task.priority.toUpperCase()}
                  </Badge>
                  
                  {/* AI Analysis Status */}
                  {isAIHealthy && !task.description?.includes('Generated by AI Task Analyzer') && (
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-ai-violet-400 rounded-full animate-pulse"></div>
                      <span className="text-xs text-ai-violet-400 font-medium">AI Ready</span>
                    </div>
                  )}
                  
                  {task.description?.includes('Generated by AI Task Analyzer') && (
                    <div className="flex items-center gap-1">
                      <Zap className="w-3 h-3 text-ai-violet-400 animate-pulse" />
                      <span className="text-xs text-ai-violet-400 font-medium">AI Enhanced</span>
                    </div>
                  )}
                </div>

                {/* Assignee and Quick Move */}
                <div className="flex items-center justify-between">
                  {task.assignee && (
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <Avatar className="w-5 h-5 ring-1 ring-white/10 flex-shrink-0">
                        <AvatarFallback className="text-xs bg-gradient-to-br from-ai-violet-500/20 to-electric-blue-500/20 text-white font-medium border border-white/10">
                          {getInitials(task.assignee.name)}
                        </AvatarFallback>
                      </Avatar>
                      <span className="text-xs text-muted-foreground font-medium truncate">
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
                      className="h-6 px-2 text-xs opacity-0 group-hover:opacity-100 transition-all duration-300 hover:bg-white/10 border border-transparent hover:border-white/20 rounded-lg flex-shrink-0"
                      title={`Move to ${nextColumn.name}`}
                    >
                      <ArrowRight className="h-3 w-3" />
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </Draggable>

      {/* Task Modal */}
      <TaskModal
        task={task}
        boardId={boardId}
        columns={columns}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </>
  );
}