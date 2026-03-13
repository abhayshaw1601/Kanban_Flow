'use client';

import { useState } from 'react';
import { useBoard } from '@/hooks/use-board';
import { useBoardMembers, useRemoveBoardMember } from '@/hooks/use-board-members';
import { useCurrentUser } from '@/hooks/use-current-user';
import { KanbanBoard } from '@/components/kanban/kanban-board';
import { AddMemberDialog } from '@/components/boards/add-member-dialog';
import { EditBoardDialog } from '@/components/boards/edit-board-dialog';
import { DiagramTaskCreator } from '@/components/boards/diagram-task-creator';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Calendar, Users, UserPlus, UserMinus, Settings, Trash2 } from 'lucide-react';
import Link from 'next/link';
import { format } from 'date-fns';
import { toast } from 'sonner';

interface BoardPageProps {
  params: {
    boardId: string;
  };
}

function BoardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Skeleton className="h-10 w-10" />
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-96" />
        </div>
      </div>
      <div className="flex gap-6 overflow-x-auto pb-4">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="flex-shrink-0 w-80">
            <Skeleton className="h-6 w-24 mb-4" />
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, j) => (
                <Skeleton key={j} className="h-32 w-full" />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function BoardPage({ params }: BoardPageProps) {
  const [isAddMemberOpen, setIsAddMemberOpen] = useState(false);
  const [isEditBoardOpen, setIsEditBoardOpen] = useState(false);
  const { data: board, isLoading, error } = useBoard(params.boardId);
  const { data: boardMembers, isLoading: membersLoading } = useBoardMembers(parseInt(params.boardId));
  const { data: currentUser } = useCurrentUser();
  const removeMemberMutation = useRemoveBoardMember();

  const isAdmin = currentUser?.role === 'admin';

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleRemoveMember = async (userId: number, userName: string) => {
    if (userId === currentUser?.id) {
      toast.error("You cannot remove yourself from the board");
      return;
    }

    try {
      await removeMemberMutation.mutateAsync({
        userId,
        boardId: parseInt(params.boardId),
      });
      toast.success(`${userName} removed from board`);
    } catch (error) {
      toast.error('Failed to remove member from board');
    }
  };

  if (isLoading) {
    return <BoardSkeleton />;
  }

  if (error || !board) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="rounded-full bg-destructive/10 p-6 mb-4">
          <Calendar className="h-12 w-12 text-destructive" />
        </div>
        <h3 className="text-lg font-semibold mb-2">Board not found</h3>
        <p className="text-muted-foreground mb-6">
          The board you&apos;re looking for doesn&apos;t exist or you don&apos;t have access to it.
        </p>
        <Button asChild>
          <Link href="/dashboard/boards">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Boards
          </Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/dashboard/boards">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">{board.name}</h1>
          {board.description && (
            <p className="text-muted-foreground mt-1">{board.description}</p>
          )}
          <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
            <div className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              <span>Created {format(new Date(board.created_at), 'MMM d, yyyy')}</span>
            </div>
          </div>
        </div>
        {isAdmin && (
          <div className="flex gap-2">
            <DiagramTaskCreator 
              boardId={parseInt(params.boardId)}
              boardName={board.name}
              isAdmin={isAdmin}
            />
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsEditBoardOpen(true)}
              className="flex items-center gap-2"
            >
              <Settings className="h-4 w-4" />
              Edit Board
            </Button>
          </div>
        )}
      </div>

      {/* Board Members Section */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            <h2 className="text-lg font-semibold">Board Members</h2>
            {!membersLoading && boardMembers && (
              <Badge variant="secondary">{boardMembers.length}</Badge>
            )}
          </div>
          {isAdmin && (
            <Button
              onClick={() => setIsAddMemberOpen(true)}
              size="sm"
              className="flex items-center gap-2"
            >
              <UserPlus className="h-4 w-4" />
              Add Member
            </Button>
          )}
        </div>

        {membersLoading ? (
          <div className="flex gap-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex items-center gap-2">
                <Skeleton className="h-8 w-8 rounded-full" />
                <Skeleton className="h-4 w-20" />
              </div>
            ))}
          </div>
        ) : boardMembers && boardMembers.length > 0 ? (
          <div className="flex flex-wrap gap-3">
            {boardMembers.map((member) => (
              <div
                key={member.id}
                className="flex items-center gap-2 bg-gray-50 dark:bg-gray-700 rounded-lg px-3 py-2 group"
              >
                <Avatar className="w-8 h-8">
                  <AvatarFallback className="text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                    {getInitials(member.name)}
                  </AvatarFallback>
                </Avatar>
                <div className="flex flex-col">
                  <span className="text-sm font-medium">{member.name}</span>
                  <span className="text-xs text-muted-foreground">{member.email}</span>
                </div>
                <Badge variant={member.role === 'admin' ? 'default' : 'secondary'} className="text-xs">
                  {member.role}
                </Badge>
                {isAdmin && member.id !== currentUser?.id && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveMember(member.id, member.name)}
                    disabled={removeMemberMutation.isPending}
                    className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                    title={`Remove ${member.name} from board`}
                  >
                    <UserMinus className="h-3 w-3" />
                  </Button>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <Users className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No members assigned to this board yet.</p>
            {isAdmin && (
              <Button
                onClick={() => setIsAddMemberOpen(true)}
                variant="outline"
                size="sm"
                className="mt-2"
              >
                Add First Member
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Kanban Board */}
      <KanbanBoard board={board} />

      {/* Add Member Dialog */}
      <AddMemberDialog
        boardId={parseInt(params.boardId)}
        isOpen={isAddMemberOpen}
        onClose={() => setIsAddMemberOpen(false)}
      />

      {/* Edit Board Dialog */}
      {board && (
        <EditBoardDialog
          board={board}
          isOpen={isEditBoardOpen}
          onClose={() => setIsEditBoardOpen(false)}
        />
      )}
    </div>
  );
}