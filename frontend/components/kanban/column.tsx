'use client';

import { useState } from 'react';
import { Droppable } from '@hello-pangea/dnd';
import { TaskCard } from './task-card';
import { TaskForm } from './task-form';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import type { Column as ColumnType } from '@/hooks/use-board';

interface ColumnProps {
  column: ColumnType;
  isAdmin: boolean;
  boardId: number;
  allColumns: ColumnType[];
}

export function Column({ column, isAdmin, boardId, allColumns }: ColumnProps) {
  const [isTaskFormOpen, setIsTaskFormOpen] = useState(false);

  // Sort tasks by order
  const sortedTasks = [...column.tasks].sort((a, b) => a.order - b.order);

  return (
    <>
      <div className="flex flex-col w-80 bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
        {/* Column Header */}
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100">
            {column.name}
          </h3>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            {sortedTasks.length}
          </span>
        </div>

        {/* Droppable Area */}
        <Droppable droppableId={column.id.toString()}>
          {(provided, snapshot) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className={`flex-1 min-h-[200px] space-y-3 ${
                snapshot.isDraggingOver
                  ? 'bg-blue-50 dark:bg-blue-900/20 border-2 border-dashed border-blue-300 dark:border-blue-600'
                  : ''
              } rounded-md p-2 transition-colors`}
            >
              {sortedTasks.length === 0 ? (
                <div className="flex items-center justify-center h-32 text-gray-400 dark:text-gray-500 text-sm">
                  No tasks yet
                </div>
              ) : (
                sortedTasks.map((task, index) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    index={index}
                    boardId={boardId}
                    columns={allColumns}
                  />
                ))
              )}
              {provided.placeholder}
            </div>
          )}
        </Droppable>

        {/* Add Task Button (Admin Only) */}
        {isAdmin && (
          <div className="mt-4">
            <Button
              variant="ghost"
              size="sm"
              className="w-full justify-start text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
              onClick={() => setIsTaskFormOpen(true)}
            >
              <Plus className="w-4 h-4 mr-2" />
              Add task
            </Button>
          </div>
        )}
      </div>

      {/* Task Form Modal */}
      <TaskForm
        boardId={boardId}
        columns={allColumns}
        defaultColumnId={column.id}
        isOpen={isTaskFormOpen}
        onClose={() => setIsTaskFormOpen(false)}
      />
    </>
  );
}