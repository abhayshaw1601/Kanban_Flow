'use client';

import { DragDropContext, Droppable, DropResult } from '@hello-pangea/dnd';
import { Column } from './column';
import { useMoveTask } from '@/hooks/use-tasks';
import { useCurrentUser } from '@/hooks/use-current-user';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';
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
    <div className="relative min-h-screen bg-ai-gradient">
      {/* Animated background grid */}
      <div className="absolute inset-0 opacity-20">
        <div className="absolute inset-0" style={{
          backgroundImage: `
            linear-gradient(rgba(139, 92, 246, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(139, 92, 246, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '20px 20px'
        }} />
      </div>

      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="relative z-10 h-full overflow-x-auto">
          <div className="flex gap-6 p-6 min-w-max" style={{ minWidth: 'calc(100vw - 280px)' }}>
            {sortedColumns.map((column, index) => (
              <div
                key={column.id}
                className={cn(
                  "column-enter opacity-0 animate-fade-in flex-shrink-0",
                  // Stagger animation delay
                  index === 0 && "animation-delay-0",
                  index === 1 && "animation-delay-150",
                  index === 2 && "animation-delay-300",
                  index === 3 && "animation-delay-450"
                )}
                style={{
                  animationDelay: `${index * 150}ms`,
                  animationFillMode: 'forwards'
                }}
              >
                <Column
                  column={column}
                  isAdmin={isAdmin}
                  boardId={board.id}
                  allColumns={sortedColumns}
                />
              </div>
            ))}
            
            {/* Spacer to ensure full width utilization */}
            <div className="flex-1 min-w-[100px]" />
          </div>
        </div>
      </DragDropContext>
    </div>
  );
}