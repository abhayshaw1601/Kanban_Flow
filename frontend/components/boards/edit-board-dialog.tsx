'use client';

import { useState } from 'react';
import { useUpdateBoard, useDeleteBoard } from '@/hooks/use-boards';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Loader2, Save, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';
import type { BoardDetail } from '@/hooks/use-board';

interface EditBoardDialogProps {
  board: BoardDetail;
  isOpen: boolean;
  onClose: () => void;
}

export function EditBoardDialog({ board, isOpen, onClose }: EditBoardDialogProps) {
  const [name, setName] = useState(board.name);
  const [description, setDescription] = useState(board.description || '');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  
  const updateBoardMutation = useUpdateBoard();
  const deleteBoardMutation = useDeleteBoard();
  const router = useRouter();

  const handleSave = async () => {
    if (!name.trim()) {
      toast.error('Board name is required');
      return;
    }

    try {
      await updateBoardMutation.mutateAsync({
        boardId: board.id,
        data: {
          name: name.trim(),
          description: description.trim() || undefined,
        },
      });
      toast.success('Board updated successfully');
      onClose();
    } catch (error) {
      toast.error('Failed to update board');
    }
  };

  const handleDelete = async () => {
    try {
      await deleteBoardMutation.mutateAsync(board.id);
      toast.success('Board deleted successfully');
      router.push('/dashboard/boards');
    } catch (error) {
      toast.error('Failed to delete board');
    }
  };

  const handleClose = () => {
    setName(board.name);
    setDescription(board.description || '');
    setShowDeleteConfirm(false);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Edit Board</DialogTitle>
          <DialogDescription>
            Update board information or delete the board.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Board Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter board name"
              disabled={updateBoardMutation.isPending}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter board description (optional)"
              rows={3}
              disabled={updateBoardMutation.isPending}
            />
          </div>

          {!showDeleteConfirm ? (
            <div className="flex gap-2 pt-4">
              <Button variant="outline" onClick={handleClose} className="flex-1">
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={updateBoardMutation.isPending || !name.trim()}
                className="flex-1"
              >
                {updateBoardMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <Save className="h-4 w-4 mr-2" />
                )}
                Save Changes
              </Button>
            </div>
          ) : null}

          {/* Delete Section */}
          <div className="border-t pt-4">
            {!showDeleteConfirm ? (
              <Button
                variant="destructive"
                onClick={() => setShowDeleteConfirm(true)}
                className="w-full"
                disabled={updateBoardMutation.isPending}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete Board
              </Button>
            ) : (
              <div className="space-y-3">
                <div className="text-sm text-muted-foreground">
                  <p className="font-medium text-destructive">Warning: This action cannot be undone.</p>
                  <p>This will permanently delete the board, all columns, tasks, and remove all members.</p>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowDeleteConfirm(false)}
                    className="flex-1"
                    disabled={deleteBoardMutation.isPending}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={handleDelete}
                    disabled={deleteBoardMutation.isPending}
                    className="flex-1"
                  >
                    {deleteBoardMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <Trash2 className="h-4 w-4 mr-2" />
                    )}
                    Delete Forever
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}