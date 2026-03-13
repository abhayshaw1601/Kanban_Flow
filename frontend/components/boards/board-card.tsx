'use client';

import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calendar, Users, CheckCircle, Clock, Brain, Zap, ArrowRight } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
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

  // Simulate AI enhancement status (in real app, this would come from board data)
  const isAIEnhanced = Math.random() > 0.5;

  return (
    <Link href={`/dashboard/boards/${board.id}`}>
      <Card className={cn(
        "h-full cursor-pointer group relative overflow-hidden",
        "card-glow transition-all duration-300 ease-in-out",
        "hover:scale-105 hover:-translate-y-2"
      )}>
        {/* AI Enhancement Indicator */}
        {isAIEnhanced && (
          <div className="absolute top-4 right-4 z-10">
            <div className="flex items-center gap-1 px-2 py-1 bg-ai-violet-500/20 border border-ai-violet-500/30 rounded-full backdrop-blur-sm">
              <Brain className="h-3 w-3 text-ai-violet-400" />
              <span className="text-xs text-ai-violet-400 font-medium">AI</span>
            </div>
          </div>
        )}

        {/* Gradient overlay on hover */}
        <div className="absolute inset-0 bg-gradient-to-br from-ai-violet-500/5 to-electric-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

        <CardHeader className="pb-4 relative z-10">
          <div className="flex items-start justify-between">
            <div className="flex-1 pr-8">
              <CardTitle className="line-clamp-1 group-hover:text-ai-violet-300 transition-colors duration-300 text-lg font-semibold tracking-tight">
                {board.name}
              </CardTitle>
              <CardDescription className="line-clamp-2 min-h-[2.5rem] mt-2 text-muted-foreground leading-relaxed">
                {board.description || 'No description provided'}
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="pt-0 relative z-10">
          <div className="space-y-4">
            {/* Stats */}
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/10">
                <CheckCircle className="h-4 w-4 text-green-400" />
                <span className="text-muted-foreground font-medium">0 tasks</span>
              </div>
              <div className="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/10">
                <Users className="h-4 w-4 text-blue-400" />
                <span className="text-muted-foreground font-medium">0 members</span>
              </div>
            </div>
            
            {/* Creation date and AI status */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="h-4 w-4" />
                <span>Created {formatCreatedDate(board.created_at)}</span>
              </div>
              
              {isAIEnhanced && (
                <div className="flex items-center gap-1 text-xs text-ai-violet-400">
                  <Zap className="h-3 w-3 animate-pulse" />
                  <span className="font-medium">AI Enhanced</span>
                </div>
              )}
            </div>

            {/* Hover action indicator */}
            <div className="flex items-center justify-between pt-2 border-t border-white/10">
              <span className="text-xs text-muted-foreground">Click to open board</span>
              <ArrowRight className="h-4 w-4 text-muted-foreground group-hover:text-ai-violet-400 group-hover:translate-x-1 transition-all duration-300" />
            </div>
          </div>
        </CardContent>

        {/* Animated border on hover */}
        <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none">
          <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-ai-violet-500/20 via-electric-blue-500/20 to-ai-violet-500/20 p-[1px]">
            <div className="h-full w-full rounded-xl bg-card" />
          </div>
        </div>
      </Card>
    </Link>
  );
}