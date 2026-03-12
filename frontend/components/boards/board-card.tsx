'use client';

import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calendar, Users, CheckCircle, Clock } from 'lucide-react';
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
      <Card className="h-full transition-all hover:shadow-lg hover:scale-[1.02] cursor-pointer shadow-soft border-0 group">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="line-clamp-1 group-hover:text-primary transition-colors">
                {board.name}
              </CardTitle>
              <CardDescription className="line-clamp-2 min-h-[2.5rem] mt-2">
                {board.description || 'No description provided'}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-3">
            {/* Stats */}
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <CheckCircle className="h-4 w-4" />
                <span>0 tasks</span>
              </div>
              <div className="flex items-center gap-1">
                <Users className="h-4 w-4" />
                <span>0 members</span>
              </div>
            </div>
            
            {/* Creation date */}
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              <span>Created {formatCreatedDate(board.created_at)}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}