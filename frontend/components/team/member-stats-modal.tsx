'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { CheckCircle, Clock, AlertCircle, TrendingUp, BarChart3 } from 'lucide-react';
import { useMemberStatistics } from '@/hooks/use-analytics';

interface MemberStatsModalProps {
  userId: number | null;
  userName: string;
  isOpen: boolean;
  onClose: () => void;
}

export function MemberStatsModal({ userId, userName, isOpen, onClose }: MemberStatsModalProps) {
  const { data: stats, isLoading, error } = useMemberStatistics(userId);

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getPerformanceIcon = (color: string) => {
    switch (color) {
      case 'green':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'yellow':
        return <Clock className="w-5 h-5 text-yellow-600" />;
      case 'red':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      default:
        return <BarChart3 className="w-5 h-5 text-gray-600" />;
    }
  };

  const getPerformanceBadge = (color: string, status: string) => {
    const badgeClasses = {
      green: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
      yellow: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
      red: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
    };

    const statusLabels = {
      excellent: 'Excellent',
      good: 'Good',
      needs_improvement: 'Needs Improvement'
    };

    return (
      <Badge className={badgeClasses[color as keyof typeof badgeClasses]}>
        {statusLabels[status as keyof typeof statusLabels]}
      </Badge>
    );
  };

  if (isLoading) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Member Statistics</DialogTitle>
          </DialogHeader>
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400">Loading statistics...</p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  if (error || !stats) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Member Statistics</DialogTitle>
          </DialogHeader>
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-400">Failed to load statistics</p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <Avatar className="w-10 h-10">
              <AvatarFallback className="bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                {getInitials(userName)}
              </AvatarFallback>
            </Avatar>
            <div>
              <span>{stats.user_name} - Performance Statistics</span>
              <p className="text-sm font-normal text-gray-600 dark:text-gray-400">
                {stats.user_email}
              </p>
            </div>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* Performance Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Performance Overview
                </div>
                {getPerformanceBadge(stats.performance.color, stats.performance.status)}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4 mb-4">
                {getPerformanceIcon(stats.performance.color)}
                <div>
                  <p className="font-semibold text-lg">
                    {stats.statistics.completion_percentage}% Completion Rate
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {stats.performance.description}
                  </p>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mb-4">
                <div
                  className={`h-3 rounded-full transition-all duration-300 ${
                    stats.performance.color === 'green'
                      ? 'bg-green-500'
                      : stats.performance.color === 'yellow'
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.min(stats.statistics.completion_percentage, 100)}%` }}
                ></div>
              </div>
            </CardContent>
          </Card>

          {/* Task Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-2xl font-bold text-blue-600 mb-2">
                  {stats.statistics.total_tasks}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Tasks</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-2xl font-bold text-gray-600 mb-2">
                  {stats.statistics.todo_tasks}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">To Do</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-2xl font-bold text-yellow-600 mb-2">
                  {stats.statistics.in_progress_tasks}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">In Progress</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-2xl font-bold text-green-600 mb-2">
                  {stats.statistics.done_tasks}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Completed</p>
              </CardContent>
            </Card>
          </div>

          {/* Board Breakdown */}
          {stats.board_breakdown.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Board Performance Breakdown
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {stats.board_breakdown.map((board) => (
                    <div key={board.board_id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold">{board.board_name}</h4>
                        <Badge variant="outline">
                          {board.completion_percentage}% Complete
                        </Badge>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-2">
                        <span>{board.completed_tasks} of {board.total_tasks} tasks completed</span>
                      </div>

                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-300 ${
                            board.completion_percentage > 50
                              ? 'bg-green-500'
                              : board.completion_percentage >= 30
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                          }`}
                          style={{ width: `${Math.min(board.completion_percentage, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {stats.statistics.total_tasks === 0 && (
            <Card>
              <CardContent className="p-12 text-center">
                <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  No Tasks Assigned
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  This member has no tasks assigned yet. Assign some tasks to see performance statistics.
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}