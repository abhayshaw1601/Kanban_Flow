'use client';

import { useState, useEffect } from 'react';
import { useCurrentUser } from '@/hooks/use-current-user';
import { Sidebar } from '@/components/dashboard/sidebar';
import { TopBar } from '@/components/dashboard/topbar';
import { NotificationProvider } from '@/components/providers/notification-provider';
import { useRouter } from 'next/navigation';
import { Loading } from '@/components/ui/loading';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { data: user, isLoading, error } = useCurrentUser();
  const router = useRouter();

  // Force dark mode for premium AI SaaS theme
  useEffect(() => {
    document.documentElement.classList.add('dark');
  }, []);

  // Handle loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="text-center">
          <div className="relative mb-6">
            <div className="w-16 h-16 border-4 border-ai-violet-500/20 border-t-ai-violet-500 rounded-full animate-spin mx-auto" />
            <div className="absolute inset-0 w-16 h-16 border-4 border-transparent border-t-electric-blue-500 rounded-full animate-spin mx-auto" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }} />
          </div>
          <p className="text-muted-foreground font-medium">Loading your workspace...</p>
          <div className="mt-2 flex items-center justify-center gap-1">
            <div className="w-2 h-2 bg-ai-violet-500 rounded-full animate-pulse" />
            <div className="w-2 h-2 bg-electric-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
            <div className="w-2 h-2 bg-ai-violet-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
          </div>
        </div>
      </div>
    );
  }

  // Handle error state (user not authenticated)
  if (error || !user) {
    router.push('/login');
    return null;
  }

  const isAdmin = user.role === 'admin';

  return (
    <NotificationProvider>
      <div className="flex h-screen overflow-hidden bg-background">
        {/* Animated background */}
        <div className="fixed inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-ai-violet-500/5 rounded-full blur-3xl animate-pulse" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-electric-blue-500/5 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-ai-violet-500/3 to-electric-blue-500/3 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }} />
        </div>

        {/* Sidebar */}
        <Sidebar
          isAdmin={isAdmin}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        {/* Main content */}
        <div className="flex flex-col flex-1 overflow-hidden relative z-10">
          {/* TopBar */}
          <TopBar
            userName={user.name}
            userEmail={user.email}
            userAvatar={user.avatar}
            onMenuClick={() => setSidebarOpen(true)}
          />

          {/* Page content */}
          <main className="flex-1 overflow-y-auto">
            <div className="min-h-full">
              {children}
            </div>
          </main>
        </div>
      </div>
    </NotificationProvider>
  );
}
