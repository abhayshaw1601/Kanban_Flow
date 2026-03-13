'use client';

import { useState, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Upload, FileImage, Brain, Download, RefreshCw, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api';

interface DiagramAnalysis {
  diagram_type: string;
  title: string;
  description: string;
  components: Array<{
    id: string;
    name: string;
    type: string;
    description: string;
    technology?: string;
    layer?: string;
  }>;
  connections: Array<{
    from: string;
    to: string;
    type: string;
    description: string;
    direction: string;
    protocol?: string;
  }>;
  data_flows: Array<{
    name: string;
    path: string[];
    data_type: string;
    description: string;
  }>;
  layers: Array<{
    name: string;
    components: string[];
    description: string;
  }>;
  external_dependencies: Array<{
    name: string;
    type: string;
    description: string;
  }>;
  project_breakdown: {
    suggested_tasks: Array<{
      title: string;
      description: string;
      component: string;
      priority: string;
      estimated_effort: string;
      dependencies: string[];
    }>;
    development_phases: Array<{
      phase: string;
      tasks: string[];
      description: string;
    }>;
  };
}

export function DiagramAnalyzer() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<DiagramAnalysis | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    setAnalysis(null);

    // Create preview URL
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      toast.error('Please select a diagram file first');
      return;
    }

    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await apiClient.post('/ai/analyze-diagram', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setAnalysis(response.data.analysis);
        toast.success('Diagram analyzed successfully!');
      } else {
        throw new Error('Analysis failed');
      }
    } catch (error: any) {
      console.error('Diagram analysis failed:', error);
      
      if (error.response?.status === 403) {
        toast.error('Only administrators can analyze diagrams');
      } else if (error.response?.status === 400) {
        toast.error(error.response.data.detail || 'Invalid file format');
      } else {
        toast.error('Failed to analyze diagram. Please try again.');
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDownloadJSON = () => {
    if (!analysis) return;

    const dataStr = JSON.stringify(analysis, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `diagram-analysis-${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
    toast.success('Analysis downloaded as JSON');
  };

  const handleReset = () => {
    setSelectedFile(null);
    setAnalysis(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      service: 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400',
      database: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      ui: 'bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400',
      api: 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400',
      external: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
      user: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
    };
    return colors[type] || 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-400';
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
    <div className="space-y-6">
      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5" />
            AI Diagram Analyzer
          </CardTitle>
          <CardDescription>
            Upload architecture or flow diagrams and convert them to structured JSON format using Gemini AI
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
                      onClick={handleAnalyze}
                      disabled={isAnalyzing}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      {isAnalyzing ? (
                        <>
                          <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Brain className="w-4 h-4 mr-2" />
                          Analyze with AI
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

      {/* Analysis Results */}
      {analysis && (
        <div className="space-y-6">
          {/* Overview */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  Analysis Results
                </CardTitle>
                <Button onClick={handleDownloadJSON} variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Download JSON
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                    {analysis.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mt-1">
                    {analysis.description}
                  </p>
                  <Badge className="mt-2">
                    {analysis.diagram_type.toUpperCase()}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Components */}
          {analysis.components && analysis.components.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Components ({analysis.components.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  {analysis.components.map((component, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-gray-900 dark:text-gray-100">
                          {component.name}
                        </h4>
                        <Badge className={getTypeColor(component.type)}>
                          {component.type}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                        {component.description}
                      </p>
                      {component.technology && (
                        <div className="text-xs text-blue-600 dark:text-blue-400">
                          Tech: {component.technology}
                        </div>
                      )}
                      {component.layer && (
                        <div className="text-xs text-purple-600 dark:text-purple-400">
                          Layer: {component.layer}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Suggested Tasks */}
          {analysis.project_breakdown?.suggested_tasks && analysis.project_breakdown.suggested_tasks.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Suggested Tasks ({analysis.project_breakdown.suggested_tasks.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysis.project_breakdown.suggested_tasks.map((task, index) => (
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
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                        {task.description}
                      </p>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        <span>Component: {task.component}</span>
                        {task.dependencies.length > 0 && (
                          <span>Dependencies: {task.dependencies.join(', ')}</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Development Phases */}
          {analysis.project_breakdown?.development_phases && analysis.project_breakdown.development_phases.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Development Phases</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analysis.project_breakdown.development_phases.map((phase, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-2">
                        {phase.phase}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                        {phase.description}
                      </p>
                      <div className="text-xs text-gray-500">
                        Tasks: {phase.tasks.join(', ')}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Error Display */}
          {analysis.error && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-red-600">
                  <AlertCircle className="w-5 h-5" />
                  Analysis Error
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-red-600">{analysis.error}</p>
                  {analysis.raw_response && (
                    <div>
                      <h4 className="font-medium mb-2">Raw AI Response:</h4>
                      <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded text-sm overflow-auto">
                        {analysis.raw_response}
                      </pre>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}