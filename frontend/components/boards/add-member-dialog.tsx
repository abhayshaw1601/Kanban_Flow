'use client';

import { useState } from 'react';
import { useUsers } from '@/hooks/use-users';
import { useAddBoardMember, useBoardMembers } from '@/hooks/use-board-members';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Loader2, UserPlus } from 'lucide-react';
import { toast } from 'sonner';

interface AddMemberDialogProps {
  boardId: number;
  isOpen: boolean;
  onClose: () => void;
}

export function AddMemberDialog({ boardId, isOpen, onClose }: AddMemberDialogProps) {
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null);
  
  const { data: users, isLoading: usersLoading } = useUsers();
  const { data: boardMembers } = useBoardMembers(boardId);
  const addMemberMutation = useAddBoardMember();

  // Get users who are not already board members
  const availableUsers = users?.filter(user => 
    !boardMembers?.some(member => member.id === user.id)
  ) || [];

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleAddMember = async () => {
    if (!selectedUserId) return;

    try {
      await addMemberMutation.mutateAsync({
        userId: selectedUserId,
        boardId,
      });
      toast.success('Member added to board successfully');
      setSelectedUserId(null);
      onClose();
    } catch (error) {
      toast.error('Failed to add member to board');
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Add Member to Board</DialogTitle>
          <DialogDescription>
            Select an employee to add to this board.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {usersLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin" />
            </div>
          ) : availableUsers.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              All users are already members of this board.
            </div>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {availableUsers.map((user) => (
                <div
                  key={user.id}
                  className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedUserId === user.id
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:bg-muted/50'
                  }`}
                  onClick={() => setSelectedUserId(user.id)}
                >
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className="text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                      {getInitials(user.name)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <div className="font-medium">{user.name}</div>
                    <div className="text-sm text-muted-foreground">{user.email}</div>
                  </div>
                  <Badge variant={user.role === 'admin' ? 'default' : 'secondary'}>
                    {user.role}
                  </Badge>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-2 pt-4">
            <Button variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
            <Button
              onClick={handleAddMember}
              disabled={!selectedUserId || addMemberMutation.isPending}
              className="flex-1"
            >
              {addMemberMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <UserPlus className="h-4 w-4 mr-2" />
              )}
              Add Member
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}