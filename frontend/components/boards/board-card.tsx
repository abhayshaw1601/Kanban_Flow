'use client';

import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calendar } from 'lucide-react';
import { format } from 'date-fns';
import type { Board } from '@/hooks/use-boards';

interface BoardCardProps {
  board: Board;
}

export function BoardCard({ board }: BoardCardProps) {
  // Safely format the creation date
  const formatCreatedDate = (dateString: string) => {
    try {
      if (!dateString) return 'Unknown date';
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'Invalid date';
      return format(date, 'MMM d, yyyy');
    } catch (error) {
      return 'Invalid date';
    }
  };

  return (
    <Link href={`/dashboard/boards/${board.id}`}>
      <Card className="h-full transition-all hover:shadow-md hover:scale-[1.02] cursor-pointer">
        <CardHeader>
          <CardTitle className="line-clamp-1">{board.name}</CardTitle>
          <CardDescription className="line-clamp-2 min-h-[2.5rem]">
            {board.description || 'No description provided'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>Created {formatCreatedDate(board.created_at)}</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}