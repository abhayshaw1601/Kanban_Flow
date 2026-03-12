'use client';

import { DragDropContext, Droppable, DropResult } from '@hello-pangea/dnd';
import { Column } from './column';
import { useMoveTask } from '@/hooks/use-tasks';
import { useCurrentUser } from '@/hooks/use-current-user';
import { toast } from 'sonner';
import type { BoardDetail } from '@/hooks/use-board';

interface KanbanBoardProps {
  board: BoardDetail;
}

export function KanbanBoard({ board }: KanbanBoardProps) {
  const { data: user } = useCurrentUser();
  const moveTask = useMoveTask();

  const isAdmin = user?.role === 'admin';

  const handleDragEnd = async (result: DropResult) => {
    const { destination, source, draggableId } = result;

    // If dropped outside a droppable area
    if (!destination) {
      return;
    }

    // If dropped in the same position
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const taskId = parseInt(draggableId);
    const sourceColumnId = parseInt(source.droppableId);
    const destinationColumnId = parseInt(destination.droppableId);

    try {
      await moveTask.mutateAsync({
        taskId,
        columnId: destinationColumnId,
        order: destination.index,
      });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to move task';
      toast.error(errorMessage);
    }
  };

  // Sort columns by order
  const sortedColumns = [...board.columns].sort((a, b) => a.order - b.order);

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <div className="flex gap-6 overflow-x-auto pb-4">
        {sortedColumns.map((column) => (
          <Column
            key={column.id}
            column={column}
            isAdmin={isAdmin}
            boardId={board.id}
            allColumns={sortedColumns}
          />
        ))}
      </div>
    </DragDropContext>
  );
}