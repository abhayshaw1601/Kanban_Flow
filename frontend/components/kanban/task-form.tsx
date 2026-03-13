'use client';

import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Calendar, User, Brain, Sparkles } from 'lucide-react';
import { toast } from 'sonner';
import dynamic from 'next/dynamic';
import { useBoardMembers } from '@/hooks/use-board-members';
import { useCreateTask } from '@/hooks/use-tasks';
import { useAnalyzeTask, useAIAnalyzerHealth } from '@/hooks/use-ai-analyzer';
import { aiAnalyzer } from '@/lib/ai-analyzer';
import type { Column } from '@/hooks/use-board';

// Dynamically import markdown editor to avoid SSR issues
const MDEditor = dynamic(
  () => import('@uiw/react-md-editor').then((mod) => mod.default),
  { ssr: false }
);

interface TaskFormProps {
  boardId: number;
  columns: Column[];
  defaultColumnId?: number;
  isOpen: boolean;
  onClose: () => void;
}

export function TaskForm({ boardId, columns, defaultColumnId, isOpen, onClose }: TaskFormProps) {
  const { data: members = [] } = useBoardMembers(boardId);
  const createTask = useCreateTask();
  const analyzeTask = useAnalyzeTask();
  const { data: isAIHealthy = false } = useAIAnalyzerHealth();

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    due_date: '',
    priority: 'medium' as 'low' | 'medium' | 'high',
    column_id: defaultColumnId || columns[0]?.id || 0,
    assignee_id: null as number | null,
  });

  const [useAIEnhancement, setUseAIEnhancement] = useState(false);

  const isHighPriority = formData.priority === 'high';
  const canUseAI = isAIHealthy && isHighPriority;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.title.trim()) {
      toast.error('Task title is required');
      return;
    }

    try {
      let taskDescription = formData.description;

      // If AI enhancement is enabled and it's a high priority task
      if (useAIEnhancement && canUseAI && formData.title.trim()) {
        try {
          const context = `Kanban board task management system. Board has columns: ${columns.map(c => c.name).join(', ')}`;
          const analysis = await analyzeTask.mutateAsync({
            prompt: formData.title,
            context: context + (formData.description ? `\n\nInitial description: ${formData.description}` : ''),
          });

          taskDescription = aiAnalyzer.formatAnalysisAsMarkdown(analysis, formData.title);
          toast.success('Task enhanced with AI analysis!');
        } catch (error) {
          console.error('AI enhancement failed:', error);
          toast.warning('AI enhancement failed, creating task without AI analysis');
        }
      }

      const taskData: any = {
        title: formData.title.trim(),
        description: taskDescription || null,
        priority: formData.priority,
        column_id: formData.column_id,
        assignee_id: formData.assignee_id,
      };

      // Only include due_date if it's provided
      if (formData.due_date) {
        taskData.due_date = new Date(formData.due_date).toISOString();
      }

      await createTask.mutateAsync(taskData);

      toast.success('Task created successfully');
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        due_date: '',
        priority: 'medium',
        column_id: defaultColumnId || columns[0]?.id || 0,
        assignee_id: null,
      });
      setUseAIEnhancement(false);
      
      onClose();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to create task';
      toast.error(errorMessage);
    }
  };

  const handleClose = () => {
    // Reset form when closing
    setFormData({
      title: '',
      description: '',
      due_date: '',
      priority: 'medium',
      column_id: defaultColumnId || columns[0]?.id || 0,
      assignee_id: null,
    });
    setUseAIEnhancement(false);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Task</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title">Title *</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Enter task title"
              required
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <div className="min-h-[200px]">
              <MDEditor
                value={formData.description}
                onChange={(value) => setFormData({ ...formData, description: value || '' })}
                preview="edit"
                hideToolbar={false}
                visibleDragbar={false}
              />
            </div>
          </div>

          {/* Column and Priority Row */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="column">Column</Label>
              <Select
                value={formData.column_id.toString()}
                onValueChange={(value) =>
                  setFormData({ ...formData, column_id: parseInt(value) })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {columns.map((column) => (
                    <SelectItem key={column.id} value={column.id.toString()}>
                      {column.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="priority">Priority</Label>
              <Select
                value={formData.priority}
                onValueChange={(value: 'low' | 'medium' | 'high') =>
                  setFormData({ ...formData, priority: value })
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* AI Enhancement Option - Only show for high priority tasks */}
          {canUseAI && (
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-700">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  <Brain className="w-5 h-5 text-purple-600" />
                  <span className="font-medium text-purple-800 dark:text-purple-300">AI Enhancement</span>
                </div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useAIEnhancement}
                    onChange={(e) => setUseAIEnhancement(e.target.checked)}
                    className="rounded border-purple-300 text-purple-600 focus:ring-purple-500"
                  />
                  <span className="text-sm text-purple-700 dark:text-purple-300">
                    Auto-enhance with AI analysis
                  </span>
                </label>
              </div>
              {useAIEnhancement && (
                <p className="text-xs text-purple-600 dark:text-purple-400 mt-2 bg-purple-100 dark:bg-purple-900/30 p-2 rounded">
                  <Sparkles className="w-3 h-3 inline mr-1" />
                  AI will automatically analyze your high-priority task and add structured breakdown, acceptance criteria, and potential blockers.
                </p>
              )}
            </div>
          )}

          {/* Due Date */}
          <div className="space-y-2">
            <Label htmlFor="due_date">Due Date</Label>
            <div className="relative">
              <Calendar className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                id="due_date"
                type="date"
                value={formData.due_date}
                onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                className="pl-10"
              />
            </div>
          </div>

          {/* Assignee */}
          <div className="space-y-2">
            <Label htmlFor="assignee">Assignee</Label>
            <Select
              value={formData.assignee_id?.toString() || 'unassigned'}
              onValueChange={(value) =>
                setFormData({
                  ...formData,
                  assignee_id: value === 'unassigned' ? null : parseInt(value),
                })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="unassigned">
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-gray-400" />
                    <span>Unassigned</span>
                  </div>
                </SelectItem>
                {members.map((member) => (
                  <SelectItem key={member.id} value={member.id.toString()}>
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900/20 flex items-center justify-center text-xs text-blue-800 dark:text-blue-400">
                        {member.name.charAt(0).toUpperCase()}
                      </div>
                      <span>{member.name}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-2 pt-4">
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createTask.isPending || analyzeTask.isPending || !formData.title.trim()}
            >
              {createTask.isPending || analyzeTask.isPending ? (
                <>
                  {analyzeTask.isPending ? (
                    <>
                      <Brain className="w-4 h-4 mr-2 animate-pulse" />
                      AI Analyzing...
                    </>
                  ) : (
                    'Creating...'
                  )}
                </>
              ) : (
                <>
                  {useAIEnhancement && canUseAI && (
                    <Sparkles className="w-4 h-4 mr-2" />
                  )}
                  Create Task
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}