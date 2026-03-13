'use client';

import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Upload, FileImage, Brain, RefreshCw, CheckCircle, AlertCircle, Plus, Wand2 } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api';
import { useQueryClient } from '@tanstack/react-query';

interface CreatedTask {
  title: string;
  description: string;
  priority: string;
  component: string;
  estimated_effort: string;
  dependencies: string[];
}

interface TaskCreationResult {
  success: boolean;
  message: string;
  board_id: number;
  board_name: string;
  column_name: string;
  tasks_created: number;
  created_tasks: CreatedTask[];
  analysis_summary: {
    diagram_type: string;
    title: string;
    description: string;
    components_found: number;
    connections_found: number;
  };
}

interface DiagramTaskCreatorProps {
  boardId: number;
  boardName: string;
  isAdmin: boolean;
}

export function DiagramTaskCreator({ boardId, boardName, isAdmin }: DiagramTaskCreatorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [result, setResult] = useState<TaskCreationResult | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  // Don't render if not admin
  if (!isAdmin) {
    return null;
  }

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Please select an image file (PNG, JPEG, GIF, WebP)');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size must be less than 10MB');
      return;
    }

    setSelectedFile(file);
    setResult(null);

    // Create preview URL
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleCreateTasks = async () => {
    if (!selectedFile) {
      toast.error('Please select a diagram file first');
      return;
    }

    setIsCreating(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await apiClient.post(`/ai/create-tasks-from-diagram/${boardId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setResult(response.data);
        toast.success(`Created ${response.data.tasks_created} tasks from diagram!`);
        
        // Refresh the board data
        queryClient.invalidateQueries({ queryKey: ['board', boardId.toString()] });
      } else {
        throw new Error('Task creation failed');
      }
    } catch (error: any) {
      console.error('Task creation failed:', error);
      
      if (error.response?.status === 403) {
        toast.error('Only administrators can create tasks from diagrams');
      } else if (error.response?.status === 400) {
        toast.error(error.response.data.detail || 'Invalid diagram or board configuration');
      } else {
        toast.error('Failed to create tasks from diagram. Please try again.');
      }
    } finally {
      setIsCreating(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setResult(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    handleReset();
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
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <Wand2 className="w-4 h-4" />
          Create Tasks from Diagram
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5" />
            Create Tasks from Architecture Diagram
          </DialogTitle>
          <DialogDescription>
            Upload an architecture or flow diagram to automatically generate tasks for "{boardName}"
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {!result && (
            <>
              {/* File Upload Section */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Upload Diagram</CardTitle>
                  <CardDescription>
                    Select an architecture or flow diagram to analyze
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* File Upload */}
                    <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6">
                      <div className="text-center">
                        <FileImage className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <div className="space-y-2">
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            Upload your architecture or flow diagram
                          </p>
                          <p className="text-xs text-gray-500">
                            Supports PNG, JPEG, GIF, WebP (max 10MB)
                          </p>
                        </div>
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept="image/*"
                          onChange={handleFileSelect}
                          className="hidden"
                        />
                        <Button
                          onClick={() => fileInputRef.current?.click()}
                          variant="outline"
                          className="mt-4"
                        >
                          <Upload className="w-4 h-4 mr-2" />
                          Select File
                        </Button>
                      </div>
                    </div>

                    {/* Selected File Preview */}
                    {selectedFile && (
                      <div className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <h4 className="font-medium text-gray-900 dark:text-gray-100">
                              {selectedFile.name}
                            </h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                          </div>
                          <div className="flex gap-2">
                            <Button
                              onClick={handleCreateTasks}
                              disabled={isCreating}
                              className="bg-blue-600 hover:bg-blue-700"
                            >
                              {isCreating ? (
                                <>
                                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                                  Creating Tasks...
                                </>
                              ) : (
                                <>
                                  <Plus className="w-4 h-4 mr-2" />
                                  Create Tasks
                                </>
                              )}
                            </Button>
                            <Button variant="outline" onClick={handleReset}>
                              Reset
                            </Button>
                          </div>
                        </div>

                        {/* Image Preview */}
                        {previewUrl && (
                          <div className="mt-4">
                            <img
                              src={previewUrl}
                              alt="Diagram preview"
                              className="max-w-full max-h-96 object-contain border rounded"
                            />
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </>
          )}

          {/* Results Section */}
          {result && (
            <div className="space-y-6">
              {/* Success Summary */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-green-600">
                    <CheckCircle className="w-5 h-5" />
                    Tasks Created Successfully!
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {result.tasks_created}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">Tasks Created</div>
                    </div>
                    <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">
                        {result.analysis_summary.components_found}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">Components</div>
                    </div>
                    <div className="text-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">
                        {result.analysis_summary.connections_found}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">Connections</div>
                    </div>
                    <div className="text-center p-3 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                      <div className="text-lg font-bold text-orange-600">
                        {result.analysis_summary.diagram_type.toUpperCase()}
                      </div>
                      <div className="text-sm text-gray-600 dark:text-gray-400">Diagram Type</div>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <h4 className="font-semibold text-gray-900 dark:text-gray-100">
                      {result.analysis_summary.title}
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {result.analysis_summary.description}
                    </p>
                    <p className="text-sm text-blue-600 dark:text-blue-400">
                      Tasks added to "{result.column_name}" column in "{result.board_name}"
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Created Tasks List */}
              <Card>
                <CardHeader>
                  <CardTitle>Created Tasks ({result.created_tasks.length})</CardTitle>
                  <CardDescription>
                    These tasks are now available on your board and can be assigned to team members
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {result.created_tasks.map((task, index) => (
                      <div key={index} className="border rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-medium text-gray-900 dark:text-gray-100">
                            {task.title}
                          </h4>
                          <div className="flex gap-2">
                            <Badge className={getPriorityColor(task.priority)}>
                              {task.priority.toUpperCase()}
                            </Badge>
                            <Badge variant="outline">
                              {task.estimated_effort}
                            </Badge>
                          </div>
                        </div>
                        
                        <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          <strong>Component:</strong> {task.component}
                        </div>
                        
                        {task.dependencies.length > 0 && (
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            <strong>Dependencies:</strong> {task.dependencies.join(', ')}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Action Buttons */}
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={handleReset}>
                  Create More Tasks
                </Button>
                <Button onClick={handleClose}>
                  Done
                </Button>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}