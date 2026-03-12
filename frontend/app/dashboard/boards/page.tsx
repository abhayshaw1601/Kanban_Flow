'use client';

import { useBoards } from '@/hooks/use-boards';
import { useCurrentUser } from '@/hooks/use-current-user';
import { BoardCard } from '@/components/boards/board-card';
import { CreateBoardDialog } from '@/components/boards/create-board-dialog';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { LayoutDashboard, Plus, TrendingUp } from 'lucide-react';

function BoardSkeleton() {
  return (
    <Card className="h-[200px] shadow-soft border-0">
      <div className="p-6">
        <Skeleton className="h-6 w-3/4 mb-2" />
        <Skeleton className="h-4 w-full mb-1" />
        <Skeleton className="h-4 w-2/3 mb-4" />
        <div className="flex gap-2 mb-4">
          <Skeleton className="h-6 w-16" />
          <Skeleton className="h-6 w-20" />
        </div>
        <Skeleton className="h-4 w-1/2" />
      </div>
    </Card>
  );
}

function EmptyState({ isAdmin }: { isAdmin: boolean }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="rounded-full bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900/20 dark:to-purple-900/20 p-8 mb-6">
        <LayoutDashboard className="h-16 w-16 text-primary" />
      </div>
      <h3 className="text-2xl font-semibold mb-3">No boards yet</h3>
      <p className="text-muted-foreground mb-8 max-w-md text-lg">
        {isAdmin
          ? "Get started by creating your first board to organize your team's work and boost productivity."
          : "No boards have been shared with you yet. Contact your admin to get access to boards."}
      </p>
      {isAdmin && <CreateBoardDialog />}
    </div>
  );
}

function StatsCard({ title, value, icon: Icon, trend }: { 
  title: string; 
  value: string | number; 
  icon: any; 
  trend?: string;
}) {
  return (
    <Card className="shadow-soft border-0">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {trend && (
              <p className="text-xs text-green-600 dark:text-green-400 flex items-center mt-1">
                <TrendingUp className="h-3 w-3 mr-1" />
                {trend}
              </p>
            )}
          </div>
          <div className="rounded-full bg-primary/10 p-3">
            <Icon className="h-6 w-6 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function BoardsPage() {
  const { data: user } = useCurrentUser();
  const { data: boards, isLoading, error } = useBoards();

  const isAdmin = user?.role === 'admin';

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-32 mb-2" />
            <Skeleton className="h-5 w-64" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>
        
        {/* Stats skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="shadow-soft border-0">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <Skeleton className="h-4 w-20 mb-2" />
                    <Skeleton className="h-8 w-12" />
                  </div>
                  <Skeleton className="h-12 w-12 rounded-full" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <BoardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="rounded-full bg-destructive/10 p-8 mb-6">
          <LayoutDashboard className="h-16 w-16 text-destructive" />
        </div>
        <h3 className="text-2xl font-semibold mb-3">Failed to load boards</h3>
        <p className="text-muted-foreground text-lg">
          There was an error loading your boards. Please try again.
        </p>
      </div>
    );
  }

  const totalBoards = boards?.length || 0;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            Boards
          </h1>
          <p className="text-muted-foreground text-lg mt-2">
            Manage your project boards and track progress
          </p>
        </div>
        {isAdmin && boards && boards.length > 0 && <CreateBoardDialog />}
      </div>

      {/* Stats */}
      {boards && boards.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatsCard
            title="Total Boards"
            value={totalBoards}
            icon={LayoutDashboard}
          />
          <StatsCard
            title="Team Members"
            value="8"
            icon={Plus}
          />
          <StatsCard
            title="Recent Activity"
            value="12"
            icon={TrendingUp}
            trend="+3 this week"
          />
        </div>
      )}

      {/* Content */}
      {!boards || boards.length === 0 ? (
        <EmptyState isAdmin={isAdmin} />
      ) : (
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold">Your Boards</h2>
            <Badge variant="secondary" className="text-sm">
              {totalBoards} {totalBoards === 1 ? 'board' : 'boards'}
            </Badge>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {boards.map((board) => (
              <BoardCard key={board.id} board={board} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}