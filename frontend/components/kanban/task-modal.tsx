'use client';

import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Calendar, Trash2, User, Brain, Sparkles, CheckCircle, AlertTriangle } from 'lucide-react';
import { format } from 'date-fns';
import { toast } from 'sonner';
import dynamic from 'next/dynamic';
import { useCurrentUser } from '@/hooks/use-current-user';
import { useBoardMembers } from '@/hooks/use-board-members';
import { useUpdateTask, useDeleteTask, useCreateTask } from '@/hooks/use-tasks';
import { useAnalyzeTask, useAIAnalyzerHealth, useCreateSubTasks, useEnhanceTask } from '@/hooks/use-ai-analyzer';
import { aiAnalyzer } from '@/lib/ai-analyzer';
import type { Task, Column } from '@/hooks/use-board';

// Dynamically import markdown editor to avoid SSR issues
const MDEditor = dynamic(
  () => import('@uiw/react-md-editor').then((mod) => mod.default),
  { ssr: false }
);

interface TaskModalProps {
  task: Task | null;
  boardId: number;
  columns: Column[];
  isOpen: boolean;
  onClose: () => void;
}

export function TaskModal({ task, boardId, columns, isOpen, onClose }: TaskModalProps) {
  const { data: user } = useCurrentUser();
  const { data: members = [] } = useBoardMembers(boardId);
  const updateTask = useUpdateTask();
  const deleteTask = useDeleteTask();
  const createTask = useCreateTask();
  const analyzeTask = useAnalyzeTask();
  const enhanceTask = useEnhanceTask();
  const createSubTasks = useCreateSubTasks();
  const { data: isAIHealthy = false } = useAIAnalyzerHealth();

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    due_date: '',
    priority: 'medium' as 'low' | 'medium' | 'high',
    assignee_id: null as number | null,
  });

  const [showAIOptions, setShowAIOptions] = useState(false);
  const [aiAnalysisMode, setAIAnalysisMode] = useState<'enhance' | 'subtasks'>('enhance');

  const isAdmin = user?.role === 'admin';
  const isHighPriority = formData.priority === 'high';
  const canUseAI = isAIHealthy && isHighPriority;

  // Update form data when task changes
  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title,
        description: task.description || '',
        due_date: task.due_date ? format(new Date(task.due_date), 'yyyy-MM-dd') : '',
        priority: task.priority,
        assignee_id: task.assignee_id,
      });
    }
  }, [task]);

  const handleSave = async () => {
    if (!task) return;

    try {
      const updateData: any = {
        title: formData.title,
        description: formData.description || null,
        priority: formData.priority,
        assignee_id: formData.assignee_id,
      };

      // Only include due_date if it's provided
      if (formData.due_date) {
        updateData.due_date = new Date(formData.due_date).toISOString();
      } else {
        updateData.due_date = null;
      }

      await updateTask.mutateAsync({
        taskId: task.id,
        data: updateData,
      });

      toast.success('Task updated successfully');
      onClose();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to update task';
      toast.error(errorMessage);
    }
  };

  const handleDelete = async () => {
    if (!task || !isAdmin) return;

    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await deleteTask.mutateAsync(task.id);
      toast.success('Task deleted successfully');
      onClose();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to delete task';
      toast.error(errorMessage);
    }
  };

  const handleAIAnalysis = async () => {
    if (!task || !canUseAI) return;

    try {
      const context = `Kanban board task management system. Board has columns: ${columns.map(c => c.name).join(', ')}`;
      
      if (aiAnalysisMode === 'enhance') {
        // Use the backend enhance endpoint
        await enhanceTask.mutateAsync({
          taskId: task.id,
          request: {
            prompt: formData.title,
            context: context + (formData.description ? `\n\nCurrent description: ${formData.description}` : ''),
          }
        });
        
        toast.success('Task enhanced with AI analysis!');
        // Refresh to show updated description
        window.location.reload();
      } else {
        // Create sub-tasks mode
        const analysis = await analyzeTask.mutateAsync({
          prompt: formData.title,
          context: context + (formData.description ? `\n\nCurrent description: ${formData.description}` : ''),
        });

        const currentColumnIndex = columns.findIndex(col => col.id === task.column_id);
        const targetColumnId = currentColumnIndex > 0 ? columns[0].id : task.column_id; // Use first column for sub-tasks
        
        const subTasksData = aiAnalyzer.createSubTasksData(analysis, task, targetColumnId);
        
        await createSubTasks.mutateAsync({
          subTasks: subTasksData,
          createTaskFn: (taskData) => createTask.mutateAsync(taskData),
        });

        toast.success(`Created ${subTasksData.length} sub-tasks from AI analysis!`);
      }

      setShowAIOptions(false);
    } catch (error: any) {
      console.error('AI Analysis failed:', error);
      toast.error('AI analysis failed. Please try again.');
    }
  };

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

  if (!task) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Edit Task</span>
            <div className="flex items-center gap-2">
              <Badge className={`text-xs ${getPriorityColor(formData.priority)}`}>
                {formData.priority.toUpperCase()}
              </Badge>
              {canUseAI && (
                <Badge variant="outline" className="text-xs bg-gradient-to-r from-purple-100 to-blue-100 text-purple-800 border-purple-200">
                  <Sparkles className="w-3 h-3 mr-1" />
                  AI Ready
                </Badge>
              )}
            </div>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="Task title"
            />
          </div>

          {/* AI Analyzer Section - Only show for high priority tasks */}
          {canUseAI && (
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-700">
              <div className="flex items-center gap-2 mb-3">
                <Brain className="w-5 h-5 text-purple-600" />
                <h3 className="font-semibold text-purple-800 dark:text-purple-300">AI Task Analyzer</h3>
                <Badge variant="outline" className="text-xs bg-green-100 text-green-800 border-green-200">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Available
                </Badge>
              </div>
              
              {!showAIOptions ? (
                <div className="space-y-3">
                  <p className="text-sm text-purple-700 dark:text-purple-300">
                    High-priority task detected! Use AI to automatically break down this task into structured sub-tasks and acceptance criteria.
                  </p>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setShowAIOptions(true)}
                    className="bg-white hover:bg-purple-50 border-purple-300 text-purple-700"
                  >
                    <Sparkles className="w-4 h-4 mr-2" />
                    Analyze with AI
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label className="text-sm font-medium text-purple-800 dark:text-purple-300">
                      Choose Analysis Mode:
                    </Label>
                    <div className="grid grid-cols-2 gap-2">
                      <Button
                        type="button"
                        variant={aiAnalysisMode === 'enhance' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setAIAnalysisMode('enhance')}
                        className="text-xs"
                      >
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Enhance Description
                      </Button>
                      <Button
                        type="button"
                        variant={aiAnalysisMode === 'subtasks' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setAIAnalysisMode('subtasks')}
                        className="text-xs"
                      >
                        <AlertTriangle className="w-3 h-3 mr-1" />
                        Create Sub-tasks
                      </Button>
                    </div>
                  </div>
                  
                  <div className="text-xs text-purple-600 dark:text-purple-400 bg-purple-100 dark:bg-purple-900/30 p-2 rounded">
                    {aiAnalysisMode === 'enhance' 
                      ? '🔍 AI will analyze your task and add structured breakdown, acceptance criteria, and potential blockers to the description.'
                      : '📋 AI will create separate sub-tasks based on technical breakdown of your high-priority task.'
                    }
                  </div>
                  
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      size="sm"
                      onClick={handleAIAnalysis}
                      disabled={analyzeTask.isPending || createSubTasks.isPending || enhanceTask.isPending}
                      className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white"
                    >
                      {analyzeTask.isPending || createSubTasks.isPending || enhanceTask.isPending ? (
                        <>
                          <Brain className="w-4 h-4 mr-2 animate-pulse" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4 mr-2" />
                          Run Analysis
                        </>
                      )}
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => setShowAIOptions(false)}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}

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

          {/* Due Date and Priority Row */}
          <div className="grid grid-cols-2 gap-4">
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
          <div className="flex items-center justify-between pt-4">
            <div>
              {isAdmin && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleDelete}
                  disabled={deleteTask.isPending}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete Task
                </Button>
              )}
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={updateTask.isPending || !formData.title.trim()}
              >
                {updateTask.isPending ? 'Saving...' : 'Save Changes'}
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}