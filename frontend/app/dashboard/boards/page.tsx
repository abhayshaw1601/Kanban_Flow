'use client';

import { useBoards } from '@/hooks/use-boards';
import { useCurrentUser } from '@/hooks/use-current-user';
import { BoardCard } from '@/components/boards/board-card';
import { CreateBoardDialog } from '@/components/boards/create-board-dialog';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { LayoutDashboard, Plus, TrendingUp, Users, Brain, Zap } from 'lucide-react';

function BoardSkeleton() {
  return (
    <Card className="card-premium h-[200px]">
      <div className="p-6">
        <Skeleton className="h-6 w-3/4 mb-2 bg-white/10" />
        <Skeleton className="h-4 w-full mb-1 bg-white/10" />
        <Skeleton className="h-4 w-2/3 mb-4 bg-white/10" />
        <div className="flex gap-2 mb-4">
          <Skeleton className="h-6 w-16 bg-white/10" />
          <Skeleton className="h-6 w-20 bg-white/10" />
        </div>
        <Skeleton className="h-4 w-1/2 bg-white/10" />
      </div>
    </Card>
  );
}

function EmptyState({ isAdmin }: { isAdmin: boolean }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="relative mb-8">
        <div className="w-24 h-24 rounded-full bg-gradient-to-br from-ai-violet-500/20 to-electric-blue-500/20 border border-ai-violet-500/30 flex items-center justify-center backdrop-blur-sm">
          <LayoutDashboard className="h-12 w-12 text-ai-violet-400" />
        </div>
        <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-br from-ai-violet-600 to-electric-blue-600 rounded-full flex items-center justify-center">
          <Brain className="h-4 w-4 text-white" />
        </div>
      </div>
      <h3 className="text-3xl font-bold mb-4 tracking-tight bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
        No boards yet
      </h3>
      <p className="text-muted-foreground mb-8 max-w-md text-lg leading-relaxed">
        {isAdmin
          ? "Get started by creating your first AI-powered board to organize your team's work and boost productivity."
          : "No boards have been shared with you yet. Contact your admin to get access to boards."}
      </p>
      {isAdmin && <CreateBoardDialog />}
    </div>
  );
}

function StatsCard({ title, value, icon: Icon, trend, aiPowered }: { 
  title: string; 
  value: string | number; 
  icon: any; 
  trend?: string;
  aiPowered?: boolean;
}) {
  return (
    <Card className="card-glow group">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <p className="text-sm font-medium text-muted-foreground tracking-tight">{title}</p>
              {aiPowered && (
                <Zap className="h-3 w-3 text-ai-violet-400 animate-pulse" />
              )}
            </div>
            <p className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
              {value}
            </p>
            {trend && (
              <p className="text-xs text-green-400 flex items-center mt-2">
                <TrendingUp className="h-3 w-3 mr-1" />
                {trend}
              </p>
            )}
          </div>
          <div className="relative">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-ai-violet-500/20 to-electric-blue-500/20 border border-ai-violet-500/30 flex items-center justify-center backdrop-blur-sm group-hover:scale-110 transition-transform duration-300">
              <Icon className="h-7 w-7 text-ai-violet-400" />
            </div>
            {aiPowered && (
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-ai-violet-500 rounded-full animate-pulse" />
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function BoardsPage() {
  const { data: user } = useCurrentUser();
  const { data: boards, isLoading, error } = useBoards();

  const isAdmin = user?.role === 'admin';

  if (isLoading) {
    return (
      <div className="space-y-8 p-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-10 w-40 mb-3 bg-white/10" />
            <Skeleton className="h-6 w-80 bg-white/10" />
          </div>
          <Skeleton className="h-12 w-40 bg-white/10" />
        </div>
        
        {/* Stats skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="card-premium">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <Skeleton className="h-4 w-24 mb-2 bg-white/10" />
                    <Skeleton className="h-8 w-16 bg-white/10" />
                  </div>
                  <Skeleton className="h-14 w-14 rounded-xl bg-white/10" />
                </div>
              </CardContent>
            </Card>
          ))}
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
      <div className="flex flex-col items-center justify-center py-20 text-center p-6">
        <div className="w-24 h-24 rounded-full bg-red-500/20 border border-red-500/30 flex items-center justify-center backdrop-blur-sm mb-6">
          <LayoutDashboard className="h-12 w-12 text-red-400" />
        </div>
        <h3 className="text-3xl font-bold mb-4 tracking-tight text-red-400">Failed to load boards</h3>
        <p className="text-muted-foreground text-lg">
          There was an error loading your boards. Please try again.
        </p>
      </div>
    );
  }

  const totalBoards = boards?.length || 0;

  return (
    <div className="space-y-8 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-5xl font-bold tracking-tight bg-gradient-to-r from-white via-white/90 to-white/70 bg-clip-text text-transparent mb-3">
            Boards
          </h1>
          <p className="text-muted-foreground text-xl leading-relaxed">
            Manage your AI-powered project boards and track progress
          </p>
        </div>
        {isAdmin && boards && boards.length > 0 && <CreateBoardDialog />}
      </div>

      {/* Stats */}
      {boards && boards.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatsCard
            title="Total Boards"
            value={totalBoards}
            icon={LayoutDashboard}
            aiPowered={true}
          />
          <StatsCard
            title="Team Members"
            value="8"
            icon={Users}
          />
          <StatsCard
            title="AI Insights"
            value="24"
            icon={Brain}
            trend="+12 this week"
            aiPowered={true}
          />
        </div>
      )}

      {/* Content */}
      {!boards || boards.length === 0 ? (
        <EmptyState isAdmin={isAdmin} />
      ) : (
        <div>
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-2xl font-semibold tracking-tight bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
              Your Boards
            </h2>
            <Badge className="bg-ai-violet-500/20 text-ai-violet-300 border border-ai-violet-500/30 px-3 py-1 text-sm font-medium">
              {totalBoards} {totalBoards === 1 ? 'board' : 'boards'}
            </Badge>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {boards.map((board, index) => (
              <div
                key={board.id}
                className="animate-fade-in"
                style={{
                  animationDelay: `${index * 100}ms`,
                  animationFillMode: 'forwards'
                }}
              >
                <BoardCard board={board} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}