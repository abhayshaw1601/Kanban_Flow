'use client';

import { useBoards } from '@/hooks/use-boards';
import { useCurrentUser } from '@/hooks/use-current-user';
import { BoardCard } from '@/components/boards/board-card';
import { CreateBoardDialog } from '@/components/boards/create-board-dialog';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { LayoutDashboard, Plus } from 'lucide-react';

function BoardSkeleton() {
  return (
    <Card className="h-[180px]">
      <div className="p-6">
        <Skeleton className="h-6 w-3/4 mb-2" />
        <Skeleton className="h-4 w-full mb-1" />
        <Skeleton className="h-4 w-2/3 mb-4" />
        <Skeleton className="h-4 w-1/2" />
      </div>
    </Card>
  );
}

function EmptyState({ isAdmin }: { isAdmin: boolean }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="rounded-full bg-muted p-6 mb-4">
        <LayoutDashboard className="h-12 w-12 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-semibold mb-2">No boards yet</h3>
      <p className="text-muted-foreground mb-6 max-w-sm">
        {isAdmin
          ? "Get started by creating your first board to organize your team's work."
          : "No boards have been shared with you yet. Contact your admin to get access to boards."}
      </p>
      {isAdmin && <CreateBoardDialog />}
    </div>
  );
}

export default function BoardsPage() {
  const { data: user } = useCurrentUser();
  const { data: boards, isLoading, error } = useBoards();

  const isAdmin = user?.role === 'admin';

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Boards</h1>
            <p className="text-muted-foreground">
              Manage your project boards and track progress
            </p>
          </div>
          <Skeleton className="h-10 w-32" />
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
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="rounded-full bg-destructive/10 p-6 mb-4">
          <LayoutDashboard className="h-12 w-12 text-destructive" />
        </div>
        <h3 className="text-lg font-semibold mb-2">Failed to load boards</h3>
        <p className="text-muted-foreground">
          There was an error loading your boards. Please try again.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Boards</h1>
          <p className="text-muted-foreground">
            Manage your project boards and track progress
          </p>
        </div>
        {isAdmin && boards && boards.length > 0 && <CreateBoardDialog />}
      </div>

      {/* Content */}
      {!boards || boards.length === 0 ? (
        <EmptyState isAdmin={isAdmin} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {boards.map((board) => (
            <BoardCard key={board.id} board={board} />
          ))}
        </div>
      )}
    </div>
  );
}