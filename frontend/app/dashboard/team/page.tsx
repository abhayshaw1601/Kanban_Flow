'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { UserPlus, Users, Shield, User, BarChart3, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { toast } from 'sonner';
import { useCurrentUser } from '@/hooks/use-current-user';
import { useUsers } from '@/hooks/use-users';
import { useBoards } from '@/hooks/use-boards';
import { useAddBoardMember } from '@/hooks/use-board-members';
import { useTeamOverview } from '@/hooks/use-analytics';
import { MemberStatsModal } from '@/components/team/member-stats-modal';

export default function TeamPage() {
  const router = useRouter();
  const { data: currentUser, isLoading: userLoading } = useCurrentUser();
  const { data: users = [], isLoading: usersLoading } = useUsers();
  const { data: boards = [] } = useBoards();
  const { data: teamOverview } = useTeamOverview();
  const addBoardMember = useAddBoardMember();

  const [selectedUser, setSelectedUser] = useState<string>('');
  const [selectedBoard, setSelectedBoard] = useState<string>('');
  const [selectedMemberId, setSelectedMemberId] = useState<number | null>(null);
  const [selectedMemberName, setSelectedMemberName] = useState<string>('');
  const [isStatsModalOpen, setIsStatsModalOpen] = useState(false);

  // Redirect non-admin users
  useEffect(() => {
    if (!userLoading && currentUser && currentUser.role !== 'admin') {
      router.push('/dashboard');
      toast.error('Access denied. Admin privileges required.');
    }
  }, [currentUser, userLoading, router]);

  // Don't render anything while checking user role
  if (userLoading || (currentUser && currentUser.role !== 'admin')) {
    return null;
  }

  const handleAddMember = async () => {
    if (!selectedUser || !selectedBoard) {
      toast.error('Please select both a user and a board');
      return;
    }

    try {
      await addBoardMember.mutateAsync({
        userId: parseInt(selectedUser),
        boardId: parseInt(selectedBoard),
      });

      toast.success('User added to board successfully');
      setSelectedUser('');
      setSelectedBoard('');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to add user to board';
      toast.error(errorMessage);
    }
  };

  const handleMemberClick = (userId: number, userName: string) => {
    setSelectedMemberId(userId);
    setSelectedMemberName(userName);
    setIsStatsModalOpen(true);
  };

  const getPerformanceIndicator = (userId: number) => {
    const memberStats = teamOverview?.team_members.find(m => m.user_id === userId);
    if (!memberStats || memberStats.total_tasks === 0) {
      return null;
    }

    const { performance_color, completion_percentage } = memberStats;
    
    const indicators = {
      green: { icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-100' },
      yellow: { icon: Clock, color: 'text-yellow-600', bg: 'bg-yellow-100' },
      red: { icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-100' }
    };

    const indicator = indicators[performance_color];
    const Icon = indicator.icon;

    return (
      <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${indicator.bg}`}>
        <Icon className={`w-3 h-3 ${indicator.color}`} />
        <span className={`text-xs font-medium ${indicator.color}`}>
          {completion_percentage}%
        </span>
      </div>
    );
  };

  const getRoleIcon = (role: string) => {
    return role === 'admin' ? (
      <Shield className="w-4 h-4 text-blue-600" />
    ) : (
      <User className="w-4 h-4 text-gray-600" />
    );
  };

  const getRoleBadge = (role: string) => {
    return role === 'admin' ? (
      <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
        Admin
      </Badge>
    ) : (
      <Badge variant="secondary">Employee</Badge>
    );
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(word => word.charAt(0))
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  if (usersLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading team members...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            Team Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage users and board memberships
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
          <Users className="w-4 h-4" />
          <span>{users.length} team members</span>
        </div>
      </div>

      {/* Add Member to Board */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UserPlus className="w-5 h-5" />
            Add User to Board
          </CardTitle>
          <CardDescription>
            Assign users to specific boards to give them access
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">Select User</label>
              <Select value={selectedUser} onValueChange={setSelectedUser}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a user" />
                </SelectTrigger>
                <SelectContent>
                  {users.map((user) => (
                    <SelectItem key={user.id} value={user.id.toString()}>
                      <div className="flex items-center gap-2">
                        <Avatar className="w-6 h-6">
                          <AvatarFallback className="text-xs">
                            {getInitials(user.name)}
                          </AvatarFallback>
                        </Avatar>
                        <span>{user.name}</span>
                        {getRoleIcon(user.role)}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex-1">
              <label className="text-sm font-medium mb-2 block">Select Board</label>
              <Select value={selectedBoard} onValueChange={setSelectedBoard}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a board" />
                </SelectTrigger>
                <SelectContent>
                  {boards.map((board) => (
                    <SelectItem key={board.id} value={board.id.toString()}>
                      {board.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleAddMember}
              disabled={!selectedUser || !selectedBoard || addBoardMember.isPending}
            >
              {addBoardMember.isPending ? 'Adding...' : 'Add to Board'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Team Members List */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {users.map((user) => (
          <Card 
            key={user.id} 
            className="cursor-pointer hover:shadow-md transition-shadow"
            onClick={() => handleMemberClick(user.id, user.name)}
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="relative">
                    <Avatar className="w-12 h-12">
                      <AvatarFallback className="text-lg bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400">
                        {getInitials(user.name)}
                      </AvatarFallback>
                    </Avatar>
                    {/* Performance Indicator */}
                    {getPerformanceIndicator(user.id) && (
                      <div className="absolute -top-1 -right-1">
                        {getPerformanceIndicator(user.id)}
                      </div>
                    )}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                      {user.name}
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {user.email}
                    </p>
                  </div>
                </div>
                <div className="flex flex-col items-end gap-2">
                  {getRoleBadge(user.role)}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 px-2 text-xs"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleMemberClick(user.id, user.name);
                    }}
                  >
                    <BarChart3 className="w-3 h-3 mr-1" />
                    Stats
                  </Button>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                  Member since {new Date(user.created_at).toLocaleDateString()}
                </p>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <Users className="w-4 h-4" />
                    <span>Board member</span>
                  </div>
                  {teamOverview?.team_members.find(m => m.user_id === user.id)?.total_tasks && (
                    <div className="text-xs text-gray-500">
                      {teamOverview.team_members.find(m => m.user_id === user.id)?.total_tasks} tasks
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {users.length === 0 && (
        <Card>
          <CardContent className="p-12 text-center">
            <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              No team members found
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Users will appear here once they register for the application.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Member Statistics Modal */}
      <MemberStatsModal
        userId={selectedMemberId}
        userName={selectedMemberName}
        isOpen={isStatsModalOpen}
        onClose={() => {
          setIsStatsModalOpen(false);
          setSelectedMemberId(null);
          setSelectedMemberName('');
        }}
      />
    </div>
  );
}