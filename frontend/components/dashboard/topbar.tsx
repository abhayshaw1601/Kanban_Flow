'use client';

import { Menu, Moon, Sun, LogOut, AlertTriangle, ClipboardList } from 'lucide-react';
import { useTheme } from 'next-themes';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { apiClient } from '@/lib/api';
import { toast } from 'sonner';
import { useRouter } from 'next/navigation';
import { useBlockerNotifications } from '@/hooks/use-blocker-notifications';
import { useAssignedTasks } from '@/hooks/use-assigned-tasks';
import { useCurrentUser } from '@/hooks/use-current-user';
import { AssignedTasksModal } from '@/components/tasks/assigned-tasks-modal';
import { BlockedTasksModal } from '@/components/tasks/blocked-tasks-modal';
import { useState } from 'react';

interface TopBarProps {
  userName: string;
  userEmail: string;
  userAvatar: string | null;
  onMenuClick: () => void;
}

export function TopBar({ userName, userEmail, userAvatar, onMenuClick }: TopBarProps) {
  const { theme, setTheme } = useTheme();
  const router = useRouter();
  const { data: currentUser } = useCurrentUser();
  const { totalBlocked, blockedTasks } = useBlockerNotifications();
  const { data: assignedTasksData } = useAssignedTasks();
  const [showBlockerDropdown, setShowBlockerDropdown] = useState(false);
  const [showAssignedTasksModal, setShowAssignedTasksModal] = useState(false);
  const [showBlockedTasksModal, setShowBlockedTasksModal] = useState(false);

  // Only show indicators for non-admin users
  const shouldShowIndicators = currentUser && currentUser.role !== 'admin';
  const shouldShowBlockerIndicator = shouldShowIndicators && totalBlocked > 0;

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const handleLogout = async () => {
    try {
      await apiClient.post('/api/auth/logout');
      toast.success('Logged out successfully');
      router.push('/login');
    } catch (error) {
      toast.error('Failed to logout');
      console.error('Logout error:', error);
    }
  };

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const handleViewAllBlockedTasks = () => {
    setShowBlockedTasksModal(true);
    setShowBlockerDropdown(false);
  };

  const handleViewSpecificTask = async (taskId: number, boardName: string) => {
    try {
      // Get all boards to find the one containing this task
      const response = await fetch('/api/boards', {
        credentials: 'include'
      });
      if (response.ok) {
        const boards = await response.json();
        const board = boards.find((b: any) => b.name === boardName);
        if (board) {
          router.push(`/dashboard/boards/${board.id}`);
          toast.success(`Navigating to ${boardName} board`);
        } else {
          router.push('/dashboard/boards');
          toast.info('Navigating to boards page');
        }
      } else {
        router.push('/dashboard/boards');
      }
    } catch (error) {
      console.error('Error finding board:', error);
      router.push('/dashboard/boards');
    }
    setShowBlockerDropdown(false);
  };

  return (
    <>
      <header className="sticky top-0 z-30 w-full glass-nav border-b border-white/10">
        <div className="flex h-16 items-center px-6 gap-4">
          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden hover:bg-white/10 transition-colors duration-200"
            onClick={onMenuClick}
          >
            <Menu className="h-5 w-5" />
          </Button>

          {/* Spacer */}
          <div className="flex-1" />

          {/* View Assigned Tasks Button */}
          {shouldShowIndicators && (
            <Button
              variant="ghost"
              onClick={() => setShowAssignedTasksModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-electric-blue-500/20 border border-electric-blue-500/30 rounded-xl hover:bg-electric-blue-500/30 transition-all duration-300 backdrop-blur-sm"
              title="View all your assigned tasks"
            >
              <ClipboardList className="h-4 w-4 text-electric-blue-400" />
              <span className="text-sm font-medium text-electric-blue-300 tracking-tight">
                My Tasks
              </span>
              {assignedTasksData && (
                <Badge className="bg-electric-blue-600 text-white text-xs px-2 py-1 rounded-full">
                  {assignedTasksData.statistics.total_tasks}
                </Badge>
              )}
            </Button>
          )}

          {/* Blocker notification indicator with dropdown */}
          {shouldShowBlockerIndicator && (
            <DropdownMenu open={showBlockerDropdown} onOpenChange={setShowBlockerDropdown}>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="flex items-center gap-2 px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-xl hover:bg-red-500/30 transition-all duration-300 backdrop-blur-sm animate-pulse"
                  title="Click to view your blocked tasks"
                >
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                  <span className="text-sm font-medium text-red-300 tracking-tight">
                    {totalBlocked} Blocked Task{totalBlocked > 1 ? 's' : ''}
                  </span>
                  <Badge className="bg-red-600 text-white text-xs px-2 py-1 rounded-full">
                    {totalBlocked}
                  </Badge>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-80 modal-glass border border-white/20 rounded-xl" align="end" forceMount>
                <DropdownMenuLabel className="font-normal p-4">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-semibold leading-none text-red-400 tracking-tight">
                      🚨 Blocked Tasks ({totalBlocked})
                    </p>
                    <p className="text-xs leading-none text-red-400/80">
                      These tasks need immediate attention
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator className="bg-white/10" />
                
                {/* Show first 3 blocked tasks */}
                {blockedTasks.slice(0, 3).map((task) => (
                  <DropdownMenuItem
                    key={task.task_id}
                    onClick={() => handleViewSpecificTask(task.task_id, task.board_name)}
                    className="cursor-pointer flex-col items-start p-4 h-auto hover:bg-white/5 transition-colors duration-200"
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className="font-medium text-sm truncate flex-1 text-foreground">
                        {task.title}
                      </span>
                      {task.is_overdue && (
                        <Badge className="bg-red-500/20 text-red-400 text-xs ml-2 border border-red-500/30">
                          OVERDUE
                        </Badge>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {task.board_name} • {task.column_name}
                    </div>
                    {task.blocker_reason && (
                      <div className="text-xs text-red-400 mt-1">
                        {task.blocker_reason}
                      </div>
                    )}
                  </DropdownMenuItem>
                ))}
                
                {blockedTasks.length > 3 && (
                  <>
                    <DropdownMenuSeparator className="bg-white/10" />
                    <DropdownMenuItem
                      onClick={handleViewAllBlockedTasks}
                      className="cursor-pointer text-center justify-center text-red-400 font-medium hover:bg-white/5 transition-colors duration-200"
                    >
                      View All {totalBlocked} Blocked Tasks →
                    </DropdownMenuItem>
                  </>
                )}
                
                {blockedTasks.length <= 3 && (
                  <>
                    <DropdownMenuSeparator className="bg-white/10" />
                    <DropdownMenuItem
                      onClick={handleViewAllBlockedTasks}
                      className="cursor-pointer text-center justify-center text-red-400 font-medium hover:bg-white/5 transition-colors duration-200"
                    >
                      View All Blocked Tasks →
                    </DropdownMenuItem>
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          )}

          {/* Dark mode toggle - hidden since we're dark mode first */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="hover:bg-white/10 transition-colors duration-200 opacity-50"
            title="Theme toggle (Dark mode optimized)"
          >
            <Moon className="h-5 w-5 text-ai-violet-400" />
            <span className="sr-only">Toggle theme</span>
          </Button>

          {/* User menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full hover:bg-white/10 transition-colors duration-200">
                <Avatar className="h-10 w-10 ring-2 ring-ai-violet-500/30 hover:ring-ai-violet-500/50 transition-all duration-300">
                  <AvatarImage src={userAvatar || undefined} alt={userName} />
                  <AvatarFallback className="bg-gradient-to-br from-ai-violet-600 to-electric-blue-600 text-white font-semibold">
                    {getInitials(userName)}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56 modal-glass border border-white/20 rounded-xl" align="end" forceMount>
              <DropdownMenuLabel className="font-normal p-4">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-semibold leading-none text-foreground tracking-tight">{userName}</p>
                  <p className="text-xs leading-none text-muted-foreground">
                    {userEmail}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator className="bg-white/10" />
              <DropdownMenuItem onClick={handleLogout} className="cursor-pointer hover:bg-white/5 transition-colors duration-200 m-2 rounded-lg">
                <LogOut className="mr-2 h-4 w-4" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      {/* Assigned Tasks Modal */}
      <AssignedTasksModal
        isOpen={showAssignedTasksModal}
        onClose={() => setShowAssignedTasksModal(false)}
      />

      {/* Blocked Tasks Modal */}
      <BlockedTasksModal
        isOpen={showBlockedTasksModal}
        onClose={() => setShowBlockedTasksModal(false)}
      />
    </>
  );
}
