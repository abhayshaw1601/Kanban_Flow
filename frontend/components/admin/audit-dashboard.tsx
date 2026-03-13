'use client';

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, CheckCircle, Clock, Search, RefreshCw, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { useRunAudit, usePendingProjects, useClearBlockers } from '@/hooks/use-analytics';

export function AuditDashboard() {
  const [showResults, setShowResults] = useState(false);
  const runAudit = useRunAudit();
  const { data: pendingProjects, refetch: refetchPending } = usePendingProjects();
  const clearBlockers = useClearBlockers();

  const handleRunAudit = async () => {
    try {
      const result = await runAudit.mutateAsync();
      toast.success(result.message);
      setShowResults(true);
      refetchPending();
    } catch (error: any) {
      toast.error('Failed to run audit: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleClearBlockers = async () => {
    if (!confirm('Are you sure you want to clear all blocker flags? This will remove blocker status from all tasks.')) {
      return;
    }

    try {
      const result = await clearBlockers.mutateAsync();
      toast.success(result.message);
      refetchPending();
    } catch (error: any) {
      toast.error('Failed to clear blockers: ' + (error.response?.data?.detail || error.message));
    }
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
      {/* Audit Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="w-5 h-5" />
            Project Audit System
          </CardTitle>
          <CardDescription>
            Check for overdue tasks and automatically mark them as blockers for employees
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <Button
              onClick={handleRunAudit}
              disabled={runAudit.isPending}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {runAudit.isPending ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Running Audit...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4 mr-2" />
                  Run Audit
                </>
              )}
            </Button>
            
            <Button
              variant="outline"
              onClick={handleClearBlockers}
              disabled={clearBlockers.isPending}
            >
              {clearBlockers.isPending ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Clearing...
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4 mr-2" />
                  Clear All Blockers
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
      {/* Pending Projects Overview */}
      {pendingProjects && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Pending Projects Overview</span>
              <Badge variant="outline">
                {pendingProjects.total_pending} Total Pending
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {pendingProjects.pending_projects.length === 0 ? (
                <div className="text-center py-8">
                  <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                    All Projects Complete!
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    No pending projects found. Great work team!
                  </p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {pendingProjects.pending_projects.map((project) => (
                    <div
                      key={project.task_id}
                      className={`border rounded-lg p-4 ${
                        project.is_blocker 
                          ? 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/10' 
                          : project.is_overdue
                          ? 'border-orange-200 bg-orange-50 dark:border-orange-800 dark:bg-orange-900/10'
                          : 'border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className="font-semibold text-gray-900 dark:text-gray-100">
                              {project.title}
                            </h4>
                            {project.is_blocker && (
                              <Badge className="bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400">
                                <AlertTriangle className="w-3 h-3 mr-1" />
                                BLOCKER
                              </Badge>
                            )}
                          </div>
                          
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 dark:text-gray-400">
                            <div>
                              <span className="font-medium">Board:</span> {project.board_name}
                            </div>
                            <div>
                              <span className="font-medium">Status:</span> {project.column_name}
                            </div>
                            <div>
                              <span className="font-medium">Assignee:</span> {project.assignee}
                            </div>
                            <div>
                              <span className="font-medium">Due:</span>{' '}
                              {project.due_date ? (
                                <span className={project.is_overdue ? 'text-red-600 font-medium' : ''}>
                                  {new Date(project.due_date).toLocaleDateString()}
                                  {project.days_until_due !== null && (
                                    <span className="ml-1">
                                      ({project.days_until_due < 0 
                                        ? `${Math.abs(project.days_until_due)} days overdue`
                                        : `${project.days_until_due} days left`
                                      })
                                    </span>
                                  )}
                                </span>
                              ) : (
                                'No due date'
                              )}
                            </div>
                          </div>
                          
                          {project.blocker_reason && (
                            <div className="mt-2 p-2 bg-red-100 dark:bg-red-900/20 rounded text-sm text-red-800 dark:text-red-400">
                              <strong>Blocker Reason:</strong> {project.blocker_reason}
                            </div>
                          )}
                        </div>
                        
                        <div className="flex items-center gap-2">
                          <Badge className={getPriorityColor(project.priority)}>
                            {project.priority.toUpperCase()}
                          </Badge>
                          {project.is_overdue && !project.is_blocker && (
                            <Clock className="w-4 h-4 text-orange-500" />
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Audit Results */}
      {showResults && runAudit.data && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              Audit Results
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {runAudit.data.results.statistics.total_tasks}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Total Tasks</div>
                </div>
                <div className="text-center p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <div className="text-2xl font-bold text-red-600">
                    {runAudit.data.results.statistics.overdue_tasks}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Overdue</div>
                </div>
                <div className="text-center p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600">
                    {runAudit.data.results.statistics.due_soon_tasks}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Due Soon</div>
                </div>
                <div className="text-center p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {runAudit.data.results.statistics.completed_tasks}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">Completed</div>
                </div>
              </div>
              
              {/* Reassignment Results */}
              {runAudit.data.results.reassigned_tasks && runAudit.data.results.reassigned_tasks.length > 0 && (
                <div className="mt-6">
                  <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3 flex items-center gap-2">
                    🔄 Task Reassignments
                    <Badge className="bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-400">
                      {runAudit.data.results.reassigned_tasks.length} Reassigned
                    </Badge>
                  </h4>
                  <div className="space-y-2">
                    {runAudit.data.results.reassigned_tasks.map((reassignment: any, index: number) => (
                      <div
                        key={index}
                        className="p-3 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="font-medium text-gray-900 dark:text-gray-100">
                              {reassignment.title}
                            </span>
                            <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              <span className="text-red-600">From: {reassignment.old_assignee}</span>
                              <span className="mx-2">→</span>
                              <span className="text-green-600">To: {reassignment.new_assignee}</span>
                            </div>
                          </div>
                          <Badge className="bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400">
                            {reassignment.days_overdue} days overdue
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="text-sm text-gray-600 dark:text-gray-400">
                Audit completed at: {new Date(runAudit.data.results.audit_completed_at).toLocaleString()}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}