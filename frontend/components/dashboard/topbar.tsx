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
      <header className="sticky top-0 z-30 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-16 items-center px-4 gap-4">
          {/* Mobile menu button */}
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
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
              className="flex items-center gap-2 px-3 py-1 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-full hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors cursor-pointer"
              title="View all your assigned tasks"
            >
              <ClipboardList className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                My Tasks
              </span>
              {assignedTasksData && (
                <Badge className="bg-blue-600 text-white text-xs px-1.5 py-0.5">
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
                  className="flex items-center gap-2 px-3 py-1 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-full hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors cursor-pointer"
                  title="Click to view your blocked tasks"
                >
                  <AlertTriangle className="h-4 w-4 text-red-600 dark:text-red-400" />
                  <span className="text-sm font-medium text-red-700 dark:text-red-300">
                    {totalBlocked} Blocked Task{totalBlocked > 1 ? 's' : ''}
                  </span>
                  <Badge className="bg-red-600 text-white text-xs px-1.5 py-0.5">
                    {totalBlocked}
                  </Badge>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-80" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none text-red-700 dark:text-red-300">
                      🚨 Blocked Tasks ({totalBlocked})
                    </p>
                    <p className="text-xs leading-none text-red-600 dark:text-red-400">
                      These tasks need immediate attention
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                
                {/* Show first 3 blocked tasks */}
                {blockedTasks.slice(0, 3).map((task) => (
                  <DropdownMenuItem
                    key={task.task_id}
                    onClick={() => handleViewSpecificTask(task.task_id, task.board_name)}
                    className="cursor-pointer flex-col items-start p-3 h-auto"
                  >
                    <div className="flex items-center justify-between w-full">
                      <span className="font-medium text-sm truncate flex-1">
                        {task.title}
                      </span>
                      {task.is_overdue && (
                        <Badge className="bg-red-100 text-red-800 text-xs ml-2">
                          OVERDUE
                        </Badge>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {task.board_name} • {task.column_name}
                    </div>
                    {task.blocker_reason && (
                      <div className="text-xs text-red-600 dark:text-red-400 mt-1">
                        {task.blocker_reason}
                      </div>
                    )}
                  </DropdownMenuItem>
                ))}
                
                {blockedTasks.length > 3 && (
                  <>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      onClick={handleViewAllBlockedTasks}
                      className="cursor-pointer text-center justify-center text-red-600 dark:text-red-400 font-medium"
                    >
                      View All {totalBlocked} Blocked Tasks →
                    </DropdownMenuItem>
                  </>
                )}
                
                {blockedTasks.length <= 3 && (
                  <>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      onClick={handleViewAllBlockedTasks}
                      className="cursor-pointer text-center justify-center text-red-600 dark:text-red-400 font-medium"
                    >
                      View All Blocked Tasks →
                    </DropdownMenuItem>
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          )}

          {/* Dark mode toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
            <span className="sr-only">Toggle theme</span>
          </Button>

          {/* User menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                <Avatar className="h-10 w-10">
                  <AvatarImage src={userAvatar || undefined} alt={userName} />
                  <AvatarFallback className="bg-primary text-primary-foreground">
                    {getInitials(userName)}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">{userName}</p>
                  <p className="text-xs leading-none text-muted-foreground">
                    {userEmail}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} className="cursor-pointer">
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
